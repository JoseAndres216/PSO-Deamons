#!/usr/bin/env python3
import os
import sys
import time
import atexit
import subprocess
import re
from signal import SIGTERM

import highTemperatureNotifier

TEMP_PATH = "/sys/class/thermal/thermal_zone0/temp"

'''
Daemon class to periodically fetch CPU temperature and log it to a file.
Supports start, stop, and restart operations.
'''
class TemperatureDaemon:

    '''
    Initialize daemon with PID file and log file path.
    '''
    def __init__(self, pidFile):
        self.pidFile = pidFile
        self.temperatureLogRoute = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TemperatureLog.txt")

    '''
    Perform UNIX double-fork magic to daemonize the process.
    Redirect standard file descriptors to /dev/null.
    Write the daemon PID to the pidFile.
    '''
    def daemonize(self):
        if os.fork():
            sys.exit()
        os.chdir("/")
        os.setsid()
        os.umask(0)

        if os.fork():
            sys.exit()

        sys.stdout.flush()
        sys.stderr.flush()
        with open('/dev/null', 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())

        atexit.register(self.delete_pid)
        pid = str(os.getpid())
        with open(self.pidFile, 'w') as f:
            f.write(f"{pid}\n")

    '''
    Remove the PID file when the daemon exits.
    '''
    def delete_pid(self):
        if os.path.exists(self.pidFile):
            os.remove(self.pidFile)

    '''
    Start the daemon if it is not already running.
    '''
    def start(self):
        try:
            with open(self.pidFile, 'r') as f:
                pid = int(f.read().strip())
        except IOError:
            pid = None

        if pid:
            print("Daemon is already running.")
            sys.exit(1)

        self.daemonize()
        self.run()

    '''
    Stop the daemon if it is running by killing its PID.
    '''
    def stop(self):
        try:
            with open(self.pidFile, 'r') as f:
                pid = int(f.read().strip())
        except IOError:
            pid = None

        if not pid:
            print("Daemon is not running.")
            return

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError:
            self.delete_pid()

    '''
    Restart the daemon by stopping and then starting it.
    '''
    def restart(self):
        self.stop()
        self.start()


    '''
    
    '''
    def notifyIfHighTemperature(self, registeredTemperature):
        highTemperatureFlagFileRoute = os.path.join(os.path.dirname(__file__), "HighTemperatureFlag.txt")
        valor = "1" if registeredTemperature >= 80.0 else "0"
        with open(highTemperatureFlagFileRoute, "w") as f:
            f.write(valor)

        return

    '''
    Execute 'sensors' command and parse its output to extract the temperature
    for 'Package id 0' from 'coretemp-isa-0000'.
    Returns the temperature as a float or None if unavailable.
    '''
    def getTemperature(self):
        try:
            output = subprocess.check_output(['sensors'], text=True)
            blocks = output.split("\n\n")
            for block in blocks:
                if block.startswith("coretemp-isa-0000"):
                    for line in block.splitlines():
                        if line.strip().startswith("Package id 0:"):
                            match = re.search(r"\+([0-9]+\.[0-9])°C", line)
                            if match:
                                tempStr = match.group(1)
                                return float(tempStr)
            return None
        except Exception:
            return None

    '''
    Main loop of the daemon: fetch temperature every 5 seconds and
    append the reading with timestamp to the log file.
    '''
    def run(self):
        while True:
            temperature = self.getTemperature()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            if temperature is not None:
                self.notifyIfHighTemperature(temperature)
                with open(self.temperatureLogRoute, "a") as log:
                    log.write(f"{timestamp} - Temperature registered: {temperature:.1f}°C\n")
            else:
                with open(self.temperatureLogRoute, "a") as log:
                    log.write(f"{timestamp} - Temperature registered: Not available\n")
            time.sleep(5)

if __name__ == "__main__":
    daemon = TemperatureDaemon("/tmp/temperatureDaemon.pid")

    if len(sys.argv) != 2:
        print("Usage: python temperatureDaemon.py start|stop|restart")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'start':
        daemon.start()
    elif command == 'stop':
        daemon.stop()
    elif command == 'restart':
        daemon.restart()
    else:
        print("Unknown command")
        sys.exit(1)

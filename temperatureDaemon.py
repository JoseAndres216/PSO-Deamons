#!/usr/bin/env python3
import os
import sys
import time
import atexit
from signal import SIGTERM

TEMP_PATH = "/sys/class/thermal/thermal_zone0/temp"

class TemperatureDaemon:
    def __init__(self, pidFile):
        self.pidFile = pidFile
        # Ruta al archivo de log en el mismo directorio que este script
        self.logPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TemperatureLog.txt")

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

        atexit.register(self.deletePid)
        pid = str(os.getpid())
        with open(self.pidFile, 'w') as f:
            f.write(f"{pid}\n")

    def deletePid(self):
        if os.path.exists(self.pidFile):
            os.remove(self.pidFile)

    def start(self):
        try:
            with open(self.pidFile, 'r') as f:
                pid = int(f.read().strip())
        except IOError:
            pid = None

        if pid:
            print("Daemon ya está corriendo.")
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        try:
            with open(self.pidFile, 'r') as f:
                pid = int(f.read().strip())
        except IOError:
            pid = None

        if not pid:
            print("Daemon no está corriendo.")
            return

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError:
            self.deletePid()

    def restart(self):
        self.stop()
        self.start()

    def getTemperature(self):
        try:
            with open(TEMP_PATH, 'r') as f:
                tempStr = f.read().strip()
                tempCelsius = int(tempStr) / 1000.0
                return tempCelsius
        except FileNotFoundError:
            return None

    def run(self):
        while True:
            temperature = self.getTemperature()
            if temperature is not None:
                with open(self.logPath, "a") as log:
                    log.write(f"Temperature registered: {temperature:.1f}°C\n")
            else:
                with open(self.logPath, "a") as log:
                    log.write("Temperature registered: not available\n")
            time.sleep(5)

if __name__ == "__main__":
    daemon = TemperatureDaemon("/tmp/temperatureDaemon.pid")

    if len(sys.argv) != 2:
        print("Uso: python temperatureDaemon.py start|stop|restart")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'start':
        daemon.start()
    elif command == 'stop':
        daemon.stop()
    elif command == 'restart':
        daemon.restart()
    else:
        print("Comando desconocido")
        sys.exit(1)

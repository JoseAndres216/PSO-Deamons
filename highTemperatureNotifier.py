#!/usr/bin/env python3
import os
import time
import subprocess

HIGHTEMPERATUREFLAGROUTE = os.path.join(os.path.dirname(__file__), "HighTemperatureFlag.txt")

'''
Function to notify the user about high CPU temperature.
'''
def notifyHighTemperature():
    try:
        subprocess.run(["notify-send", "Warning: High temperature ⚠️", "CPU temperature is 80°C or higher."])
    except Exception as e:
        print("Notification error:", e)

'''
Main function to check the temperature flag and notify if high temperature is detected.
'''
def main():
    alreadyNotified = False

    while True:
        if os.path.exists(HIGHTEMPERATUREFLAGROUTE):
            with open(HIGHTEMPERATUREFLAGROUTE, "r") as f:
                flag = f.read().strip()

            if flag == "1" and not alreadyNotified:
                notifyHighTemperature()
                alreadyNotified = True
            elif flag == "0":
                alreadyNotified = False

        time.sleep(5)

if __name__ == "__main__":
    main()

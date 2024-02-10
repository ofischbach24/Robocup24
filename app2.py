#!/usr/bin/env python3
import subprocess
from colorama import Fore
from motorlib import board,motor
import RPi.GPIO as GPIO
from evdev import InputDevice, categorize, ecodes

# Function to get information about connected game controllers using xinput
def get_gamepad_info():
    try:
        result = subprocess.run(['xinput', 'list'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running xinput: {e}")
        return None

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup Boards
# io1 = board(0x18)
pi = board('pi', type="pi")

# Setup Motors
RightTread = motor(pi, pins=[1, 11])
LeftTread = motor(pi, pins=[2, 12])

# Setup Power Variables
powerDrive = 1

# Define deadzone threshold
DEADZONE_THRESHOLD = 0.2

def apply_deadzone(value, threshold):
    return 0 if abs(value) < threshold else value

def Shutdown(message):
    if message:
        # Sets all motors to 0
        RightTread.start(0)
        LeftTread.start(0)

        print(Fore.RED + 'Shutdown' + Fore.RESET)

# Example usage of get_gamepad_info
gamepad_info = get_gamepad_info()
if gamepad_info:
    print("Gamepad Information:")
    print(gamepad_info)

# Path to the event file for the gamepad, adjust as needed
gamepad_path = "/dev/input/eventX"
gamepad = InputDevice(gamepad_path)

for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:
        if event.code == ecodes.ABS_Y:
            joystick1_value = event.value / 32767.0
            joystick1_value = apply_deadzone(joystick1_value, DEADZONE_THRESHOLD)
            LeftTread.start(int(joystick1_value * 100 * powerDrive))

        elif event.code == ecodes.ABS_RX:
            joystick2_value = event.value / 32767.0
            joystick2_value = apply_deadzone(joystick2_value, DEADZONE_THRESHOLD)
            RightTread.start(int(joystick2_value * 100 * powerDrive))

    elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_START:
        shutdown_value = event.value
        Shutdown(shutdown_value)

#!/usr/bin/python3
import sys

import pigpio
import time
import os
from evdev import InputDevice, ecodes

# Pin Definitions
PIN_ENABLE_LEFT = 24
PIN_ENABLE_RIGHT = 4
PIN_BACKWARD_LEFT = 25
PIN_BACKWARD_RIGHT = 17
PIN_FORWARD_LEFT = 23
PIN_FORWARD_RIGHT = 22
PIN_YAW = 13
PIN_PITCH = 18

AXIS_LEFT_RIGHT = 0
AXIS_UP_DOWN = 1
AXIS_CAMERA_UP_DOWN = 2
AXIS_CAMERA_LEFT_RIGHT = 3

def forward(pi):
    pi.write(PIN_FORWARD_LEFT, 1)
    pi.write(PIN_FORWARD_RIGHT, 1)
    pi.write(PIN_BACKWARD_LEFT, 0)
    pi.write(PIN_BACKWARD_RIGHT, 0)

def backward(pi):
    pi.write(PIN_FORWARD_LEFT, 0)
    pi.write(PIN_FORWARD_RIGHT, 0)
    pi.write(PIN_BACKWARD_LEFT, 1)
    pi.write(PIN_BACKWARD_RIGHT, 1)

def left(pi):
    pi.write(PIN_FORWARD_LEFT, 0)
    pi.write(PIN_FORWARD_RIGHT, 1)
    pi.write(PIN_BACKWARD_LEFT, 1)
    pi.write(PIN_BACKWARD_RIGHT, 0)

def right(pi):
    pi.write(PIN_FORWARD_LEFT, 1)
    pi.write(PIN_FORWARD_RIGHT, 0)
    pi.write(PIN_BACKWARD_LEFT, 0)
    pi.write(PIN_BACKWARD_RIGHT, 1)

def stop(pi):
    pi.write(PIN_FORWARD_LEFT, 0)
    pi.write(PIN_FORWARD_RIGHT, 0)
    pi.write(PIN_BACKWARD_LEFT, 0)
    pi.write(PIN_BACKWARD_RIGHT, 0)

# centers camera
def center_camera(pi):
    pi.set_servo_pulsewidth(PIN_YAW, 1500)
    pi.set_servo_pulsewidth(PIN_PITCH, 1500)

# converts mouse percentage into servo pulsewidths to move camera
def move_camera(pi, x_perc, y_perc):
    yaw = int(1000 + (x_perc / 100) * 1000)
    pitch = int(1000 + (y_perc / 100) * 1000)
    pi.set_servo_pulsewidth(PIN_YAW, yaw)
    pi.set_servo_pulsewidth(PIN_PITCH, pitch)


def handle_command_loop(pi):
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break  # EOF

            # takes command and makes it useful to us
            parts = line.strip().split()
            if len(parts) != 3:
                continue  # Skip malformed input

            key, x_str, y_str = parts

            try:
                x = float(x_str)
                y = float(y_str)
            except ValueError:
                continue  # Skip bad values

            key = key.upper()

            # Movement keys
            if key == 'W':
                forward(pi)
                time.sleep(0.15)
                stop(pi)
            elif key == 'S':
                backward(pi)
                time.sleep(0.15)
                stop(pi)
            elif key == 'A':
                left(pi)
                time.sleep(0.15)
                stop(pi)
            elif key == 'D':
                right(pi)
                time.sleep(0.15)
                stop(pi)
            else:
                stop(pi)

            # Camera control via mouse % position
            move_camera(pi, x, y)

    except KeyboardInterrupt:
        pass
    finally:
        stop(pi)
        print("Exiting command loop")

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Can't start pigpio")
    exit(1)

addon_board = os.getenv("ADDONBOARD")
if addon_board == "0":
    pi.set_mode(PIN_ENABLE_LEFT, pigpio.OUTPUT)
    pi.set_mode(PIN_ENABLE_RIGHT, pigpio.OUTPUT)
    pi.write(PIN_ENABLE_LEFT, 1)
    pi.write(PIN_ENABLE_RIGHT, 1)

# Set pin modes
for pin in [PIN_BACKWARD_LEFT, PIN_BACKWARD_RIGHT, PIN_FORWARD_LEFT, PIN_FORWARD_RIGHT, PIN_YAW, PIN_PITCH]:
    pi.set_mode(pin, pigpio.OUTPUT)

# center camera
center_camera(pi)

# starts command loop
handle_command_loop(pi)

# Cleanup
center_camera(pi)
pi.set_servo_pulsewidth(PIN_YAW, 0)
pi.set_servo_pulsewidth(PIN_PITCH, 0)
if addon_board == "0":
    pi.write(PIN_ENABLE_LEFT, 0)
    pi.write(PIN_ENABLE_RIGHT, 0)
pi.stop()

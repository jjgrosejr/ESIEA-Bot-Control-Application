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

def camera_left(pi): pi.set_servo_pulsewidth(PIN_YAW, 750)
def camera_right(pi): pi.set_servo_pulsewidth(PIN_YAW, 2250)
def camera_up(pi): pi.set_servo_pulsewidth(PIN_PITCH, 750)
def camera_down(pi): pi.set_servo_pulsewidth(PIN_PITCH, 2200)
def center_camera(pi): 
    pi.set_servo_pulsewidth(PIN_YAW, 1500)
    pi.set_servo_pulsewidth(PIN_PITCH, 1500)

def dance(pi):
    left(pi)
    time.sleep(1)
    right(pi)
    time.sleep(1)
    stop(pi)

def handle_command_loop(pi):
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break  # EOF

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
            elif key == 'S':
                backward(pi)
            elif key == 'A':
                left(pi)
            elif key == 'D':
                right(pi)
            else:
                stop(pi)

            # Camera control via mouse % position
            if y < 30:
                camera_up(pi)
            elif y > 70:
                camera_down(pi)

            if x < 30:
                camera_left(pi)
            elif x > 70:
                camera_right(pi)

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

center_camera(pi)

handle_command_loop()

# Cleanup
center_camera(pi)
pi.set_servo_pulsewidth(PIN_YAW, 0)
pi.set_servo_pulsewidth(PIN_PITCH, 0)
if addon_board == "0":
    pi.write(PIN_ENABLE_LEFT, 0)
    pi.write(PIN_ENABLE_RIGHT, 0)
pi.stop()

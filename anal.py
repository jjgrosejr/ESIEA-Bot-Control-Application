#!/usr/bin/python3

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
dance(pi)

# Connect joystick
try:
    gamepad = InputDevice("/dev/input/js0")
except FileNotFoundError:
    print("Joystick not found")
    pi.stop()
    exit(1)

# Event loop
for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:
        if event.code == AXIS_UP_DOWN:
            if event.value < 0:
                forward(pi)
            elif event.value > 0:
                backward(pi)
            else:
                stop(pi)
        elif event.code == AXIS_LEFT_RIGHT:
            if event.value < 0:
                left(pi)
            elif event.value > 0:
                right(pi)
            else:
                stop(pi)
        elif event.code == AXIS_CAMERA_UP_DOWN:
            if event.value < 0:
                camera_up(pi)
            elif event.value > 0:
                camera_down(pi)
        elif event.code == AXIS_CAMERA_LEFT_RIGHT:
            if event.value > 0:
                camera_left(pi)
            elif event.value < 0:
                camera_right(pi)
    elif event.type == ecodes.EV_KEY:
        if event.code == 11 and event.value == 1:
            center_camera(pi)
        elif event.code == 9 and event.value == 1:
            os.system("sudo shutdown -h now")
            break

# Cleanup
center_camera(pi)
pi.set_servo_pulsewidth(PIN_YAW, 0)
pi.set_servo_pulsewidth(PIN_PITCH, 0)
if addon_board == "0":
    pi.write(PIN_ENABLE_LEFT, 0)
    pi.write(PIN_ENABLE_RIGHT, 0)
pi.stop()

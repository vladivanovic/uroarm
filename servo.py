#
# This file is for both testing the robot arm and also for functions used by other scripts like Angle.py, Arm.py and Kinematics.py
#

import sys
import time
import math
import serial
import PySimpleGUI as sg
from util import nax, read_params, servo_angle_keys, radian, write_params, spin, get_move_time
import numpy as np
from talker import Talker, TalkerError, SerialPortError
from adafruit_pca9685 import PCA9685
import board
import busio

servo_angles = [np.nan] * nax

#def init_servo_nano(params):
#    global pwm
#    print("Initialising Servo Nano") # this never appears in the console... yet if I take the function out of the main app it doesnt work.
#    try:
#        pwm = PCA9685(address=0x40)
        #pwm.set_pwm_freq(60)
#        pwm.frequency = 60
#    except ModuleNotFoundError:
#        print("no Adafruit")

#def setPWM(ch, pos):
#    pulse = round(150 + (600 - 150) * (pos + 0.5 * math.pi) / math.pi)
#    pwm.set_pwm(ch, 0, pulse)
#    print('set pulse ok') # this never appears in the console...

#def set_servo_angle_nano(ch, deg):
#    rad = radian(deg)
#    setPWM(ch, rad)
#    print('set servo angle ok') # this never appears in the console...

def init_servo(params_arg): # Also used in Arm.py, Angle.py
    global params, servo_angles, servo_param, ser
    params = params_arg
    for ch, deg in enumerate(params['prev-servo']):
        servo_angles[ch] = deg
    com_port = params['COM'] 
    servo_param = params['servo-angle']
    try:
        ser = Talker(com_port)
        print('Connected to Serial Port ' + com_port + ' successfully')
        time.sleep(1)
        cmd = "from code import move_servo, i2c"
        while True:
            try:
                n = ser.send(cmd)
                print("Writing " + str(cmd))
                time.sleep(1)
                break
            except serial.SerialTimeoutException:
                print("Serial Write Time Out")
                time.sleep(1)
    except SerialPortError as e: 
        print(e)
        sys.exit(0)
    except TalkerError as e:
        print(e)

def set_servo_param(ch, scale, offset): # Used in Angle.py
    servo_param[ch] = [scale, offset]
    params['servo-angle'][ch] = [scale, offset]
    write_params(params)
    print('set params ok')

def angle_to_servo(ch, deg): # Used in Arm.py, Angle.py
    coef, intercept = servo_param[ch]
    return coef * deg + intercept

def servo_to_angle(ch, deg): # Used in Kinematics.py, Arm.py, Angle.py
    coef, intercept = servo_param[ch]
    return (deg - intercept) / coef

def set_servo_angle(ch: int, deg: float): # Main Function - Called by 'move_servo' below; Used in Arm.py, Angle.py
    servo_angles[ch] = deg
    cmd = "move_servo(%d,%.1f)" % (ch, deg)
    try:
        reply = ser.send(cmd)
        print("Set Servo Angle: " + reply)
        time.sleep(1)
    except TalkerError as e:
        print(e)

def move_servo(ch, dst): # Main Function - Calls 'set_servo_angle' above; Used in Angle.py
    src = servo_angles[ch]
    move_time = get_move_time()
    start_time = time.time()
    while True:
        #t = (time.time() - start_time) / move_time
        #if 1 <= t:
        #    break
        #deg = t * dst + (1 - t) * src
        deg = dst
        set_servo_angle(ch, deg)
        print("Move Servo Function " + str(ch) + " " + str(deg))
        yield

def move_all_servo(dsts): # Apparently used in Angle.py
    srcs = list(servo_angles)
    move_time = get_move_time()
    start_time = time.time()
    while True:
        t = (time.time() - start_time) / move_time
        if 1 <= t:
            break
        for ch in range(nax):
            deg = t * dsts[ch] + (1 - t) * srcs[ch]
            set_servo_angle(ch, deg)
        yield

if __name__ == '__main__':
    params = read_params()
    init_servo(params)
    layout = [
        [
            spin(f'J{i+1}', f'J{i+1}-servo', int(servo_angles[i]), 0, 180, True) for i in range(nax)
        ]
        +
        [ sg.Text('', size=(15,1)) ]
        +
        [ sg.Button('Close') ]
    ]
    window = sg.Window('Servo', layout, element_justification='c') # disable_minimize=True, 
    moving = None
    while True:
        event, values = window.read(timeout=1)
        #print(f"Event: {event}, Values: {values}")
        if moving is not None:
            try:
                moving.__next__()
            except StopIteration:
                moving = None
                print('========== stop moving ==========')
                params['prev-servo'] = servo_angles
                write_params(params)
        if event in servo_angle_keys:
            ch = servo_angle_keys.index(event)
            deg = values[event]
            # print(f"Channel: {ch}, Degree: {deg}")
            moving = move_servo(ch, deg)
        elif event == sg.WIN_CLOSED or event == 'Close':
            params['prev-servo'] = servo_angles
            print(params)
            write_params(params)
            break
    window.close()
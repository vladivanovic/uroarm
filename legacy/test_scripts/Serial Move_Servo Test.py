import serial
import time

class TalkerError(Exception):
    pass

class SerialPortError(TalkerError):
    pass

class Talker():
    TERMINATOR = '\r'.encode('UTF8')

    def __init__(self, com_port, timeout=1):
        self.com_port = com_port
        try:
            self.serial = serial.Serial(com_port, 115200, timeout=timeout)
            time.sleep(2)
            self.serial.write(b'\x03')
            self.receive()
        except serial.serialutil.SerialException:
            raise SerialPortError(f'The specified serial port does not exist: {com_port}')

    def send(self, text: str):
        line = '%s\r\f' % text
        self.serial.write(line.encode('utf-8'))
        time.sleep(1)  # Give some time for the device to process the command
        reply = self.receive()
        if text not in reply:  # the line should be echoed, so the result should match
            raise TalkerError(f'expected {text} got {reply}')
        return reply

    def receive(self) -> str:
        reply = self.serial.read_all().decode('utf-8').strip()
        # Filter out escape sequences and irrelevant output
        filtered_reply = []
        for line in reply.split('\n'):
            if not any(unwanted in line for unwanted in ["\x1b[", ">>>", "None"]):
                filtered_reply.append(line)
        return '\n'.join(filtered_reply)

    def close(self):
        self.serial.close()

import os
import json

def write_params(params):
    with open('data/arm.json', 'w') as f:
        json.dump(params, f, indent=4)

def read_params():
    if not os.path.isfile('data/arm.json'):

        params = {
            "COM": "COM?",
            "camera-index": 0,
            "prev-servo": [ 90 ] * 6,
            "servo-angle": [[ 1, 90]] * 6,
            "marker-ids": [ 0, 1, 2, 3, 4 ],
            "cameras" : {}
        }
        write_params(params)
        print('data/arm.json is created.')
        sys.exit(0)
    with open('data/arm.json', 'r') as f:
        params = json.load(f)
    return params

import sys
import time
import numpy as np

servo_angles = [np.nan] * 6

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
    while True:
        deg = dst
        set_servo_angle(ch, deg)
        print("Move Servo Function " + str(ch) + " " + str(deg))
        yield

params = read_params()
init_servo(params)

# Set initial position
set_servo_angle(0,60)
time.sleep(5)
set_servo_angle(1,80)
time.sleep(5)
set_servo_angle(2,150)
time.sleep(5)
set_servo_angle(3,110)

# Pick up position

# Lift up

# Set final position

# Let go
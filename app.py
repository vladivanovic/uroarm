#
# Main application, slowly looking to replace PySimpleGUI with Flask as a Web Interface 
# 

# Main imports for Flask app
from flask import Flask, render_template, request, redirect, url_for
import json

# All imports from original Servo.py
import sys
import time
import math
import serial
from util import nax, read_params, servo_angle_keys, radian, write_params, spin, get_move_time
import numpy as np
from talker import Talker, TalkerError, SerialPortError

# All functions copied from original Servo.py
servo_angles = [np.nan] * nax

def init_servo_nano(params):
    global pwm
    try:
        import Adafruit_PCA9685
        print('import Adafruit Successful')
        pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        pwm.set_pwm_freq(60)

    except ModuleNotFoundError:
        print("no Adafruit")

def setPWM(ch, pos):
    pulse = round( 150 + (600 - 150) * (pos + 0.5 * math.pi) / math.pi )
    pwm.set_pwm(ch, 0, pulse)
    print('set pulse ok')

def set_servo_angle_nano(ch, deg):
    rad = radian(deg)
    setPWM(ch, rad)
    print('set servo angle ok')

def init_servo(params_arg):
    global params, servo_angles, servo_param, ser

    params = params_arg

    for ch, deg in enumerate(params['prev-servo']):
        servo_angles[ch] = deg

    com_port = params['COM'] 
    servo_param = params['servo-angle']

    try:
        ser = Talker()
        print('connected to serial port successfully')
        time.sleep(1)
        cmd = "from code import move_servo, i2c\r\n"
        while True:
            try:
                n = ser.send(cmd)
                print("Writing " + str(cmd))
                time.sleep(1)
                break
            except serial.SerialTimeoutException:
                print("write time out")
                time.sleep(1)
    except SerialPortError as e: 
        print(e)
        sys.exit(0)
    except TalkerError as e:
        print(e)

def set_servo_param(ch, scale, offset):
    servo_param[ch] = [scale, offset]
    params['servo-angle'][ch] = [scale, offset]

    write_params(params)
    print('set params ok')

def angle_to_servo(ch, deg):
    coef, intercept = servo_param[ch]

    return coef * deg + intercept

def servo_to_angle(ch, deg):
    coef, intercept = servo_param[ch]

    return (deg - intercept) / coef

def set_servo_angle(ch: int, deg: float):
    servo_angles[ch] = deg
    cmd = "move_servo(%d,%.1f)" % (ch, deg)
    try:
        reply = ser.send(cmd)
        print("Console Output: " + reply)
        time.sleep(1)
    except TalkerError as e:
        print(e)

def move_servo(ch, dst):
    src = servo_angles[ch]

    move_time = get_move_time()
    start_time = time.time()
    while True:
        t = (time.time() - start_time) / move_time
        if 1 <= t:
            break

        deg = t * dst + (1 - t) * src

        set_servo_angle(ch, deg)
        yield

def move_all_servo(dsts):
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

# Main Flask Application
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global servo_angles
    params = read_params()
    init_servo(params)

    if request.method == 'POST':
        for i in range(nax):
            servo_angles[i] = int(request.form[f'J{i+1}-servo'])
        params['prev-servo'] = servo_angles
        write_params(params)
        return redirect(url_for('index'))

    return render_template('index.html', servo_angles=servo_angles)

if __name__ == '__main__':
    app.run(debug=True)


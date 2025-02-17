# MicroPython based Robot Arm Controller
This is my fork of teatime77/uroarm
The original creator created a tutorial (Japanese) at the following link https://uroa.jp/arm/

# Installation Procedure
1. Pull the repo, create a venv
2. Install requirements.txt with pip3
3. Follow instructions at the above link, using the same Servo Controller and Robot Arm configuration where possible (one day I'll copy it here and translate it)
4. Load MicroPython or CircuitPython on to your Pi Pico or Pi Pico 2 board
5. I will translate the rest of the linked document to English in the future!

# Things to keep in mind
1. How you power your environment is important, you will need 5v 3A Power Supply for the Servo Controller+Servos to power this neatly.
2. Servo Specifications - in my case I have been running two different types of Servos, DS3218MG for Motors 1 and 2 and the MG996R for Motors 0, 3, 4 and 5. Looking at the datasheets for these the PWM (Pulse Width Modulation) for the DS3218MG is 500~2500μs for 0 to 180degrees; conversely the MG996R is 1000~2000μs for 0 to 180 degrees. That being said, it seems like PWM being 100~600 on a 50Hz signal seems to be what works when running through an Arduino+PCA9685 - I need to learn more about how all of this works.

# Getting started
1. Servo.py is used for testing the serial connection to your Pico works, then testing the PWM and Servo motors work
2. Angle.py is used for calibrating the motors and setting smaller movement limits to prevent the arm flying off (e.g. 0 on your motor may flip the arm backwards, so you set 90 as the new 0 and limit the scope of the arm)
3. Arm.py will be the main application for triggering all other actions

# Things that helped me
I stepped in to MicroControllers etc as a complete newbie. Here are some links that helped me out along the way.
1. MicroPython downloads https://micropython.org/download/RPI_PICO/
2. Servo Driver documentation https://cdn-learn.adafruit.com/downloads/pdf/adafruit-16-channel-servo-driver-with-raspberry-pi.pdf
3. Learning how PySerial works to troubleshoot Python Script on my local machine interacting with Script on MicroController https://blog.rareschool.com/2021/01/controlling-raspberry-pi-pico-using.html
4. Naturally, the PySerial API Documentation for that too https://pyserial.readthedocs.io/en/latest/pyserial_api.html
5. Many people use Thonny to interact with MicroPython boards, here's how you can use a module MicroPico in VS Code to do the same https://medium.com/its-the-forge/how-to-run-micropython-on-raspberry-pi-pico-via-vs-code-41d7316f5f73#:~:text=To%20run%20a%20code%20on%20Pico%20you%20can,project%20to%20Pico%E2%80%9D%20or%20%E2%80%9CDownload%20project%20from%20Pico%E2%80%9D.
6. Conversely, for Circuit Python people use MuEditor often, more information here https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor
7. Having troubles with my PiPico in general (I think the pins were not soldered on so the connection was not great), I tried moving across to my Arduino but not being familiar with C I leverage this as a resource (along with AI) to get started https://github.com/Circuit-Digest/PCA9685-multiple-servo-control-using-Arduino/tree/main

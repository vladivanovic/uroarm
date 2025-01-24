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
How you power your environment is important, you will need 5v 3A Power Supply for the Servo Controller+Servos to power this neatly.

# Things that helped me
I stepped in to MicroControllers etc as a complete newbie. Here are some links that helped me out along the way.
1. MicroPython downloads https://micropython.org/download/RPI_PICO/
2. Servo Driver documentation https://cdn-learn.adafruit.com/downloads/pdf/adafruit-16-channel-servo-driver-with-raspberry-pi.pdf
3. Learning how PySerial works to troubleshoot Python Script on my local machine interacting with Script on MicroController https://blog.rareschool.com/2021/01/controlling-raspberry-pi-pico-using.html
4. Naturally, the PySerial API Documentation for that too https://pyserial.readthedocs.io/en/latest/pyserial_api.html
5. Many people use Thonny to interact with MicroPython boards, here's how you can use a module MicroPico in VS Code to do the same https://medium.com/its-the-forge/how-to-run-micropython-on-raspberry-pi-pico-via-vs-code-41d7316f5f73#:~:text=To%20run%20a%20code%20on%20Pico%20you%20can,project%20to%20Pico%E2%80%9D%20or%20%E2%80%9CDownload%20project%20from%20Pico%E2%80%9D.
6. Conversely, for Circuit Python people use MuEditor often, more information here https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor
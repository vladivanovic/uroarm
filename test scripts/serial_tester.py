import serial
import time

ser = serial.Serial('/dev/tty.usbmodem2101', 115200)
time.sleep(2)
ser.write(b'\x03')

print("Importing Main")
premoji = "from code import move_servo, i2c\r\n"
premojiEncoded = premoji.encode('utf-8')
print(premojiEncoded)
ser.write(premojiEncoded)

print("I2C Scanning")
moji = "print(i2c.scan())\r\n"
mojiEncoded = moji.encode('utf-8')
print(mojiEncoded)
ser.write(mojiEncoded)

print("Reading response")
readLine = ser.read(size=1)
print(readLine)
print(readLine.strip())
print(readLine.strip().decode('utf-8'))

print("Setting up directory list")
moji2 = "import os\r\n"
moji2Encoded = moji.encode('utf-8')
print(moji2Encoded)
moji3 = "os.listdir('/')\r\n"
moji3Encoded = moji.encode('utf-8')
print(moji3Encoded)
ser.write(moji2Encoded)
ser.write(moji3Encoded)

print("Reading response")
readLine = ser.read(size=1)
print(readLine)
print(readLine.strip())
print(readLine.strip().decode('utf-8'))

ser.close()
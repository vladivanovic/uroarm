from machine import Pin, PWM, I2C
import pca9685
import servo
from utime import sleep

#pin = Pin("LED", Pin.OUT)
#print("LED starts flashing...")
#while True:
#    try:
#        pin.toggle()
#        sleep(1) # sleep 1sec
#    except KeyboardInterrupt:
#        break
#pin.off()
#print("Finished.")

sda = Pin(0)
scl = Pin(1)
id = 0
i2c = I2C(id=id, sda=sda, scl=scl)
print(i2c.scan())
pca = PCA9685(i2c=i2c)
servo = Servos(i2c=i2c)
print("Starting Upright Position")
servo.position(index=0, degrees=90)
sleep(1)
servo.position(index=1, degrees=90)
sleep(1)
servo.position(index=2, degrees=90)
sleep(1)
servo.position(index=3, degrees=90)
sleep(1)
servo.position(index=4, degrees=90)
sleep(1)
servo.position(index=5, degrees=90)
print("Upright Position Done")
sleep(5)
print("Starting Downward Position")
# Lower Number = Clockwise; Higher Number = Anti-Clockwise
servo.position(index=0, degrees=70)
sleep(1)
servo.position(index=1, degrees=70)
sleep(1)
servo.position(index=2, degrees=70)
sleep(1)
servo.position(index=3, degrees=70)
sleep(1)
servo.position(index=4, degrees=70)
sleep(1)
servo.position(index=5, degrees=70)
print("Downward position Done")
sleep(5)
print("Starting Upright Position")
servo.position(index=0, degrees=90)
sleep(1)
servo.position(index=1, degrees=90)
sleep(1)
servo.position(index=2, degrees=90)
sleep(1)
servo.position(index=3, degrees=90)
sleep(1)
servo.position(index=4, degrees=90)
sleep(1)
servo.position(index=5, degrees=90)
print("Upright Position Done")
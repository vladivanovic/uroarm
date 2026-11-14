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
# Need a sleep() per command to not overload it so servo does nothing
servo.position(index=7, degrees=0)
sleep(1)
servo.position(index=7, degrees=180)
sleep(1)
servo.position(index=7, degrees=40)
sleep(1)
servo.position(index=7, degrees=120)
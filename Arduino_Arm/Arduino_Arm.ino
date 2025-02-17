#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);   // Initiates library.

#define SERVOMIN  500  // Minimum pulse length count out of 4096.
#define SERVOMAX  2400 // Maximum pulse length count out of 4096.

int Servo_pin0 = 0; // Defines a counter for servos.
int Servo_pin1 = 1; // Defines a counter for servos.
int Servo_pin2 = 2; // Defines a counter for servos.
int Servo_pin3 = 3; // Defines a counter for servos.
int Servo_pin4 = 4; // Defines a counter for servos.
int Servo_pin5 = 5; // Defines a counter for servos.
int angle;

void setup() {
  pwm.begin();         // 初期設定
  pwm.setPWMFreq(60);  // PWM周期を50Hzに設定
  delay(1000);
  Serial.println("Starting Servo Movement Script!");
  // Servo 1 - Position 1
  angle = 60;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin0, angle);        // サーボを動作させる
  delay(1000);
  // Servo 2 - Position 1
  angle = 50;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin1, angle);        // サーボを動作させる
  delay(1000);
  // Servo 3 - Position 1
  angle = 160;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin2, angle);        // サーボを動作させる
  delay(1000);
  // Servo 4 - Position 1
  angle = 160;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);
  pwm.writeMicroseconds(Servo_pin3, angle);
  delay(1000);
  // Servo 5 - Position 1
  angle = 90;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);
  pwm.writeMicroseconds(Servo_pin4, angle);
  delay(1000);
  // Servo 6 - Claw Position 1
  angle = 90;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);
  pwm.writeMicroseconds(Servo_pin5, angle);
  delay(1000); 
  // Pick up Position Complete!
  // Claw Grabbing now!
  // Servo 6 - Claw Position 1
  angle = 120;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);
  pwm.writeMicroseconds(Servo_pin5, angle);
  delay(1000);   
  // Starting Position 2 Movement!
  // Servo 2 - Position 2
  angle = 70;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin1, angle);        // サーボを動作させる
  delay(1000);
  // Servo 1 - Position 2
  angle = 120;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin0, angle);        // サーボを動作させる
  delay(1000);
  // Starting Position 3 Movement!
  // Servo 2 - Position 3
  angle = 60;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin1, angle);        // サーボを動作させる
  delay(1000);
  // Servo 2 - Position 3.5
  angle = 70;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);  // 角度(0~180)をパルス幅(500~2400μs)に変換
  pwm.writeMicroseconds(Servo_pin1, angle);        // サーボを動作させる
  delay(1000);
  // Claw Releasing now!
  // Servo 6 - Claw Position 1
  angle = 60;
  angle = map(angle,0, 180, SERVOMIN, SERVOMAX);
  pwm.writeMicroseconds(Servo_pin5, angle);
  delay(1000); 
}

void loop() {

}
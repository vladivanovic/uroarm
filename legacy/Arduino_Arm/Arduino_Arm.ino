#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);   // Initiates library.

void setup() {
  Serial.begin(9600);
  Serial.println("PCA9685 Servo loading");
  pwm.begin();         // 初期設定
  pwm.setPWMFreq(50);  // PWM周期を50Hzに設定
  delay(10);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();  // Remove any leading/trailing whitespace
    // Serial.print("Raw data received: ");
    // Serial.println(data);

    // Remove "moveServo(" and ")"
    int startIndex = data.indexOf('(');
    int endIndex = data.indexOf(')');
    if (startIndex >= 0 && endIndex > startIndex) {
      String params = data.substring(startIndex + 1, endIndex);
      // Serial.print("Parameters extracted: ");
      // Serial.println(params);

      int commaIndex = params.indexOf(',');
      if (commaIndex > 0) {
        int chn = params.substring(0, commaIndex).toInt();
        float deg = params.substring(commaIndex + 1).toFloat();

        Serial.print("Parsed - Channel: ");
        Serial.print(chn);
        Serial.print(", Degree: ");
        Serial.println(deg);

        moveServo(chn, deg);
      } else {
        Serial.println("Error: Invalid parameter format");
      }
    } else {
      Serial.println("Error: Invalid command format");
    }
  }
}

void moveServo(int chn, float deg) {
  uint16_t pulseLength;

  if (chn == 0 || chn == 3 || chn == 4 || chn == 5) {
    // Code for Servos 0, 3, 4, 5 - MG996R
    uint16_t pulseMin = 100;  // Example values, adjust as needed
    uint16_t pulseMax = 600;
    pulseLength = map(deg, 0, 180, pulseMin, pulseMax);
    Serial.print("Running code for channel ");
    Serial.println(chn);
  } else if (chn == 1 || chn == 2) {
    // Code for Servos 1, 2 - DS3219MG
    uint16_t pulseMin = 100;  // Example values, adjust as needed
    uint16_t pulseMax = 600;
    pulseLength = map(deg, 0, 180, pulseMin, pulseMax);
    Serial.print("Running code for channel ");
    Serial.println(chn);
  } else {
    // Handle invalid channel
    Serial.println("Error: Invalid channel");
    return;
  }
  Serial.print("Channel: ");
  Serial.print(chn);
  Serial.print(", Degree: ");
  Serial.print(deg);
  Serial.print(", Pulse Length: ");
  Serial.println(pulseLength);
  pwm.setPWM(chn, 0, pulseLength);
}

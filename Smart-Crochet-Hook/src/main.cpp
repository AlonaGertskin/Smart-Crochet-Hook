#include <Arduino.h>
#include <Wire.h>

#define MPU_ADDR 0x69
const unsigned long INTERVAL_US = 20000; // 20,000 microseconds = 20ms (50Hz)
unsigned long nextSampleMicros = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 9);
  
  // Minimal Setup to wake the MPU (Assuming your previous init logic)
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); 
  Wire.write(0x00); 
  Wire.endTransmission();
  
  nextSampleMicros = micros();
}

void loop() {
  // Wait until it's time for the next sample
  if (micros() >= nextSampleMicros) {
    nextSampleMicros += INTERVAL_US;

    // 1. Read MPU Data
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B); 
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, 14, true);

    int16_t ax = Wire.read()<<8 | Wire.read();
    int16_t ay = Wire.read()<<8 | Wire.read();
    int16_t az = Wire.read()<<8 | Wire.read();
    Wire.read(); Wire.read(); // Skip temp
    int16_t gx = Wire.read()<<8 | Wire.read();
    int16_t gy = Wire.read()<<8 | Wire.read();
    int16_t gz = Wire.read()<<8 | Wire.read();

    // 2. Stream as clean CSV
    // Format: ax,ay,az,gx,gy,gz
    Serial.print(millis()); Serial.print(",");
    Serial.print(ax); Serial.print(",");
    Serial.print(ay); Serial.print(",");
    Serial.print(az); Serial.print(",");
    Serial.print(gx); Serial.print(",");
    Serial.print(gy); Serial.print(",");
    Serial.println(gz);
  }
}
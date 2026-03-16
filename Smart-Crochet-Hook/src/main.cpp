#include <Arduino.h>
#include <Wire.h>
#include <MPU9250.h>
#define MPU_ADDR 0x69
MPU9250 mpu;

const unsigned long INTERVAL_US = 20000; // 20,000 microseconds = 20ms (50Hz)
unsigned long nextSampleMicros = 0;

// Function to write a single byte to a specific MPU register
void writeRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);   // The register address
  Wire.write(value); // The data to put in that register
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 9);
  
  writeRegister(0x6B, 0x00); // Wake up the MPU
  writeRegister(0x1B, 0x18); // Set Gyro config (±2000 dps)
  
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
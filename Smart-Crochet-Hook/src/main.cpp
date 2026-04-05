#include <Arduino.h>
#include <Wire.h>
#include <MPU9250.h>
#include "config.h"

// Function to write a single byte to a specific MPU register
void writeRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);   // The register address
  Wire.write(value); // The data to put in that register
  Wire.endTransmission();
}

void setup() {
  Serial.begin(COMM_SPEED);
  Wire.begin(SDA_PIN, SCL_PIN);  
  writeRegister(REG_PWR_MGMT_1, 0x00); // Wake up the MPU
  writeRegister(REG_GYRO_CONFIG, GYRO_FULL_SCALE_2000DPS); // Set Gyro config (±2000 dps)
  
  nextSampleMicros = micros();
}

void loop() {
  // Wait until it's time for the next sample
  if (micros() >= nextSampleMicros) {
    nextSampleMicros += INTERVAL_US;

    // 1. Read MPU Data
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(REG_ACCEL_XOUT_H); 
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, MPU_DATA_LEN, true);

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
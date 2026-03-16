#include <Arduino.h>
#include <Wire.h>
#include <MPU9250.h>
// --- DEFINITIONS ---
#define MPU_ADDR 0x69
#define SDA_PIN 8
#define SCL_PIN 9
// Registers
#define REG_PWR_MGMT_1 0x6B
#define REG_GYRO_CONFIG 0x1B
#define REG_ACCEL_XOUT_H 0x3B
// Settings
#define MPU_DATA_LEN 14
#define GYRO_FULL_SCALE_2000DPS 0x18
#define COMM_SPEED 115200

const unsigned long INTERVAL_US = 20000; // 20,000 microseconds = 20ms (50Hz)
unsigned long nextSampleMicros = 0;
MPU9250 mpu;

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
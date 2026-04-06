#include <Arduino.h>
#include <Wire.h>
#include <MPU9250.h>
#include "config.h"

HookPacket currentPacket;

// Function to write a single byte to a specific MPU register
void writeRegister(uint8_t reg, uint8_t value, bool sendStop = true) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);   // The register address
  if (sendStop) { // If we are just preparing a read, we don't  need to write a value
    Wire.write(value);// The data to put in that register
  }
  Wire.endTransmission(sendStop); // releases the bus after transmission
}

// Helper function to read two bytes and combine them into a 16-bit integer
int16_t read16Bit() {
  return (Wire.read() << 8) | Wire.read();
}

void readMotion(HookPacket &p) {
  writeRegister(ACCEL_XOUT_H, 0, false);
  Wire.requestFrom(MPU_ADDR, MPU_DATA_LEN);
  //p.header = PACKET_HEADER;
  p.timestamp = millis(); // Capture the timestamp when reading the data
// Accelerometer
  p.ax = read16Bit();
  p.ay = read16Bit();
  p.az = read16Bit();
  // Skip Temperature (2 bytes)
  read16Bit(); 
  // Gyroscope
  p.gx = read16Bit();
  p.gy = read16Bit();
  p.gz = read16Bit();
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

    readMotion(currentPacket);

    // Format: ax,ay,az,gx,gy,gz
    Serial.write((uint8_t*)&currentPacket, sizeof(currentPacket));
  }
}
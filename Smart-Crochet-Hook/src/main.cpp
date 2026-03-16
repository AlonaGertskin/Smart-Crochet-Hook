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

const unsigned long INTERVAL_US = 20000; // 20ms (50Hz)
unsigned long nextSampleMicros = 0;

// The __attribute__((packed)) ensures there is no "padding" in the memory
struct __attribute__((packed)) HookPacket {
  uint32_t timestamp; // 4 bytes
  int16_t ax, ay, az; // 6 bytes
  int16_t gx, gy, gz; // 6 bytes
};

HookPacket currentPacket;

// Function to write a single byte to a specific MPU register
void writeRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);   // The register address
  Wire.write(value); // The data to put in that register
  Wire.endTransmission(); // releases the bus after transmission
}

// Helper function to read two bytes and combine them into a 16-bit integer
int16_t read16Bit() {
  return (Wire.read() << 8) | Wire.read();
}

void readMotion(HookPacket &p) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(REG_ACCEL_XOUT_H); 
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, MPU_DATA_LEN, true);

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

 // Capture all data into the packet
  readMotion(currentPacket);

 // Send the raw bytes of the packet to the PC
    Serial.write((uint8_t*)&currentPacket, sizeof(currentPacket));
  }
}
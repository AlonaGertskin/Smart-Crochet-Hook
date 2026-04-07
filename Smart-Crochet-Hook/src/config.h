#pragma once
#include <Arduino.h>

// --- DEFINITIONS ---
#define MPU_ADDR 0x68
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
// Magic Number to identify the start of a packet
const uint16_t PACKET_HEADER = 0xAA55;
const uint16_t METADATA_HEADER = 0xBB66;
const uint16_t SAMPLE_RATE_HZ = 50;

const unsigned long INTERVAL_US = 20000; // 20,000 microseconds = 20ms (50Hz)
unsigned long nextSampleMicros = 0;

// --- DATA STRUCTURES ---
// We use __attribute__((packed)) to ensure NO hidden padding bytes
// are added by the compiler, matching the Python receiver perfectly.
// to keep alignment and avoid padding issues, use aligned types in the struct ie. char and then int32_t instead of int16_t
// Sent ONCE at startup

struct __attribute__((packed)) InfoPacket {
  uint16_t metadataHeader; // 0xBB66
  uint16_t packetSize;     // sizeof(HookPacket)
  uint16_t sampleRateHz;   // 50
};

struct __attribute__((packed)) HookPacket {
  uint16_t header;    // 0xAA55
  uint32_t timestamp; // 4 bytes
  int16_t ax, ay, az; // 6 bytes
  int16_t gx, gy, gz; // 6 bytes
};
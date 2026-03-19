#pragma once
#include <Arduino.h>

// --- HARDWARE MAPPING ---
#define MPU_ADDR 0x69
#define SDA_PIN 8
#define SCL_PIN 9

// --- COMMUNICATION SETTINGS ---
#define COMM_SPEED 115200
#define MPU_DATA_LEN 14

// Magic Number to identify the start of a packet
const uint16_t PACKET_HEADER = 0xAA55;

// --- TIMING SETTINGS ---
const uint32_t SAMPLE_PERIOD_US = 20000; // 20ms (50Hz)

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
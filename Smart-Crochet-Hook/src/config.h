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

const unsigned long INTERVAL_US = 20000; // 20,000 microseconds = 20ms (50Hz)
unsigned long nextSampleMicros = 0;
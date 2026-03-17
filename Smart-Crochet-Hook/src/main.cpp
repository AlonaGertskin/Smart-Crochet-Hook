#include <Arduino.h>
#include <Wire.h>
#include <MPU9250.h>
#include "config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

MPU9250 mpu;
HookPacket currentPacket;
SemaphoreHandle_t timerSemaphore;

unsigned long nextSampleMicros = 0;
//TODO send a packet for agreeing on the struct size and alignment between the ESP32 and the Python receiver
// also add header in the packet

// Function to write a single byte to a specific MPU register
void writeRegister(uint8_t reg, uint8_t value, bool sendStop = true) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);   // The register address
  if (sendStop) { // If we are just preparing a read, we don't  need to write a value
    Wire.write(value);// The data to put in that register
  }; 
  Wire.endTransmission(sendStop); // releases the bus after transmission
}

// Helper function to read two bytes and combine them into a 16-bit integer
int16_t read16Bit() {
  return (Wire.read() << 8) | Wire.read();
}

// --- Timer Interrupt Service Routine (ISR) ---
// This function runs in the "Interrupt Context"
// TODO: check if IRAM_ATTR is needed
// IRAM_ATTR is a special compiler attribute used in ESP32 programming. 
// It tells the internal linker: "Do not keep this function in the Flash memory; 
//move it into the Internal RAM (Static RAM) instead." 
void IRAM_ATTR onTimer(void* arg) {
  // Give the semaphore to unblock the loop
  xSemaphoreGiveFromISR(timerSemaphore, NULL);
}

void readMotion(HookPacket &p) {
  writeRegister(ACCEL_XOUT_H, 0, false);
  Wire.requestFrom(MPU_ADDR, MPU_DATA_LEN);
  
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
  // initialize the timer semaphore
  timerSemaphore = xSemaphoreCreateBinary();

  // MPU9250 Library Setup
  MPU9250Setting setting = {};
  if (!mpu.setup(MPU_ADDR, setting)) {
          while (1) {
              Serial.println("❌ ERROR: Sensor not found.");
              delay(5000);
          }
        }
  Serial.println("✅ Sensor Online and Configured!");
  nextSampleMicros = micros();

  // Configure Hardware Timer
  const esp_timer_create_args_t timer_args = {
    .callback = &onTimer,
    .name = "sample_trigger"
  };

  esp_timer_handle_t timer_handle;
  esp_timer_create(&timer_args, &timer_handle);
  
  // Start periodic timer
  esp_timer_start_periodic(timer_handle, SAMPLE_PERIOD_US);

  Serial.println("✅ RTOS Timer System Active");
} 

void loop() {
  // Wait here forever until the timer "Gives" the semaphore.
  // This uses 0% CPU while waiting.
  if (xSemaphoreTake(timerSemaphore, portMAX_DELAY) == pdTRUE) {

 // Capture all data into the packet
  readMotion(currentPacket);

 // Send the raw bytes of the packet to the PC
    Serial.write((uint8_t*)&currentPacket, sizeof(currentPacket));
  }
}
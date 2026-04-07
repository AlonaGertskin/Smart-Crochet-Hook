#include <Arduino.h>
#include <Wire.h>
#include <MPU9250.h>
#include "config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

HookPacket currentPacket;
uint32_t startTime = 0;
SemaphoreHandle_t timerSemaphore;

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
  p.header = PACKET_HEADER;
  p.timestamp = millis() - startTime; // Capture the timestamp when reading the data
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

// --- The ISR (Interrupt Service Routine) ---
// This runs in the background on the hardware timer's schedule
void IRAM_ATTR onTimer(void* arg) {
    // We use a special "FromISR" version of xSemaphoreGive
    // because we are inside a hardware interrupt.
    xSemaphoreGiveFromISR(timerSemaphore, NULL);
}

 void setup() {
  // Initialize Serial and I2C, then configure the MPU9250
  Serial.begin(COMM_SPEED);
  Wire.begin(SDA_PIN, SCL_PIN);  
  writeRegister(REG_PWR_MGMT_1, 0x00); // Wake up the MPU
  writeRegister(REG_GYRO_CONFIG, GYRO_FULL_SCALE_2000DPS); // Set Gyro config (±2000 dps)
  
  // Set up the hardware timer to trigger every 20ms (50Hz)
  timerSemaphore = xSemaphoreCreateBinary();

  const esp_timer_create_args_t timer_args = {
    .callback = &onTimer,
    .name = "50hz"
    };

  esp_timer_handle_t timer_handle;
  esp_timer_create(&timer_args, &timer_handle);
  esp_timer_start_periodic(timer_handle, 20000);

  // WAIT FOR PYTHON
  while (Serial.available() <= 0) {
    delay(10); // Do nothing until Python sends a byte
  }
  Serial.read(); // Clear the byte sent by Python to start the handshake

  // Send the Handshake Info Packet
  InfoPacket info = {METADATA_HEADER, sizeof(HookPacket), SAMPLE_RATE_HZ};
  Serial.write((uint8_t*)&info, sizeof(info));
  Serial.flush(); // Ensure it's sent before stream starts

} 

void loop() {
  // This will now block (sleep) until the timer gives the semaphore
    if (xSemaphoreTake(timerSemaphore, portMAX_DELAY) == pdTRUE) {
      readMotion(currentPacket);
      // Format: ax,ay,az,gx,gy,gz
      Serial.write((uint8_t*)&currentPacket, sizeof(currentPacket));
    }
  }

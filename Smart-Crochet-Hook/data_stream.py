import serial
import time
import csv

# --- CONFIGURATION ---
PORT = 'COM3'        # <--- Double check this in PlatformIO
BAUD = 115200
FILE_NAME = "baseline_test.csv"
RECORD_TIME = 5      # Seconds to record

def main():
    try:
        # Connect to the Smart Hook
        # Note: Ensure PlatformIO Serial Monitor is CLOSED before running this
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)  # Give the ESP32 a moment to wake up
        ser.reset_input_buffer()
        
        print(f"📡 Connected to Hook on {PORT}")
        print(f"⏺️  Recording {RECORD_TIME}s of data to '{FILE_NAME}'...")

        with open(FILE_NAME, "w", newline='') as f:
            writer = csv.writer(f)
            # Write the header
            writer.writerow(["ms", "ax", "ay", "az", "gx", "gy", "gz"])
            
            start_time = time.time()
            count = 0
            
            while (time.time() - start_time) < RECORD_TIME:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    parts = line.split(',')
                    # Verification: Only save if we have all 7 columns
                    if len(parts) == 7:
                        writer.writerow(parts)
                        count += 1

        print(f"✅ Success! Captured {count} samples.")
        ser.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
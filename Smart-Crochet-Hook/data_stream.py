import serial
import time
import csv
import os

# --- CONFIGURATION ---
PORT = 'COM3' 
BAUD = 115200
FOLDER = "stitch_tests"

# Create the folder if it doesn't exist
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

def record_session(ser):
    stitch_type = input("\n🧶 Enter stitch type (e.g., sc, dc, baseline): ").strip().lower()
    duration = float(input("⏱️  Enter duration in seconds (e.g., 3): "))
    
    print(f"\nReady? Get into position for '{stitch_type}'...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Generate filename with a unique timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(FOLDER, f"{stitch_type}_{timestamp}.csv")
    
    print("⏺️  RECORDING...")
    ser.reset_input_buffer()
    
    samples = []
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            parts = line.split(',')
            if len(parts) == 7:
                samples.append(parts)
    
    print("🛑 STOP!")
    
    # Save to CSV
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ms", "ax", "ay", "az", "gx", "gy", "gz"])
        writer.writerows(samples)
        
    print(f"✅ Saved {len(samples)} samples to {filename}")

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)
        print(f"📡 Hook connected on {PORT}")
        
        while True:
            record_session(ser)
            cont = input("\nRecord another take? (y/n): ").lower()
            if cont != 'y':
                break
                
        ser.close()
        print("\nSession finished. Happy crocheting! 🧶")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
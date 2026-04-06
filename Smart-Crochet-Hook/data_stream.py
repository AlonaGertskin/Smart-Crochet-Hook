import serial
import time
import csv
import os
import threading
import struct
import receiver

# --- CONFIGURATION ---
PORT = 'COM3' 
BAUD = 115200
FOLDER = "stitch_tests"

if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

def record_session(hook):
    stitch_type = input("\n🧶 Stitch type (sc, dc, baseline): ").strip().lower()
    stitch_count = int(input("🔢 How many stitches are you about to do? "))
    
    print(f"\nPreparation: Get ready for {stitch_count} {stitch_type}(s)...")
    input("Press [ENTER] to start the 3-second countdown...")
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("⏺️  RECORDING... (Press [ENTER] to stop when finished)")
    
    # Clear the buffer so we start with fresh data
    #ser.reset_input_buffer()
    
    samples = []
    stop_event = threading.Event()

    def wait_for_user():
        input()
        stop_event.set()

    # Start the "Stop Monitor" thread
    input_thread = threading.Thread(target=wait_for_user)
    input_thread.daemon = True
    input_thread.start()

    start_time = time.time()
    
    # Keep reading until the user hits Enter
    while not stop_event.is_set():
        packet = hook.get_packet()
        if packet:
            samples.append(packet)

    duration = time.time() - start_time
    print(f"🛑 STOP! Recorded {duration:.2f} seconds.")
    
    # Save the file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(FOLDER, f"{stitch_type}_x{stitch_count}_{timestamp}.csv")
    
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ms", "ax", "ay", "az", "gx", "gy", "gz"])
        writer.writerows(samples)
        
    print(f"✅ Saved {len(samples)} samples to {filename}")
    print(f"📊 Avg samples per stitch: {len(samples)/stitch_count:.1f}")

def main():
    try:
        hook = receiver.HookReceiver(PORT, BAUD)

        #ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)
        print(f"📡 Hook connected on {PORT}")
        while True:
            record_session(hook)
            if input("\nRecord another? (y/n): ").lower() != 'y':
                break
                
        hook.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
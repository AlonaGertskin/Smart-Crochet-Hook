import time
import csv
import os
import receiver
import threading

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
    
    print("⏺️  RECORDING... (Press [ENTER] to stop)")
    
    samples = []
    stop_event = threading.Event()

    # --- THE FIX: Threaded Input Listener ---
    def wait_for_user():
        input() # This blocks here until you hit Enter
        stop_event.set() # Signal the loop to stop

    # Start the "Stop Monitor" thread in the background
    input_thread = threading.Thread(target=wait_for_user)
    input_thread.daemon = True # Kill thread if main script exits
    input_thread.start()

    start_time = time.time()
    
    # Now the loop checks the 'stop_event' instead of 'True'
    while not stop_event.is_set():
        packet = hook.get_packet()
        if packet:
            samples.append(packet)
        else:
            # Prevent the CPU from spinning 100% when no data is ready
            time.sleep(0.001) 

    duration = time.time() - start_time
    print(f"\n🛑 STOP! Recorded {duration:.2f} seconds.")
    
    if samples:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(FOLDER, f"{stitch_type}_x{stitch_count}_{timestamp}.csv")
        
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ms", "ax", "ay", "az", "gx", "gy", "gz"])
            writer.writerows(samples)
            
        print(f"✅ Saved {len(samples)} samples to {filename}")
        print(f"📊 Avg samples per stitch: {len(samples)/stitch_count:.1f}")
    else:
        print("⚠️ No data captured. Check your ESP32 connections.")

def main():
    try:
        hook = receiver.HookReceiver(PORT, BAUD)
        time.sleep(2)
        
        # This sends the 's' and verifies the InfoPacket (0xBB66)
        if not hook.sync_handshake(): return 

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
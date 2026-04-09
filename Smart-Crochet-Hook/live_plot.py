import socket
import time
import receiver

# --- CONFIGURATION ---
PORT = 'COM3' 
BAUD = 115200
TELEPLOT_ADDR = ("127.0.0.1", 47269)

# Initialize UDP socket for Teleplot
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_to_teleplot(name, value):
    """Formats and sends a UDP packet to the Teleplot VS Code extension."""
    msg = f"{name}:{value}|g"
    sock.sendto(msg.encode(), TELEPLOT_ADDR)

def main():
    hook = None
    try:
        hook = receiver.HookReceiver(PORT, BAUD)
        time.sleep(2)
        
        if not hook.sync_handshake(): 
            print("❌ Handshake failed.")
            return 

        print(f"📡 Live Plotting started on {PORT}. Open Teleplot in VS Code to see data.")
        
        while True:
            packet = hook.get_packet()
            if packet:
                # Unpack the tuple: (ms, ax, ay, az, gx, gy, gz)
                if packet:
                    timestamp, ax, ay, az, gx, gy, gz = packet
                    
                    # Grouping Accelerometer data on one graph
                    send_to_teleplot("Accel/x", ax)
                    send_to_teleplot("Accel/y", ay)
                    send_to_teleplot("Accel/z", az)
                    
                    # Grouping Gyroscope data on a separate second graph
                    send_to_teleplot("Gyro/x", gx)
                    send_to_teleplot("Gyro/y", gy)
                    send_to_teleplot("Gyro/z", gz)
                else:
                # Small sleep to prevent high CPU usage
                    time.sleep(0.001) 
                
    except KeyboardInterrupt:
        print("\n👋 Stopping live plot...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Check if hook exists AND if it's not None
        if 'hook' in locals() and hook is not None:
            try:
                hook.close()
                print("🔌 Serial connection closed.")
            except:
                pass

if __name__ == "__main__":
    main()
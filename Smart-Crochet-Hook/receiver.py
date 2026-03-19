import struct
import serial

INFO_HEADER = 0xBB66
DATA_HEADER = 0xAA55

class HookReceiver:
    def __init__(self, port, baud=115200):
        self.packet_format = "" # We leave this empty initially
        self.packet_size = 0  # Will be set by InfoPacket
        # Initialize the Serial connection to the ESP32-C3
        # 'port' is the physical address (e.g., COM3)
        # 'baud' must match the COMM_SPEED (115200) defined in  main.cpp
        # 'timeout=1' ensures the script doesn't freeze if the hook is unplugged
        self.ser = serial.Serial(port, baud, timeout=1) # consider changing to API so that in the future bluetooth can be used as well
    
    def sync_handshake(self):
            print("Waiting for Handshake...")
            while True:
                raw_header = self.ser.read(2)
                if len(raw_header) < 2: # wait for the header bytes to arrive
                    continue
                
                header = struct.unpack('<H', raw_header)[0]
                if header == INFO_HEADER:
                    info = self.ser.read(4)
                    # Read total size and sample rate from ESP32
                    self.packet_size, rate = struct.unpack('<HH', info)
                    
                    # --- DYNAMIC FORMAT GENERATION ---
                    # Calculate how many 2-byte 'shorts' are left after the 
                    # 2-byte header and 4-byte timestamp
                    payload_bytes = self.packet_size - 2 - 4
                    num_shorts = payload_bytes // 2
                    
                    # Build the format: < (Little Endian), L (Timestamp), 
                    # then 'n' number of 'h' (shorts)
                    self.data_format = f"<L{num_shorts}h"
                    
                    print(f"✅ Handshake! Packet Size: {self.packet_size} bytes")
                    print(f"✅ Auto-Configured Format: {self.data_format}")
                    print(f"✅ Sample Rate: {rate} Hz")
                    return True
            
    def get_packet(self):
        # We need at least packet_size bytes in the buffer to proceed
        if self.ser.in_waiting >= self.packet_size:
            # Hunt for the header (0xAA55)
            # On Little Endian, 0xAA55 arrives as [0x55, 0xAA]
            check = self.ser.read(1)
            if not check or ord(check) != 0x55: return None
            check2 = self.ser.read(1)
            if not check2 or ord(check2) != 0xAA: return None

            payload = self.ser.read(self.packet_size - 2)
            
            try:
                return struct.unpack(self.data_format, payload)
            except struct.error:
                return None
        return None

    def close(self):
        self.ser.close()
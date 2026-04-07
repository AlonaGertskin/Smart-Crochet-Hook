import struct
import serial

INFO_HEADER = 0xBB66
DATA_HEADER = 0xAA55

class HookReceiver:
    def __init__(self, port, baud=115200):
        self.packet_size = 0  # Will be set by handshake
        self.sample_rate = 0  # Will be set by handshake
        self.data_format = "" # Will be built after handshake
        # Initialize the Serial connection to the ESP32-C3
        # 'port' is the physical address (e.g., COM3)
        # 'baud' must match the COMM_SPEED (115200) defined in  main.cpp
        # 'timeout=1' ensures the script doesn't freeze if the hook is unplugged
        self.ser = serial.Serial(port, baud, timeout=1) # consider changing to API so that in the future bluetooth can be used as well
        self.ser.reset_input_buffer() # Clears old junk so we start fresh with the InfoPacket 
    
    def sync_handshake(self):
        """Sends the 's' signal and waits for the InfoPacket."""
        self.ser.write(b's') 
        
        # Expecting 6 bytes: [Header(2), Size(2), Rate(2)]
        raw = self.ser.read(6)
        
        if len(raw) == 6 and raw[:2] == b'\x66\xbb':
            # Unpack Little-Endian: H=Header, H=Size, H=Rate
            _, size, rate = struct.unpack("<HHH", raw)
            self.packet_size = size
            self.sample_rate = rate
            
            # Dynamically build the format for HookPacket (18 bytes)
            # < : Little Endian
            # H : Header (0xAA55) -> 2 bytes
            # L : Timestamp (ms) -> 4 bytes
            # hhhhhh : 6 IMU values -> 12 bytes (6 * 2)
            # Total: 18 bytes
            self.data_format = "<H L hhhhhh"
            return True
        else:
            print(f"❌ Handshake failed. Received: {raw.hex(' ')}")
            return False
            
    def get_packet(self):
        """Reads one HookPacket and returns the data tuple."""
        # We need at least packet_size bytes in the buffer
        if self.ser.in_waiting >= self.packet_size:
            payload = self.ser.read(self.packet_size)
            
            # Verify the Data Header (0xAA55 -> b'\x55\xaa')
            if payload[:2] == b'\x55\xaa':
                try:
                    # Unpack: (Header, ms, ax, ay, az, gx, gy, gz)
                    unpacked = struct.unpack(self.data_format, payload)
                    # Return only the data (skip the header at index 0)
                    return unpacked[1:] 
                except struct.error:
                    return None
            else:
                # If we lose sync, clear one byte and try again next time
                self.ser.read(1) 
        return None

    def close(self):
        self.ser.close()
        
if __name__ == "__main__":
    PORT = "COM3" 
    BAUD = 115200
    
    hook = HookReceiver(PORT, BAUD)
    
    if hook.sync_handshake():
        print("Ready to receive data packets...")
        while True:
            packet = hook.get_packet()
            if packet:
                print(f"Received Packet: {packet}")

import struct
import serial

INFO_HEADER = 0xBB66
DATA_HEADER = 0xAA55

class HookReceiver:
    def __init__(self, port, baud=115200):
        self.packet_format = "<L h h h h h h"
        self.packet_size = 16  # Will be set by InfoPacket later
        # Initialize the Serial connection to the ESP32-C3
        # 'port' is the physical address (e.g., COM3)
        # 'baud' must match the COMM_SPEED (115200) defined in  main.cpp
        # 'timeout=1' ensures the script doesn't freeze if the hook is unplugged
        self.ser = serial.Serial(port, baud, timeout=1) # consider changing to API so that in the future bluetooth can be used as well
        self.ser.reset_input_buffer() # Clears old junk so we start fresh with the InfoPacket 
            
    def get_packet(self):
        # We need at least packet_size bytes in the buffer to proceed
        if self.ser.in_waiting >= self.packet_size:
            payload = self.ser.read(self.packet_size)
            try:
                return struct.unpack(self.packet_format, payload)
            except struct.error:
                return None
        return None

    def close(self):
        self.ser.close()
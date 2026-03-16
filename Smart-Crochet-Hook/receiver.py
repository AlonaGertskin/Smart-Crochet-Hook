import struct
import serial

class HookReceiver:
    def __init__(self, port, baud=115200):
        # The 'contract': < (little endian), I (unsigned int), 6h (6 short integers)
        # Matches the 'HookPacket' struct in main.cpp
        self.packet_format = "<I6h" 
        self.packet_size = struct.calcsize(self.packet_format)
        # Initialize the Serial connection to the ESP32-C3
        # 'port' is the physical address (e.g., COM3)
        # 'baud' must match the COMM_SPEED (115200) defined in  main.cpp
        # 'timeout=1' ensures the script doesn't freeze if the hook is unplugged
        self.ser = serial.Serial(port, baud, timeout=1)

    def get_packet(self):
        """Wait for and return one unpacked packet of data."""
        # Check the Serial buffer
        # Proceed if we have at least the  size of our HookPacket struct
        if self.ser.in_waiting >= self.packet_size:
            raw_data = self.ser.read(self.packet_size) 
            try:
                # Unpacks: (timestamp, ax, ay, az, gx, gy, gz) according to the defined format
                return struct.unpack(self.packet_format, raw_data)
            except struct.error:
                return None
        return None

    def close(self):
        self.ser.close()
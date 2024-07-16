import pyfirmata
import struct
import time

# Define the port where the Arduino is connected
port = '/dev/tty.usbmodem211301'  # Update this with the actual port where your Arduino is connected

# Create a new board instance
board = pyfirmata.Arduino(port)
# Start iterator to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Function to handle received SysEx messages
def sysex_callback(*data):
    conv_data = []
    for d in range(0, len(data), 2):
        conv_data.append(data[d] + (data[d+1] << 7))
    print("\tReceived SysEx message:", [d for d in data])
    print(f"\tConverted data: {[bin(d) for d in conv_data]} = {conv_data}")

# Function to handle received SysEx messages
def sysex_callback2(*data):
    conv_data = []
    for d in range(0, len(data), 2):
        conv_data.append(data[d] + (data[d+1] << 7))
    print("\tReceived SysEx message:", [d for d in data])
    print(f"\tConverted data: {[bin(d) for d in conv_data]} = {conv_data}")

    # Unpack the bytes object as floats
    float_value = []
    for i in range(0, len(conv_data), 4):
        float_value.append( struct.unpack('f', bytes(conv_data[i:i+4])) )
    print(f"\tFloat value: {float_value}")

# Attach the callback functions to the appropriate Firmata events
board.add_cmd_handler(0x13, sysex_callback2)

print("STARTING")

# Send a raw SysEx message to the Arduino
# Replace '0x42' and '0x01' with your custom SysEx command and data
for msg in range(0,255):
    
    # board.send_sysex(pyfirmata.START_SYSEX, [msg])
    # print(f"Sent SysEx message:\n\t{pyfirmata.START_SYSEX}, {msg:3}")

    # time.sleep(1)
    board.send_sysex(0x13, [100])
    print(f"Sent SysEx message:\n\t0x13, 100")
    time.sleep(1)

# Wait for responses
time.sleep(2)

# Close the connection
board.exit()

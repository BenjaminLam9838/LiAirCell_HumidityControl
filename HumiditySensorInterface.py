import pyfirmata
import time
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class HumiditySensorInterface:
    def __init__(self, timeout_tries=5):
        #Initialize local variables
        self.response = None
        self.max_retries = timeout_tries

    # Initialize the Firmata interface
    def connect_board(self, port):
        # Create a new board instance
        self.board = pyfirmata.Arduino(port)
        
        # Start iterator thread so that serial buffer doesn't overflow
        self.it = pyfirmata.util.Iterator(self.board)
        self.it.start()

    def add_sensor_addr(self, sensor_addr):
        # Attach the callback functions to the appropriate Firmata events
        for addr in sensor_addr:
            self.board.add_cmd_handler(addr, self._sysex_callback)

    def get_data(self, sensor_addr):
        self.board.send_sysex(sensor_addr, [])
        #Wait to get the response 5 times, with a 0.05s delay, then throw an error
        #We are waiting for _sysex_callback to set the response variable
        tries = 0
        while self.response is None and tries < self.max_retries:
            time.sleep(0.03)
            tries += 1
        if self.response is None:
            raise TimeoutError("No response received from the sensor.")

        ret = {'temperature': self.response[0], 'humidity': self.response[1]}
        self.response = None
        return ret

    # Function to handle received SysEx messages
    def _sysex_callback(self, *data):
        conv_data = []
        # Combine pairs of 7-bit values, LSB 7 bits first, then MSB 7 bits
        for i in range(0, len(data), 2):
            # Combine LSB (data[i]) and MSB (data[i+1]) into a 8-bit value
            combined_value = data[i] | (data[i+1] << 7)
            conv_data.append(combined_value)

        # Unpack the bytes object as floats
        float_value = []
        for i in range(0, len(conv_data), 4):
            float_value.append( struct.unpack('f', bytes(conv_data[i:i+4]))[0] )
        
        # print("\tReceived SysEx message length: ", len(data))
        # print(f"\tConverted data length: {len(conv_data)}")
        # print(f"\tFloat value: {float_value}")
        
        self.response = float_value
    
    # Function to handle received SysEx messages (Test function)
    def _sysex_callback_test(*data):
        conv_data = []
        for d in range(0, len(data), 2):
            conv_data.append(data[d] + (data[d+1] << 7))
        print("\tReceived SysEx message:", [d for d in data])
        print(f"\tConverted data: {[bin(d) for d in conv_data]} = {conv_data}")

# HSI = HumiditySensorInterface()
# HSI.connect_board('/dev/cu.usbmodem21101')
# HSI.add_sensor_addr([0x13, 0x14])

# HSI.get_data(0x15)


# # Create a figure and axis for the plot
# fig, ax = plt.subplots()
# ax2 = ax.twinx()
# ax2.set_ylabel('Humidity', color='b')
# ax2.tick_params(axis='y', labelcolor='b')

# # Initialize an empty list to store the data
# data = []

# # Define the update function for the animation
# def update(frame):
#     # Get the data from the sensor
#     try:
#         sensor_data = sensor.get_data(0x13)
#         print(f"SHT85:   {sensor_data}")
#         data.append(sensor_data)
#     except TimeoutError:
#         print("SHT85: No response received from the sensor.")
    
#     # Clear the axis
#     ax.clear()
#     # ax2.clear()

#     # Plot the data on the first y-axis
#     ax.plot([d['temperature'] for d in data], 'r-', label='Temperature')
#     ax.set_ylabel('Temperature', color='r')
#     ax.tick_params(axis='y', labelcolor='r')
#     ax.set_xlabel('Time')
    
#     # Create a second y-axis
#     ax2.plot([d['humidity'] for d in data], 'b-', label='Humidity')
#     ax2.set_ylabel('Humidity', color='b')
#     ax2.tick_params(axis='y', labelcolor='b')
    
#     # Set the title
#     ax.set_title('Live Plot of Sensor Data')
#     ax.set_ylim([0, 40])
#     ax2.set_ylim([0, 100])
    
# # Create the animation
# animation = FuncAnimation(fig, update, interval=500)

# # Show the plot
# plt.show()
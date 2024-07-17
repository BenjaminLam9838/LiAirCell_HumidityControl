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
        print("Board connected")

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

        # If we get here, we have a response
        #Convert the bytes to humidity and temperature
        ret = {'humidity': ((self.response[0]&0x3F)<<8 | self.response[1]) / 2**14 *100, 
               'temperature': (self.response[2]<<6 | self.response[3]>>2) / 2**14 *165 - 40}

        self.response = None
        return ret

    # Function to handle received SysEx messages
    def _sysex_callback(self, *data):
        received_bytes = []
        # Combine pairs of 7-bit values, LSB 7 bits first, then MSB 7 bits to get the 8 bit values
        for i in range(0, len(data), 2):
            # Combine LSB (data[i]) and MSB (data[i+1]) into a 8-bit value
            combined_value = data[i] | (data[i+1] << 7)
            received_bytes.append(combined_value)

        # # Unpack the bytes object as floats
        # float_value = []
        # for i in range(0, len(conv_data), 4):
        #     float_value.append( struct.unpack('f', bytes(conv_data[i:i+4]))[0] )
        
        print("\tReceived SysEx message:", [d for d in data])
        print(f"\tConverted data: {[bin(d) for d in received_bytes]} = {received_bytes}")
        # print(f"\tFloat value: {float_value}")
        
        self.response = received_bytes
    
    # Function to handle received SysEx messages (Test function)
    def _sysex_callback_test(self, *data):
        received_bytes = []
        for d in range(0, len(data), 2):
            received_bytes.append(data[d] + (data[d+1] << 7))
        print("\tReceived SysEx message:", [d for d in data])
        print(f"\tConverted data: {[bin(d) for d in received_bytes]} = {received_bytes}")
        self.response = received_bytes
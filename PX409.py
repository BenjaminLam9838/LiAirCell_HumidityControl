import serial
import time

class PX409:
    def __init__(self, timeout_s=1):
        self.baudrate = 115200
        self.timeout_s = timeout_s

    def connect(self, port):
        self.port = port
        self.connection = serial.Serial(port, self.baudrate, bytesize=8, parity='N', stopbits=1, timeout=self.timeout_s)

    def send_command(self, command):
        command_bytes = f'{command}\r'.encode('ascii')

        #print out the command
        # print("Sending: ", command_bytes)
        # print(f"{'':9}", end='')
        # for i in command_bytes:
        #     print(hex(i), end=' ')
        # print('\n')

        self.connection.write(command_bytes)
        self.connection.flush()

    def read_response(self):
        response = self.connection.readline().decode('ascii')
        self.connection.flushInput()    # Each response is only one line, so we can clear the input buffer
        return response

    def get_pressure(self):
        """
        Sends a command to retrieve the pressure reading from the device.

        Returns:
            float: The pressure reading in psig.
        """
        self.send_command('P')
        response = self.read_response().strip().split(' ')
        return float(response[0])

    def close(self):
        self.connection.close()
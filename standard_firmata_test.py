import time
from pyfirmata import Arduino, util

# Replace '/dev/tty.usbmodem21101' with the port your Arduino is connected to
board = Arduino('/dev/tty.usbmodem21101')

# Start an iterator thread so PyFirmata can update itself
it = util.Iterator(board)
it.start()

# Define the pin
pin = board.get_pin('d:13:o')

# Blink the LED
try:
    while True:
        pin.write(1)  # Turn LED on
        print("LED on")
        time.sleep(1)  # Wait for 1 second
        pin.write(0)  # Turn LED off
        print("LED off")
        time.sleep(1)  # Wait for 1 second
except KeyboardInterrupt:
    print("Exiting...")
finally:
    board.exit()

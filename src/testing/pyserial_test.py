import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configure the serial port
port = '/dev/tty.usbmodem21101'  # Change this to your actual port
baudrate = 9600  

# Create a serial object
ser = serial.Serial(port, baudrate, timeout=1)

start_time = time.time()
start_value = None

while start_value is None:
    if ser.in_waiting > 0 and ser.readable():
        data = ser.readline().decode().strip()
        inc, start_value = map(float, data.split(','))  # Split the data into two values
        start_time = time.time()

        print("STARTING", time.time()-start_time, inc, start_value)
        ser.flushInput() # Flush the serial port to read a fresh line next time


# Read from the serial port and flush after each reading
while True:
    if ser.in_waiting > 0 and ser.readable():
        #Read all data from the serial port and only grab the last line
        data = ser.read_all().decode().strip().split('\r\n')
        data = data[-1]

        # Split the data into two values
        inc, value = map(float, data.split(','))  
        print(time.time()-start_time, inc, value-start_value)

    time.sleep(1)

# # Initialize data buffers
# x_data = []
# y_data = []

# # Create a figure and axis
# fig, ax = plt.subplots()
# line, = ax.plot([], [], lw=2, marker='o')

# # Initialize the plot limits
# ax.set_xlim(0, 100)
# ax.set_ylim(-10, 10)
# ax.set_title("Real-time Data from Serial Port")
# ax.set_xlabel("Time")
# ax.set_ylabel("Value")

# # Function to initialize the plot
# def init():
#     line.set_data([], [])
#     return line,

# # Function to update the plot
# def update(frame):
#     if ser.in_waiting > 0:
#         data = ser.read_all().decode().strip()
#         data = data.split('\r\n')
#         data = [d.split(',') for d in data]
#         data = [[float(dd) for dd in d] for d in data if len(d) == 2]  # Ensure each line has two values
#         # print(data)
#         if data:
#             for point in data:
#                 timestamp, value = point
#                 x_data.append(timestamp)
#                 y_data.append(value)

#                 # Limit the data to the last 100 points for performance
#                 x_data[:] = x_data[-100:]
#                 y_data[:] = y_data[-100:]
                
#                 # Update plot limits based on data
#                 ax.set_xlim(min(x_data), max(x_data))
#                 ax.set_ylim(min(y_data), max(y_data))

#                 line.set_data(x_data, y_data)
                
#                 # Redraw the axes
#                 fig.canvas.draw()
    
#     return line,

# # Create an animation
# ani = animation.FuncAnimation(fig, update, init_func=init, blit=True, interval=1000)

# # Show the plot
# plt.show()

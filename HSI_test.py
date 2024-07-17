import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from HumiditySensorInterface import HumiditySensorInterface

HSI = HumiditySensorInterface()
HSI.connect_board('/dev/tty.usbmodem21101')
HSI.add_sensor_addr([0x10, 0x13, 0x28])

# for x in range(5):
#     print("Getting data from 0x28")

#     print(HSI.get_data(0x28))
#     time.sleep(1)

# # HSI.add_sensor_addr([0x28, 0x12])

# # print(HSI.get_data(0x12))


# Create a figure and axis for the plot
fig, ax = plt.subplots()
ax2 = ax.twinx()
ax2.set_ylabel('Humidity', color='b')
ax2.tick_params(axis='y', labelcolor='b')

# Initialize an empty list to store the data
data = []

# Define the update function for the animation
def update(frame):
    # Get the data from the sensor
    try:
        sensor_data = HSI.get_data(0x28)
        print(f"CC2:   {sensor_data}")
        data.append(sensor_data)
    except TimeoutError:
        print("CC2: No response received from the sensor.")
    
    # Clear the axis
    ax.clear()
    # ax2.clear()

    # Plot the data on the first y-axis
    ax.plot([d['temperature'] for d in data], 'r-', label='Temperature')
    ax.set_ylabel('Temperature', color='r')
    ax.tick_params(axis='y', labelcolor='r')
    ax.set_xlabel('Time')
    
    # Create a second y-axis
    ax2.plot([d['humidity'] for d in data], 'b-', label='Humidity')
    ax2.set_ylabel('Humidity', color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    
    # Set the title
    ax.set_title('Live Plot of Sensor Data')
    ax.set_ylim([0, 40])
    ax2.set_ylim([0, 100])
    
# Create the animation
animation = FuncAnimation(fig, update, interval=500)

# Show the plot
plt.show()
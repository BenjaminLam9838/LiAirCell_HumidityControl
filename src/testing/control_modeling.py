import time
import matplotlib.pyplot as plt
import simple_pid
from app import parse_timeseries
import sys
import numpy as np

# Define a simple controlled system
class ControlledSystem:
    def __init__(self):
        self.value = 0

    def update(self, control_input):
        # Simple model: next value depends on current value and control input
        self.value += (control_input - self.value) * 0.1  # Arbitrary dynamics

        #Simulate a real sensor, add noise to the value
        return self.value + np.random.normal(-0.05, 0.05)

# Initialize the PID controller with desired parameters
pid = simple_pid.PID(5.7585,15.9046,0, setpoint=1)
pid.output_limits = (-10, 10)    # Output value will be between 0 and 10
pid.sample_time = 0.1  # PID update interval in seconds

# Initialize the controlled system
controlled_system = ControlledSystem()

start_time = time.time()
# Lists to store time series data for plotting
times = [time.time() - start_time]
values = [controlled_system.value]
controls = [0]

#Create the setpoints list
setpoints = {'time': [], 'vals': []}
exprdur = [('sin(4*t)', 5),
            ('sin(2*t)', 3),
            ('2',3),
            ('5',3)]
exprdur = [('1', 5)]
setpoints['time'], setpoints['vals'] = parse_timeseries(exprdur)


# Run the simulation
try:
    while True:
        current_time = time.time() - start_time
        if current_time > setpoints['time'][-1]:
            raise KeyboardInterrupt
        
        # Get the setpoint value at the current time, and set it to the PID controller
        cur_time_ind = np.where(setpoints['time'] <= current_time)[0][-1]
        pid.setpoint = setpoints['vals'][cur_time_ind]

        # Compute new output from the PID according to the system's current value
        control = 1#pid(controlled_system.value)

        # Feed the PID output to the system and get its current value
        v = controlled_system.update(control)

        # Store the time, value, and control for plotting
        times.append(current_time)
        values.append(v)
        controls.append(control)

        # Print the current time, system value, and control value
        print(f"t: {current_time:.1f}s, System Value: {v:.2f}, Control: {control:.2f}, SP: {pid.setpoint:.2f}")

        # Wait for the next update
        time.sleep(pid.sample_time)
except KeyboardInterrupt:
    # Handle the interrupt to stop the simulation and plot the results
    print("Simulation stopped.")

    # Plot the results
    plt.figure(figsize=(10, 5))

    # Plot system value
    plt.subplot(2, 1, 1)
    plt.plot(times, values, label='System Value', color='k', linewidth=1, marker='o')
    plt.plot(setpoints['time'], setpoints['vals'], label='Setpoint', linestyle='--', color='r')
    plt.xlabel('Time (s)')
    plt.ylabel('System Value')
    plt.legend()
    plt.grid(True)

    # Plot control input
    plt.subplot(2, 1, 2)
    plt.plot(times, controls, label='Control Input')
    plt.xlabel('Time (s)')
    plt.ylabel('Control Input')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    print(values)
    print(times)
    plt.show()


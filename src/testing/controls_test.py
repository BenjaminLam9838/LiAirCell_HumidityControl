import control as ctrl
import matplotlib.pyplot as plt
import numpy as np

# Define the transfer function of the system to be controlled
system = ctrl.TransferFunction([1], [1,3,2])

# Define the PID controller parameters
Kp = 10
Ki = 10
Kd = 5

# Create the PID controller
pid = ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])


# Create the closed-loop system
closed_loop_system = ctrl.feedback(pid * system, 1)

# Simulate the response of the closed-loop system to a step input
time = np.linspace(0, 10, 1000)
time, response = ctrl.step_response(closed_loop_system, time)

# Plot the step response
plt.plot(time, response)
plt.xlabel('Time (s)')
plt.ylabel('Response')
plt.title('Step Response with PID Control')
plt.grid()
plt.show()

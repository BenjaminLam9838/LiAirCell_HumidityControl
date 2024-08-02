import random
import time
from datetime import datetime
import asyncio
import queue
import math
import logging
from alicat import FlowController
from HumiditySensorInterface import HumiditySensorInterface
import sys
import numpy as np
import sympy as sp


# Define a class to represent a generic Data Aquisition component.  
# This class handles the data acquisition and storage for the component. 
# Only the most recent 10 000 data points are stored in the data queue, 
# the rest will be written to a file, if selected.
class DAQ:
    start_time = -1

    def __init__(self):
        # If the start time has not been set, set it for all components
        if DAQ.start_time == -1:
            DAQ.start_time = time.time()

        self.data_queue = queue.Queue(10000)
        self.save_file = None
        self.port = None
        self.is_connected = False

    def reset_start_time(self):
        DAQ.start_time = time.time()

    async def fetch_data(self):
        """
        Fetches data from the hardware.

        This method fetches data from the hardware and puts it into a data queue for a sliding window.
        This function should be implemented by the child class
        In the DAQ class it is simulated data

        Remember to put the data into the data queue using self._track_data(data)

        Returns:
            data is fetched successfully, False otherwise.
        """
        pass
        
    def _track_data(self, data):
        """
        Track and save data to a queue and optionally to a file.
        If it is full, the oldest data will be removed

        Args:
            data (dict): A dictionary containing the data to be tracked. It should have the following keys:
                - datetime: The datetime of the data.
                - values: A dictionary containing the values to be tracked.

        Returns:
            None
        """
        if self.data_queue.qsize() >= self.data_queue.maxsize:
            self.data_queue.get_nowait()
        self.data_queue.put_nowait(data)

        # Save the data to a file if selected
        if self.save_file is not None:
            # Check if the file is empty, if so, write the header
            if self.save_file.tell() == 0:
                header_line = 'datetime,' + ','.join(data['values'].keys())
                self.save_file.write(header_line + '\n')
            # Write the data to the file
            data_line = f"{data['datetime']}," + ','.join([str(v) for v in data['values'].values()])
            self.save_file.write(data_line + '\n')
    
    # Function to set the save file location
    def set_save_file(self, file_path):
        if not self.is_connected:
            return
        self.save_file = open(file_path, 'w')
        logging.info(f"Opened save file at {file_path}")

    # Function to close the save file
    def close_save_file(self):
        if self.save_file is None:
            return
        
        self.save_file.close()
        logging.info(f"Closed save file at {self.save_file.name}")
        self.save_file = None
        
    # Function to get all the data from the data queue
    def pop_data_queue(self):
        data = []
        # Retrieve all data from the queue without removing it
        while self.data_queue.qsize() > 0:
            data.append(self.data_queue.get_nowait())

        return data
    
class MFC (DAQ):
    def __init__(self):
        super().__init__()
        self.port = ""

        self.is_connected = False
        
    # Attempts a connection to the MFC
    async def connect(self, port):
        """
        Attempts a connection to the flow controller.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        self.port = port
        try:
            self.fc = FlowController(address=self.port)
            message = "Connected to MFC on port " + self.port
            self.is_connected = True
            logging.info(f"Connected to MFC on port {self.port} \n{'':20} {self.fc}")
        except:
            message = "Could not connect to MFC"
            self.is_connected = False
            logging.error("Could not connect to MFC")
        
        return [self.is_connected, message]


    async def fetch_data(self):
        """
        Fetches data from the connected MFC. 
        fc.get() takes ~200ms to complete, with SD of 5ms. This is the 
        bottleneck in this function and takes the most time; the rest of the function is negligible.

        Returns:
            bool: True if data is fetched successfully, False otherwise.
        """
        if not self.is_connected:
            return False

        try:
            fc_result = await self.fc.get()
        except Exception as e:
            logging.error("MFC, fetch_data", e)
            self.is_connected = False
            return False
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Get current datetime

        # Remove the 'control_point' and 'gas' keys from the result
        fc_result.pop('control_point', None)
        fc_result.pop('gas', None)
        data = {'datetime': dt, 'values': fc_result}

        # Put the data into the data queue for a sliding window
        self._track_data(data)

        return data

    # Set the flow rate of the MFC
    async def set_flow_rate(self, flow_rate):
        """
        Sets the flow rate of the hardware. fc.set_flow_rate() takes ~200ms to complete, with SD of 3ms.

        Parameters:
        - flow_rate: The desired flow rate to be set.

        Returns:
        - True if the flow rate is successfully set, False otherwise.
        """
        if not self.is_connected:
            return False
        try:
            await self.fc.set_flow_rate(flow_rate)
        except Exception as e:
            logging.error("MFC, set_flow_rate", e)
            self.is_connected = False
            return False
        logging.info(f"Set MFC flow rate to {flow_rate}, port {self.port}")
        return True

class HumiditySensor(DAQ):
    HSI = None
    
    def __init__(self, HSI):
        super().__init__()
        self.port = None

        self.is_connected = False

        #Save the interface with humidity sensors
        if HumiditySensor.HSI is None:
            HumiditySensor.HSI = HSI
        
    # Attempts a connection to the Sensor
    async def connect(self, port):
        """
        Attempts a connection to the flow controller.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        self.port = port


        # Try to connect to the sensor
        try:
            logging.info("Attempting connection to SENSOR")
            HumiditySensor.HSI.add_sensor_addr([self.port])
            HumiditySensor.HSI.get_data(self.port) #This is to check if the sensor is connected, throws TimeoutError if not
            message = f"Connected to Sensor with address {hex(self.port)}"
            self.is_connected = True
        except Exception as e:
            message = "Humidity Sensor: Could not connect to SENSOR"
            self.is_connected = False
            logging.error(f"Could not connect to SENSOR.\n{'':<20}Error: {e}")
            return [self.is_connected, message]
         
        logging.info(f"SENSOR connected on port {hex(self.port)}!")
        return [self.is_connected, message]


    async def fetch_data(self):
        """
        Fetches data from the connected Sensor.

        Returns:
            bool: True if data is fetched successfully, False otherwise.
        """
        if not self.is_connected:
            return False

        try:
            result = HumiditySensor.HSI.get_data(self.port)
        except Exception as e:
            logging.error("HumiditySensor, fetch_data", e)
            if str(e).find("not connected") > 0:
                self.is_connected = False
            return False
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Get current datetime

        data = {'datetime': dt, 'values': result}

        # Put the data into the data queue for a sliding window
        self._track_data(data)

        return data

class DummyDAQ(DAQ):
    def __init__(self, freq=1):
        super().__init__()
        self.port = ""
        self.freq = freq

    async def fetch_data(self):
        """
        Creates simulated data and puts it into the data queue.

        Returns:
            bool: True if data is fetched successfully, False otherwise.
        """
        await asyncio.sleep(random.uniform(0.01, 0.05))

        timestamp = time.time() - DAQ.start_time
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        data = {'datetime': dt, 
            'values': {'y1': 20*math.sin(2*math.pi*self.freq * timestamp) + 20, 'y2': 20*math.cos(2*math.pi*self.freq * timestamp) +20}}
        
        # Put the data into the data queue for a sliding window
        self._track_data(data)

        return data
    
    #Always connects
    async def connect(self, port):
        """
        Attempts a connection to the flow controller.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        self.port = port
        self.is_connected = True
        
        return [self.is_connected, "Connected to DUMMYDAQ"]


class HardwareGroup:
    def __init__(self, daq_instances, max_list_length):
        self.daq_instances = daq_instances
        self.daq_lists = {}
        self.max_list_length = max_list_length

        self.flask_command_queue = asyncio.Queue()

        # Initialize a list to store data for each instance
        for daq in self.daq_instances.keys():
            self.daq_lists[daq] = []

    def add_flask_command(self, func, params):
        self.flask_command_queue.put_nowait( (func, params) )

    # Worker function to run commands in the queue
    async def _worker(self, func, kwargs):
        if asyncio.iscoroutinefunction(func):
            await func(**kwargs)
        else:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, func, kwargs)

    async def run_flask_commands(self):
        # Run all commands in the queue in parallel by assigning workers
        tasks = []
        for _ in range(self.flask_command_queue.qsize()):
            func, params = await self.flask_command_queue.get()
            tasks.append( self._worker(func, params) )
            logging.info(f"Working: {func.__name__} with params {params}")
            self.flask_command_queue.task_done()
        # Await all tasks to complete
        await asyncio.gather(*tasks)

    async def fetch_data(self):
        """
        Fetches data from all DAQ instances and pushes it to a list.

        Returns:
            None
        """
        for daq_key in self.daq_instances.keys():
            current_data = await self.daq_instances[daq_key].fetch_data()
            if current_data is not False:
                self._push_to_list(daq_key, current_data)


    #Manage the list so that it stays at the max list length
    def _push_to_list(self, daq_key, data):
        self.daq_lists[daq_key].append(data)

        if len(self.daq_lists[daq_key]) > self.max_list_length:
            self.daq_lists[daq_key].pop(0)
    
    def get_list(self, daq_key):
        return self.daq_lists[daq_key]

class HumiditySetpoint(DAQ):
    def __init__(self):
        super().__init__()
        self.is_connected = False
        self.setpoint_func = None
        self.time_points = None
        self.setpoints = None

    def set_setpoint(self, setpoint, time_min=None):
        """
        Set the setpoint function based on the given setpoint values and optional time intervals.

        Parameters:
        setpoint (int, float, list): Setpoint value(s).
        time (list, optional): Corresponding time points for the setpoints. Default is None.
        """
        if isinstance(setpoint, (int, float)) and time_min is None:
            self.setpoint_func = lambda t: setpoint
        elif isinstance(setpoint, list) and isinstance(time_min, list):
            self.setpoints = setpoint
            self.time_points = [t*60 for t in time_min]      # Convert minutes to seconds
            self.setpoint_func = self._piecewise_setpoint
        else:
            raise ValueError("Invalid input: setpoint must be a single number or a list/array with corresponding time list/array.")

    def get_setpoint(self, time_s):
        """
        Get the setpoint value at a given time.

        Parameters:
        t_value (float): The time at which to evaluate the setpoint function.

        Returns:
        float: The setpoint value at the given time.
        """
        if self.setpoint_func is not None:
            return self.setpoint_func(time_s)
        else:
            raise ValueError("Setpoint function is not defined.")


    def _piecewise_setpoint(self, time_s):
        """
        Evaluate the piecewise setpoint function at a given time value.

        Parameters:
        t_value (float): The time at which to evaluate the setpoint function.

        Returns:
        float: The setpoint value at the given time.
        """
        index = np.searchsorted(self.time_points, time_s, side='right') - 1
        if index < 0:
            index = 0
        return self.setpoints[index]

    async def fetch_data(self):
        # Don't output data if not connected. In this case, it means that the setpoint functionality
        # has not been started.
        if not self.is_connected:
            return False

        timestamp = time.time() - DAQ.start_time
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Get current datetime
        try:
            setpoint = self.get_setpoint(timestamp)
        except ValueError as e:
            return False
        
        data = {'timestamp': timestamp, 'datetime': dt, 'values': {'humidity_setpoint': setpoint}}

        self._track_data(data)
        return data
    
    def enable(self):
        '''
        Use the connection to start the setpoint function
        '''
        self.is_connected = True
        DAQ.start_time = time.time()
        return [self.is_connected, 
                f"Setpoint definition started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}"]
    
    def disable(self):
        '''
        Use the connection to stop the setpoint function
        '''
        self.is_connected = False

    @property
    def is_enabled(self):
        """
        Getter method for is_enabled.

        Returns:
            bool: The value of self.is_connected.
        """
        return self.is_connected

    def close_save_file(self):
        super().close_save_file()
        self.is_connected = False
    


def parse_timeseries(expression_duration_pairs):
    """
    Parses a list of expression-duration pairs and generates a time series of values.

    Parameters:
    expression_duration_pairs (list): A list of tuples where each tuple (expr, dur) contains an expression (string) and its duration (float).

    Returns:
    tuple: A tuple containing two numpy arrays - the time values and the corresponding values generated from the expressions.
    """

    t = sp.symbols('t')
    values = []
    time_min = []

    current_time = 0
    for expr, duration in expression_duration_pairs:
        # Skip empty expressions
        # if len(expr) == 0 or duration == :
        #     continue

        # Parse the expression
        parsed_expr = sp.sympify(expr)
        # Create a numpy function from the sympy expression
        func = sp.lambdify(t, parsed_expr, modules='numpy')

        # Generate the times for this duration
        segment_time = [i/60 for i in range( int(duration * 60) +1 )]
        segment_values = [func(x) for x in segment_time]

        # Append the values and times
        values.extend(segment_values)
        time_min.extend([t+current_time for t in segment_time])
        
        # Update current time for the next segment
        current_time += duration


    return time_min, values


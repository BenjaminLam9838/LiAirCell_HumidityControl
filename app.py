from flask import Flask, jsonify, render_template, request
import logging
import Hardware
import asyncio
import datetime
import math
import random
import time
import threading
import uuid
import os
import sympy as sp
import numpy as np

# TO DO:
# 1. Implement the set_flow_arbitrary route:
#    - Make a class that handles the flow rate setpoints, should make a new thread 
#      that starts a timer and sets the flow rate at each time point. Make the 
#      constructor the list of segments
# Bad idea, just put in in the run loop.  This will work better since theres only one thread, so no blocking conditions


print('\n\n\n')
# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s | %(message)s',
                    datefmt='%H:%M:%S',
                    handlers=[
                        logging.FileHandler("app.log"),  # Log to a file
                        logging.StreamHandler()          # Also log to console
                    ])

# Change Flask's logging to only show warnings and above
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Flask application
app = Flask(__name__, static_url_path='/static')
app.config['SERVER_NAME'] = 'localhost:5000'  # Replace with your server name and port

# GLOBAL VARIABLES
CONTROL_LOOP_ON = False
CONTROL_LOOP_SETPOINTS = None
CONTROL_LOOP_STARTTIME = None

# Create instances of the hardware components (Data aquisition components)
daq_instances = {
    'test1': Hardware.DummyDAQ(1),
    'test2': Hardware.DummyDAQ(0.5),
    'test3': Hardware.DummyDAQ(0.03),
    'MFC1': Hardware.MFC(),
    'MFC2': Hardware.MFC(),
    'SHT1': Hardware.HumiditySensor(),
    'SHT2': Hardware.HumiditySensor(),
}
hg = Hardware.HardwareGroup(daq_instances, 10)


######################
### HELPER FUNCTIONS 
######################
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
    time_s = []

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
        time_values = np.linspace(0, duration, int(duration * 60))
        segment_values = [func(x) for x in time_values]

        # Append the values and times
        values.extend(segment_values)
        time_s.extend(time_values + current_time)
        
        # Update current time for the next segment
        current_time += duration

    return np.array(time_s), np.array(values)


######################
### ROUTES
######################
@app.route('/<daq_id>/fetch_data', methods=['GET'])
def fetch_data(daq_id):
    daq = daq_instances.get(daq_id)
    data = daq.pop_data_queue()
    # logging.debug(f"Data served [{daq_id:10}] = {len(data):3} points")

    return jsonify(data)

# Route to connect to a component using a specific port
@app.route('/<daq_id>/connect', methods=['POST', 'GET'])
async def connect(daq_id):
    daq = daq_instances.get(daq_id)

    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            requestData = request.get_json()
            port = requestData.get('port')

            if not port:
                return jsonify({'success': False, 'message': 'Port not provided', 'port': ''}), 400
            
            # Attempt to connect to the daqonent with the provided port
            success, message = await daq.connect(port)
            print("\n\nConnected on port " + daq.port)
            print(message)
            
            if success:
                return jsonify({'success': True, 'message': message, 'port': daq.port}), 200
            else:
                return jsonify({'success': False, 'message': message, 'port': daq.port}), 200
        
        except Exception as e:
            print("\n\nError connecting to MFC on port " + daq.port)
            print(e)
            return jsonify({'success': False, 'message': str(e)}), 500
    
    if request.method == 'GET':
        daq = daq_instances.get(daq_id)
        logging.debug(f"Checking connection status of {daq_id}", daq.is_connected)

        if daq.is_connected:
            return jsonify({'success': True, 'message': f'Connected using port {daq.port}', 'port': daq.port}), 200
        else:
            return jsonify({'success': False, 'message': f'No Connection on port {daq.port}', 'port': daq.port}), 200

@app.route('/api/set_flow_arbitrary', methods=['POST', 'GET'])
async def set_flow_arbitrary():
    if request.method == 'POST':
        # Parse the JSON data from the request body
        requestData = request.get_json()
        #Remove the empty sections
        requestData = [req for req in requestData if req['segmentString'] != '' or req['duration'] != '']
        expr_pairs = [ (sect['segmentString'], float(sect['duration'])) for sect in requestData ]

        time_s, values = parse_timeseries(expr_pairs)
        print(time_s, values)
        # Set the setpoint flow rates for the MFCs


        # Return the timeseries to the client for plotting
        return jsonify({'time': time_s.tolist(), 'values': values.tolist()})
    # if request.method == 'GET':
    #     jsonify({'time': time_s.tolist(), 'values': values.tolist()})


@app.route('/')
def index():
    return render_template('index.html')

######################
### Hardware run loop
######################
def start_control_loop():
    CONTROL_LOOP_ON = True
    CONTROL_LOOP_STARTTIME = time.time()



async def run_loop():
    # Setup
    

    # Looping
    while True:
        # Queery data from all components (DAQs), 
        # save the recent data to a running windowed list of the last 50 elements
        await hg.fetch_data()
        
        if CONTROL_LOOP_ON:
            # Calculate the control loop, get desired setpoints
            # Set the MFCs
            pass
        

        await asyncio.sleep(0.05)


if __name__ == '__main__':
    # Log whenever the main method is run
    logging.debug("Main method is being run.")
    
    # Function to create the asyncio loop in a separate thread
    def start_asyncio_loop():
        logging.debug("Starting new asyncio loop thread.")

        # Initialization function for the asyncio loop in the new thread
        def asyncio_loop_thread():        
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_loop())
        
        thread_id = uuid.uuid4()
        loop_thread = threading.Thread(target=asyncio_loop_thread, name=str(thread_id))
        loop_thread.daemon = True
        loop_thread.start()
    
    # Log the value of WERKZEUG_RUN_MAIN
    werkzeug_run_main = os.getenv('WERKZEUG_RUN_MAIN')
    logging.debug(f"WERKZEUG_RUN_MAIN: {werkzeug_run_main}")

     # Ensure the loop starts only once, even with Flask's auto-reloader
    if werkzeug_run_main == 'true':
        logging.debug("Starting Flask app and asyncio loop.")
        start_asyncio_loop()


    print(f"App running at: http://{app.config['SERVER_NAME']}")
    app.run(debug=True)
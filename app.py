from flask import Flask, jsonify, render_template, request
from Helper_Functions import *
from HumiditySensorInterface import HumiditySensorInterface
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
import sys


# TO DO:
# 1. Implement the set_flow_arbitrary route:
#    - Make a class that handles the flow rate setpoints, should make a new thread 
#      that starts a timer and sets the flow rate at each time point. Make the 
#      constructor the list of segments
# Bad idea, just put in in the run loop.  This will work better since theres only one thread, so no blocking conditions


print('\n\n\n')
# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)-9s%(levelname)-8s | %(message)s',
                    datefmt='%H:%M:%S',
                    handlers=[
                        logging.FileHandler("app.log"),  # Log to a file
                        logging.StreamHandler()          # Also log to console
                    ])

# Change Flask's logging to only show warnings and above
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Flask application
app = Flask(__name__, static_url_path='/static')
app.config['SERVER_NAME'] = 'localhost:4000'  # Replace with your server name and port

# GLOBAL VARIABLES
CONTROL_LOOP_ON = False
CONTROL_LOOP_SETPOINTS = None
CONTROL_LOOP_STARTTIME = None
ARDUINO_PORT = '/dev/tty.usbmodem21101'
HSI = HumiditySensorInterface()

# Create instances of the hardware components (Data aquisition components)
daq_instances = {
    'test1': Hardware.DummyDAQ(1),
    'test2': Hardware.DummyDAQ(0.5),
    'test3': Hardware.DummyDAQ(0.03),
    'MFC1': Hardware.MFC(),
    'MFC2': Hardware.MFC(),
    'SHT1': Hardware.HumiditySensor(HSI),
    'SHT2': Hardware.HumiditySensor(HSI),
}
hg = Hardware.HardwareGroup(daq_instances, 10)


######################
### ROUTES
######################
@app.route('/<daq_id>/fetch_data', methods=['GET'])
def fetch_data(daq_id):
    daq = daq_instances.get(daq_id)
    data = daq.pop_data_queue()
    # logging.debug(f"Data served [{daq_id:10}] = {len(data):3} points")

    # if daq_id == 'SHT1':
    #     logging.info(f"Data served [{daq_id:10}] = {data}")

    return jsonify(data)

# Route to connect to a component using a specific port
@app.route('/<daq_id>/connect', methods=['POST', 'GET'])
async def connect(daq_id):
    daq = daq_instances.get(daq_id)
    logging.debug(f"Attempting to connect to {daq_id} on port {daq.port}")

    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            requestData = request.get_json()
            port = requestData.get('port')
            logging.info(f"[CONNECT] post {daq_id}: {requestData}")

            if not port:
                return jsonify({'success': False, 'message': 'Port not provided', 'port': ''}), 400
            
            # Attempt to connect to the daqonent with the provided port
            success, message = await daq.connect(port)
            
            if success:
                return jsonify({'success': True, 'message': message, 'port': daq.port}), 200
            else:
                return jsonify({'success': False, 'message': message, 'port': daq.port}), 200
        
        except Exception as e:
            logging.error(f"Error connecting to {type(daq)} on port {daq.port}\n{'':20}{e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    if request.method == 'GET':
        daq = daq_instances.get(daq_id)
        logging.debug(f"Checking connection status of {daq_id}", daq.is_connected)

        if daq.is_connected:
            return jsonify({'success': True, 'message': f'Connected using port {daq.port}', 'port': daq.port}), 200
        else:
            return jsonify({'success': False, 'message': f'No Connection on port {daq.port}', 'port': daq.port}), 200

@app.route('/plot_flow_arbitrary', methods=['POST', 'GET'])
async def plot_flow_arbitrary():
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
async def run_loop():
    # Setup
    
    # Try a connection to the Arduino
    try:
        logging.info(f"Starting connection to BOARD on port {ARDUINO_PORT}")
        HSI.connect_board(ARDUINO_PORT)
    except:
        logging.error("Could not connect to BOARD, CHANGE PORT")
        sys.exit()  
    logging.info(f"HSI connected on port {ARDUINO_PORT}")

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
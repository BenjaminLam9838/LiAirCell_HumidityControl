from flask import Flask, jsonify, render_template, request
from HumiditySensorInterface import HumiditySensorInterface
import logging
import Hardware
import asyncio
import datetime
import math
import time
import threading
import uuid
import os
import sys
import json
import simple_pid

TEST_MODE = True   # Set to True to run in test mode, averts required hardware connections

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

# GLOBAL VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CONTROL_DATA = { 'mode': 'MAN', 'params': {'MFC1': 0, 'MFC2': 0} }
HARDWARE_LOOP_FREQ_HZ = 2     # Hardware run loop frequency [Hz]
PID_GAINS = [5.7585,15.9046,0]  # PID gains for the control loop [Kp, Ki, Kd]
DEFAULT_SAVE_DIR = os.getcwd() + '/data'

# Humidity Sensor Interface, handles Arduino communication
ARDUINO_PORT = '/dev/cu.usbmodem143301'
HSI = HumiditySensorInterface()

# MFC Devices
MFC1_PORT = '/dev/tty.usbserial-AU057C72'
MFC2_PORT = '/dev/tty.usbserial-AU05IFFF'

# Pressure Sensor Port
PS_PORT = '/dev/cu.usbserial-555149'

# Create instances of the hardware components (Data aquisition components)
daq_instances = {
    'test1': Hardware.DummyDAQ(0.05),
    'test2': Hardware.DummyDAQ(0.5),
    'test3': Hardware.DummyDAQ(0.03),
    'MFC1': Hardware.MFC(),
    'MFC2': Hardware.MFC(),
    'SHT1': Hardware.HumiditySensor(HSI),
    'SHT2': Hardware.HumiditySensor(HSI),
    'PS1': Hardware.PressureSensor(),
    'humidity_setpoint': Hardware.HumiditySetpoint(PID_GAINS, 1/HARDWARE_LOOP_FREQ_HZ),
}
hg = Hardware.HardwareGroup(daq_instances, 10)

# Try a connection to the Arduino
try:
    logging.info(f"Starting connection to ARDUINO on port {ARDUINO_PORT}")
    HSI.connect_board(ARDUINO_PORT)
    # Connect to the MFCs
    logging.info(f"HSI connected on port {ARDUINO_PORT}")
except:
    logging.error("Could not connect to ARDUINO, CHANGE PORT")
    if not TEST_MODE: sys.exit()  # Exit the program if the Arduino connection fails

# Try a connection to the humidity sensors
asyncio.run(daq_instances['SHT1'].connect(0x31))
asyncio.run(daq_instances['SHT2'].connect(0x32))

# Try a connection to the MFCs
logging.info(f"Starting connection to MFC1 on port {MFC1_PORT}")
asyncio.run(daq_instances['MFC1'].connect(MFC1_PORT))
logging.info(f"Starting connection to MFC2 on port {MFC2_PORT}")
asyncio.run(daq_instances['MFC2'].connect(MFC2_PORT))

if  daq_instances['MFC1'].is_connected and daq_instances['MFC2'].is_connected:
    # If connected, set MFCs to 0 flow
    logging.info("MFCs connected")
    CONTROL_DATA = {'mode': 'MAN', 'params': {'MFC1': 0, 'MFC2': 0} }
    hg.add_flask_command( daq_instances['MFC1'].set_flow_rate, {'flow_rate': 0} )
    hg.add_flask_command( daq_instances['MFC2'].set_flow_rate, {'flow_rate': 0} )
else:
    logging.error("Could not connect to MFCs, CHANGE PORT")
    if not TEST_MODE: sys.exit()

# Try a connection to the pressure sensor
try:
    daq_instances['PS1'].connect(PS_PORT)
except:
    logging.error("Could not connect to Pressure Sensor, CHANGE PORT")
    if not TEST_MODE: sys.exit()

# Flask application
app = Flask(__name__, static_url_path='/static')
app.config['SERVER_NAME'] = 'localhost:4000'  # Replace with your server name and port
app_start_time = time.time()




######################
### FLASK ROUTES
######################

def print_non_serializable_parts(data):
    """
    Recursively checks the data to find and print non-JSON serializable parts.
    """
    def is_serializable(obj):
        try:
            json.dumps(obj)
            return True
        except TypeError:
            # print the object type
            print(f'Non-serializable type found: {type(obj)}')
            return False

    def check_data(data, path=''):
        if isinstance(data, list):
            for i, item in enumerate(data):
                check_data(item, f'{path}[{i}]')
        elif isinstance(data, dict):
            for key, value in data.items():
                check_data(value, f'{path}["{key}"]')
        elif not is_serializable(data):
            print(f'Non-serializable data found at {path}: {data}')

    check_data(data)
    print('Done checking non-serializable parts.')

@app.route('/<daq_id>/fetch_data', methods=['GET'])
def fetch_data(daq_id):
    daq = daq_instances.get(daq_id)
    data = daq.pop_data_queue()

    if daq_id == 'PS1':
        print(f"Pressure: {data}")
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
            
            # Add the connection command to the command queue
            await daq.connect(port)
            
            return jsonify({'success': True, 'message': 'Connection command sent', 'port': port}), 200        
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

# Route to start data acquisition
@app.route('/start_recording_data', methods=['POST'])
def start_recording_data():
    current_timestamp = time.strftime("%y%m%d_%H%M")

    #Get the set directory to save the data to
    requestData = request.get_json()
    directory = requestData['directory']
    if directory == '':
        directory = f"/LAC_{current_timestamp}"

    # Set the directory to save the data to
    directory = f"{DEFAULT_SAVE_DIR}{directory}"

    if not os.path.exists(directory):
        os.makedirs(directory)

    message = "Data recording started."
    # Start the setpoint functionality if not already started
    if not daq_instances['humidity_setpoint'].is_enabled: 
        _, message_2 = daq_instances['humidity_setpoint'].enable()
        message += f"   {message_2}"
        logging.info(f"Setpoint connected: {daq_instances['humidity_setpoint'].is_enabled}")

    # Set the save file for each DAQ instance
    for daq_key in daq_instances.keys():
        filepath = f"{directory}/{daq_key}_{current_timestamp}.csv"
        daq_instances[daq_key].set_save_file( filepath )
    return jsonify({'success': True, 'message': message}), 200

# Route to stop data acquisition
@app.route('/stop_recording_data', methods=['POST'])
def stop_recording_data():
    for daq in daq_instances.keys():
        daq_instances[daq].close_save_file()

    return jsonify({'success': True, 'message': 'Data recording stopped'}), 200

@app.route('/plot_flow_arbitrary', methods=['POST', 'GET'])
async def plot_flow_arbitrary():
    if request.method == 'POST':
        # Parse the JSON data from the request body
        requestData = request.get_json()
        #Remove the empty sections
        requestData = [req for req in requestData if req['segmentString'] != '' or req['duration'] != '']
        expr_pairs = [ (sect['segmentString'], float(sect['duration'])) for sect in requestData ]

        time_s, values = Hardware.HumiditySetpoint.parse_timeseries(expr_pairs)

        # Return the timeseries to the client for plotting
        return jsonify({'time': time_s, 'values': values})
    # if request.method == 'GET':
    #     jsonify({'time': time_s.tolist(), 'values': values.tolist()})

@app.route('/get_current_control', methods=['GET'])
def get_current_control():
    return jsonify({'control_mode': CONTROL_DATA['mode'], 'control_params': CONTROL_DATA['params']}), 200

@app.route('/set_control', methods=['POST'])
async def set_control():
    requestData = request.get_json()

    # Set the control scheme
    CONTROL_DATA['mode'] = requestData['controlMode']
    # Record the parameters
    CONTROL_DATA['params'] = requestData['params']
    logging.info(f"[SET]Control mode: {CONTROL_DATA['mode']} \n{'':20}[SET]Control params: {CONTROL_DATA['params']}")

    message = ""
    # Set the MFCs control behavior, depending on the control scheme
    if CONTROL_DATA['mode'] == 'MAN':
        daq_instances['humidity_setpoint'].disable()    #Disable the setpoint control
        # Check if each of the control parameters are not blank
        if CONTROL_DATA['params']['MFC1'] == '' or CONTROL_DATA['params']['MFC2'] == '':
            return jsonify({'success': False, 'message': 'MFC flow rate(s) blank'}), 400

        # Parse the control parameters as floats
        CONTROL_DATA['params'] = {key: float(val) for key, val in CONTROL_DATA['params'].items()}
        
        # Ensure the flow rates are within the limits.  If not, set them to the limits
        CONTROL_DATA['params']['MFC1'] = max(0, min(100, CONTROL_DATA['params']['MFC1']))
        CONTROL_DATA['params']['MFC2'] = max(0, min(100, CONTROL_DATA['params']['MFC2']))
        logging.info(f"Setting MFCs to {CONTROL_DATA['params']['MFC1']} and {CONTROL_DATA['params']['MFC2']}")

        # Set the MFCs flow rates by adding it to the command queue to be handled by the hardware loop
        hg.add_flask_command( daq_instances['MFC1'].set_flow_rate, 
                             {'flow_rate': CONTROL_DATA['params']['MFC1']} )
        hg.add_flask_command( daq_instances['MFC2'].set_flow_rate, 
                             {'flow_rate': CONTROL_DATA['params']['MFC2']} )

        message = "MFCs set to manual control"
        return jsonify({'success': True, 'message': message, 
                    'control_mode': CONTROL_DATA['mode'], 'control_params': CONTROL_DATA['params']}), 200

    elif CONTROL_DATA['mode'] == 'SPT':
        # Check if each of the control parameters are not blank
        if CONTROL_DATA['params']['flowRate'] == '' or CONTROL_DATA['params']['humidity'] == '':
            return jsonify({'success': False, 'message': 'Setpoint(s) blank'}), 400
        
        # Parse the control parameters as floats
        CONTROL_DATA['params'] = {key: float(val) for key, val in CONTROL_DATA['params'].items()}
        # Ensure the flow rates are within the limits.  If not, set them to the limits
        CONTROL_DATA['params']['flowRate'] = max(0, min(100, CONTROL_DATA['params']['flowRate']))
        CONTROL_DATA['params']['humidity'] = max(0, min(100, CONTROL_DATA['params']['humidity']))   

        # Set the setpoints for the control loop
        daq_instances['humidity_setpoint'].set_setpoint(CONTROL_DATA['params']['humidity'])
        daq_instances['humidity_setpoint'].enable()


        message = "MFCs set to setpoint control"
        return jsonify({'success': True, 'message': message, 
                    'control_mode': CONTROL_DATA['mode'], 'control_params': CONTROL_DATA['params']}), 200

    elif CONTROL_DATA['mode'] == 'ARB':
        #Remove the empty sections
        CONTROL_DATA['params']['segments'] = [sect for sect in CONTROL_DATA['params']['segments'] if sect['segmentString'] != '' or sect['duration'] != ''] 
        # Set the expression-duration pairs as the control parameters
        CONTROL_DATA['params']['segments'] = [ (sect['segmentString'], float(sect['duration'])) for sect in CONTROL_DATA['params']['segments'] ]     

        CONTROL_DATA['params']['flowRate'] = max(0, min(100, float(CONTROL_DATA['params']['flowRate'])))
        message = "MFCs set to arbitrary control"

        # Set the setpoint flow rates for the MFCs
        time_s, values = Hardware.HumiditySetpoint.parse_timeseries(CONTROL_DATA['params']['segments'])
        CONTROL_DATA['params']['time_s'] = time_s
        CONTROL_DATA['params']['values'] = values

        # Set the setpoints for the control loop
        daq_instances['humidity_setpoint'].set_setpoint(values, time_s)
    
        return jsonify({'success': True, 'message': message, 
                        'control_mode': CONTROL_DATA['mode'], 
                        'control_params': CONTROL_DATA['params'], 
                        'time': CONTROL_DATA['params']['time_s'], 
                        'values': CONTROL_DATA['params']['values']}), 200

@app.route('/')
def index():
    return render_template('index.html')

######################
### Hardware run loop
######################

async def run_loop():
    # Setup

    # Looping
    while True:
        t0 = time.time()
        # Check for commands from the Flask app and handle them
        if not hg.flask_command_queue.empty():
            await hg.run_flask_commands()
        
        # Query data from all components (DAQs)
        # Exclude SHT1 and humidity_setpoint, if using control loop.  These
        # are fetched in the control loop
        exclude = []
        if daq_instances['humidity_setpoint'].is_enabled:
            exclude = ['SHT1', 'humidity_setpoint']
        await hg.fetch_data(exclude=exclude)

        # Control loop
        if daq_instances['humidity_setpoint'].is_enabled:
            # Get the setpoint of the control scheme
            setpoint = (await daq_instances['humidity_setpoint'].fetch_data())['values']['humidity_setpoint']
            daq_instances['humidity_setpoint'].pid.setpoint = setpoint

            # Compute new output from the PID according to the system's current value
            current_humidity = await daq_instances['SHT1'].fetch_data()
            if current_humidity == False:
                logging.error("SHT1 DISCONNECTED, CANNOT RUN CONTROL LOOP")
                continue
            else:
                current_humidity = current_humidity['value']['humidity']
            
            # Get the controller output to send to the plant (MFCs)
            # This value defines the ratio of the MFC flow rates
            control = daq_instances['humidity_setpoint'].pid(current_humidity)

            # Set the MFCs
            total_flow = CONTROL_DATA['params']['flowRate']
            await daq_instances['MFC1'].set_flow_rate( total_flow*(1-control) )
            await daq_instances['MFC2'].set_flow_rate( total_flow*control     )

        # Calculate how much to delay, limit the delay to 0s, can't have negative delay
        delay = (1/HARDWARE_LOOP_FREQ_HZ) - (time.time()-t0)
        await asyncio.sleep(max(0, delay))

# Start the Flask app and hardware loop
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
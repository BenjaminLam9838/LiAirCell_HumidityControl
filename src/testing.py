import numpy as np
import sympy as sp

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
        print(expr, duration)
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


exprdur = [('sin(4*t)', 5),
            ('sin(2*t)', 3),
            ('2',2),
            ('5',3)]
parse_timeseries(exprdur)

# Create instances of the hardware components (Data aquisition components)
# daq_instances = {
#     'test1': Hardware.DummyDAQ(1),
#     'test2': Hardware.DummyDAQ(0.5),
#     'test3': Hardware.DummyDAQ(0.03),
# }

# hg = Hardware.HardwareGroup(daq_instances, 10)
# for x in range(14):
#     asyncio.run(hg.fetch_data())
# for daq in daq_instances.keys():
#     print(f"{daq}: {len(hg.get_list(daq))}")


# async def data_generator():
#     while True:
        # for mfc in mfc_instances.values():
        #     await mfc.fetch_data()
#         await asyncio.sleep(0.3)

# def start_data_generator():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(data_generator())

# data_thread = threading.Thread(target=start_data_generator)
# data_thread.daemon = True  # Daemonize the thread (optional, depends on your use case)
# data_thread.start()  # Start the thread


# while True:
#     for mfc in mfc_instances.values():
#         print(mfc.pop_data_queue())
#     time.sleep(1)

# port = '/dev/cu.usbserial-AU057C72'


# MFC1 = MFC()
# print(asyncio.run(MFC1.connect(port)))

# # Create a thread to generate data
# async def data_generator():
#     while True:
#         await MFC1.fetch_data()
#         await asyncio.sleep(0.5)

# # Function to start the asyncio loop in a separate thread
# def asyncio_loop_thread():        
#     asyncio.set_event_loop(asyncio.new_event_loop())
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(data_generator())

# # Function to start the asyncio loop in a separate thread
# def start_asyncio_loop():
#     logging.debug("Starting new asyncio loop thread.")
#     thread_id = uuid.uuid4()
#     loop_thread = threading.Thread(target=asyncio_loop_thread, name=str(thread_id))
#     loop_thread.daemon = True
#     loop_thread.start()

# start_asyncio_loop()

# while True:
#     print(MFC1.pop_data_queue())
#     time.sleep(1)


# comp1 = Component()
# # asyncio.run(comp1.fetch_data())
# # asyncio.run(comp1.fetch_data())
# # asyncio.run(comp1.fetch_data())
# # print(comp1.pop_data_queue())
# # print(comp1.pop_data_queue())

# async def data_generator():
#     while True:
#         await comp1.fetch_data()
#         await asyncio.sleep(0.3)

# def start_data_generator():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(data_generator())

# data_thread = threading.Thread(target=start_data_generator)
# data_thread.daemon = True  # Daemonize the thread (optional, depends on your use case)
# data_thread.start()  # Start the thread


# while True:
#     print(comp1.pop_data_queue())
#     time.sleep(1)
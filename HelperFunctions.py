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


# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 12:49:08 2024

@author: 20182785
"""

# cardiac_output_calculator.py

import numpy as np

def calculate_cardiac_output(flow_aortic_valve, time_points, cycle_times, n_beats):
    """
    Function to calculate cardiac output for each beat.

    Parameters:
    flow_aortic_valve (ndarray): Array of aortic flow values.
    time_points (ndarray): Array of time points corresponding to flow values.
    cycle_times (list): List of cycle times for each beat.
    n_beats (int): Number of heartbeats.

    Returns:
    list: A list of calculated cardiac output values for each beat.
    """
    timer = 0
    cardiac_output_values = []  # List to store cardiac output values
    
    # Initialize array for stroke volume and cardiac output saving
    list_cycle_times = cycle_times[1:]  # Exclude the first 0
    
    for i in range(n_beats):
        cycle_time = cycle_times[i+1]*1e3  # cycle time for beat i [ms]
        
        # Determine indices needed to slice the volume array for one beat
        start_index = int(timer/2)
        end_index = int((timer + cycle_time)/2)
        
        aortic_flow_i = flow_aortic_valve[start_index:end_index]
        time_points_i = time_points[start_index:end_index]
        stroke_volume_i = np.trapezoid(aortic_flow_i, time_points_i) * 1e3  # mL
        
        heart_rate_i = 60 / list_cycle_times[i]
        
        cardiac_output_i = stroke_volume_i * heart_rate_i  # mL/min
        
        # Store the cardiac output in the list
        cardiac_output_values.append(cardiac_output_i)
        
        # Set timer to next beat
        timer += cycle_time
    
    return cardiac_output_values

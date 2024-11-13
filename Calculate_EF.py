# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 13:06:38 2024

@author: 20182785
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 12:49:08 2024

@author: 20182785
"""

# cardiac_output_calculator.py

import numpy as np

def calculate_ejection_fraction(flow_aortic_valve, time_points, cycle_times, n_beats, V_lv):
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
    EF_values = []  # List to store cardiac output values
    
    for i in range(n_beats):
        cycle_time = cycle_times[i+1]*1e3  # cycle time for beat i [ms]
        
        # Determine indices needed to slice the volume array for one beat
        start_index = int(timer/2)
        end_index = int((timer + cycle_time)/2)
        
        aortic_flow_i = flow_aortic_valve[start_index:end_index]
        V_lv_i = V_lv[start_index:end_index]
        EDV = np.max(V_lv_i)
        time_points_i = time_points[start_index:end_index]
        stroke_volume_i = np.trapezoid(aortic_flow_i, time_points_i) * 1e6  # L
        
        EF_i = stroke_volume_i/EDV
        
        # Store the cardiac output in the list
        EF_values.append(EF_i)
        
        # Set timer to next beat
        timer += cycle_time
    
    return EF_values

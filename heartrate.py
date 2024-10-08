import numpy as np

def calculate_networktriggers(n_beats, t_cycle, mean, delta_hr, breathing_ratios):
    # Ensure the ratios sum to 1
    assert sum(breathing_ratios) == 1, "Ratios must sum to 1"
    
    # Calculate the time segments based on ratios
    T = n_beats * t_cycle         # time for the entire period (one breathing cycle)
    
    t1 = breathing_ratios[0] * T  # time for the increasing part
    t2 = breathing_ratios[1] * T  # time for the decreasing part
    t3 = breathing_ratios[2] * T  # time for the constant part
    
    # Define min and max values
    min_val = mean - delta_hr / 2
    max_val = mean + delta_hr / 2
    
    # Sample heart rates based on the generated heart rate function 
    sample_times = np.array([])
    samples_HR = np.array([])
    cycle_times = np.array([])

    time = 0
    cycle_times = np.array([0])
    while time <= T:
        sample_times = np.append(sample_times, time) 
        sampled_HR = np.piecewise(time, 
                                   [time < t1, 
                                    (time >= t1) & (time < t1 + t2), 
                                    time >= t1 + t2], 
                                   [lambda time: min_val + (max_val - min_val) * (time / t1),
                                    lambda time: max_val - (max_val - min_val) * ((time - t1) / t2),
                                    lambda time: min_val])
        
        samples_HR = np.append(samples_HR, sampled_HR)

        cycle_time = 60 / sampled_HR  # Calculate cycle time based on heart rate
        cycle_times = np.append(cycle_times, cycle_time)
        time += cycle_time
        
    return cycle_times

cycle_times = calculate_networktriggers(5, 0.8, 75, 12, [0.375,0.375,0.25])
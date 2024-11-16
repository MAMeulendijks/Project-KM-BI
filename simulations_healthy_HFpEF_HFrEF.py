import matplotlib.pyplot as plt
import numpy as np
from cardiac_calculations import CardiacCalculator
from plot_functions import HemodynamicPlotter
from _model_thorax import VanOsta2024_Breathing_Thorax

plt.close('all')

# Load model including the thorax
model = VanOsta2024_Breathing_Thorax()

# Heartrate variability (HRV) setup
include_hrv = 'on'  # Choose from 'on', 'off', 'inversed'

if include_hrv == 'on':
    cycle_times = [0, 0.857, 0.789, 0.732, 0.789, 0.857]  # Set mechanical triggers for sinus rhythm
elif include_hrv == 'inversed':
    cycle_times = [0, 0.750, 0.811, 0.882, 0.811, 0.750]
elif include_hrv == 'off':
    cycle_times = [0, 0.8, 0.8, 0.8, 0.8, 0.8]

# Calculate the length of the breathing cycle
breath_cycle_time = np.cumsum(cycle_times)[-1]
n_beats = len(cycle_times)-1

# Add components for mechanical triggers based on the number of beats
for i in range(n_beats):
    model.add_component('NetworkTrigger', str(i), 'Network.Ra')

# Set the start of mechanical triggers 
model['NetworkTrigger']['time'] = np.cumsum(cycle_times[0:-1])

# Run the model in a hemodynamically stable state
model['Solver']['store_beats'] = 2
model['General']['t_cycle'] = breath_cycle_time / (len(cycle_times)-1)  # calculate mean cycle time
model['Thorax']['p_ref'] = 0e3  # Turn off pericardial function
model['Thorax']['p_max'] = 0e3  # Turn off thorax for hemodynamic stability

# Define the states for comparison
states = ['Healthy', 'HFrEF', 'HFpEF']
CO_results = {'Healthy': [], 'HFrEF': [], 'HFpEF': []}
LA_pressure_results = {'Healthy': [], 'HFrEF': [], 'HFpEF': []}

# Loop through each state, simulate, and calculate cardiac output (CO)
for state in states:
    if state == 'HFrEF':
        model['Patch']['Sf_act'][['pLv0','pSv0']] *= 0.46  # Adjust for HFrEF
    elif state == 'HFpEF':
        model['Patch']['k1'][['pLv0', 'pSv0']] *= 1.96  # Adjust for HFpEF
    else:
        pass  # Healthy state, no adjustments

    # Run the model until stable
    model.run(stable=True)

    # Deactivate pressure-flow control and reset the cycle time for each state
    model['General']['t_cycle'] = breath_cycle_time
    model['PFC']['is_active'] = False

    # Run the model without breathing cycle for calculation
    model.run(10)

    # Calculate cardiac parameters
    V_lv = model['Cavity']['V'][:, 'cLv'] * 1e6  # Convert to microliters
    flow_aortic_valve = model['Valve']['q'][:, 'LvSyArt']
    flow_pulmonary_valve = model['Valve']['q'][:, 'RvPuArt']
    time_points = model['Solver']['t']
    LA_pressure = model['Patch']['Sf'][:, 'pLa0']*1e-3

    calculator = CardiacCalculator(time_points, cycle_times, n_beats, V_lv)

    # Calculate cardiac output (CO) for both aortic and pulmonary circulation
    aortic_CO = calculator.calculate_CO(flow_aortic_valve)
    pulmonary_CO = calculator.calculate_CO(flow_pulmonary_valve)
    results_LA_pressure = calculator.calculate_LA_pressure(LA_pressure)
    

    # Store results for plotting
    CO_results[state] = {
        'aortic': aortic_CO,
        'pulmonary': pulmonary_CO
    }
    
    LA_pressure_results[state] = results_LA_pressure
    
    print(f"CO for {state} calculated.")
    
max_pressure_healthy= np.max(LA_pressure_results['Healthy'])
max_pressure_HFrEF = np.max(LA_pressure_results['HFrEF'])
max_pressure_HFpEF = np.max(LA_pressure_results['HFpEF']) 

# Now, calculate the max LA pressure after all states are processed
max_LA_pressure = {
    'Healthy': max_pressure_healthy,
    'HFrEF': max_pressure_HFrEF,
    'HFpEF': max_pressure_HFpEF
}

std_pressure_healthy = np.std(LA_pressure_results['Healthy'])
std_pressure_HFrEF = np.std(LA_pressure_results['HFrEF'])
std_pressure_HFpEF = np.std(LA_pressure_results['HFpEF'])

# Store the variability results as a dictionary
std_LA_pressure = {
    'Healthy': std_pressure_healthy,
    'HFrEF': std_pressure_HFrEF,
    'HFpEF': std_pressure_HFpEF
}
# Remove any NaN values from the results
valid_states = [state for state, value in max_LA_pressure.items() if not np.isnan(value)]
valid_pressures = [max_LA_pressure[state] for state in valid_states]
valid_pressures_std = [std_LA_pressure[state] for state in valid_states]

plotter = HemodynamicPlotter(model, cycle_times, n_beats, breath_cycle_time)
#%% Compare aortic CO's
plotter.compare_CO_3bars(CO_results['Healthy']['aortic'], CO_results['HFrEF']['aortic'],CO_results['HFpEF']['aortic'], "Comparison of Aortic Cardiac Output", "Cardiac Output (L/min)")
plotter.compare_CO_3bars(CO_results['Healthy']['pulmonary'], CO_results['HFrEF']['pulmonary'],CO_results['HFpEF']['pulmonary'], "Comparison of Pulmonary Cardiac Output", "Cardiac Output (L/min)")
plotter.compare_pressure_3bars(LA_pressure_results['Healthy'], LA_pressure_results['HFrEF'], LA_pressure_results['HFpEF'], "Comparison of Left Atrial Pressure", "Pressure (??)")
plotter.compare_pressure_3bars(valid_pressures[0],valid_pressures[1],valid_pressures[2],"Comparison of Max Left Atrial Pressure","Pressure (??)")
plotter.compare_pressure_3bars(valid_pressures_std[0], valid_pressures_std[1], valid_pressures_std[2], "Comparison of Left Atrial Pressure Variability", "Pressure Variability (mmHg)")


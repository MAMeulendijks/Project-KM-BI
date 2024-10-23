import matplotlib.pyplot as plt
import numpy as np
import time
from calculate_CO import calculate_cardiac_output
from plot_function import plot_overview

from _model_thorax import VanOsta2024_Breathing_Thorax
plt.close('all')


# %% load model including the thorax
model = VanOsta2024_Breathing_Thorax()

include_hrv = 'on'    # on, off, or inversed

# %% Set mechanical triggers to start from the RA (reflecting sinus rhythm)

if include_hrv == 'on':
    cycle_times = [0, 0.857, 0.789, 0.732, 0.789, 0.857]
elif include_hrv == 'inversed':
    cycle_times = [0, 0.750, 0.811, 0.882, 0.811, 0.750]
elif include_hrv == 'off':
    cycle_times = [0, 0.8, 0.8, 0.8, 0.8, 0.8]

# calculate length of breathing cycle
breath_cycle_time = np.cumsum(cycle_times)[-1]
n_beats = len(cycle_times)-1

for i in range(n_beats):
    model.add_component('NetworkTrigger', str(i), 'Network.Ra')
    
# Set the start of mechanical triggers (in this case, constant sinus rhythm with no HR variability) 
model['NetworkTrigger']['time'] = np.cumsum(cycle_times[0:-1])



# %% Run hemodynamically stable to ensure 'fair' starting point
model['Solver']['store_beats'] = 2
model['General']['t_cycle'] = breath_cycle_time / (len(cycle_times)-1)   # calculate mean cycle time
model['Thorax']['p_ref'] = 0e3 # turn off pericardial function
model['Thorax']['p_max'] = 0e3 # turn off thorax for hemodynamic stability

model.run(stable=True)

# set time to simulate back to inital values, and deactivate pressure flow control
model['General']['t_cycle'] = breath_cycle_time
model['PFC']['is_active']=False

# %% run the model without breathing cycle
model.run(2)
#model.plot(plt.figure(1, clear=True))

#%%  Calculate cardiac output - no breathing

flow_aortic_valve = model['Valve']['q'][:,'LvSyArt'] 
flow_pulmonary_valve = model['Valve']['q'][:,'RvPuArt'] 
time_points = model['Solver']['t']
list_cycle_times = cycle_times[1:]

aortic_CO_no_breathing = calculate_cardiac_output(flow_aortic_valve, time_points, cycle_times, n_beats)
pulmonary_CO_no_breathing = calculate_cardiac_output(flow_pulmonary_valve, time_points, cycle_times, n_beats)

# %% Plot hemodynamic signals of interest - NO breathing
plot_overview(model, cycle_times, n_beats, breath_cycle_time, aortic_CO_no_breathing, pulmonary_CO_no_breathing)

# %% Parameterize thorax
model['Thorax']['dt'] = 0
model['Thorax']['p_max'] = -0.2666e3  # 2 mmHg is the amplitude 
model['Thorax']['tr'] = (breath_cycle_time/np.pi)   # no pause

# %% Run the model with breathing
model.run(2)

#%%  Calculate cardiac output - breathing
flow_aortic_valve = model['Valve']['q'][:,'LvSyArt'] 
flow_pulmonary_valve = model['Valve']['q'][:,'RvPuArt'] 
time_points = model['Solver']['t']
list_cycle_times = cycle_times[1:]

aortic_CO_breathing = calculate_cardiac_output(flow_aortic_valve, time_points, cycle_times, n_beats)
pulmonary_CO_breathing = calculate_cardiac_output(flow_pulmonary_valve, time_points, cycle_times, n_beats)


# %% Plot hemodynamic signals of interest - breathing
plot_overview(model, cycle_times, n_beats, breath_cycle_time, aortic_CO_breathing, pulmonary_CO_breathing)

#%% compare aortic CO's

# Define bar width and positions for the side-by-side comparison
bar_width = 0.35
index = np.arange(n_beats)

# Create the figure
plt.figure(3, figsize=(10, 6))

# Plot the two sets of data with custom colors
plt.bar(index, aortic_CO_no_breathing, bar_width, label='No Breathing', color='#1a2c5c')
plt.bar(index + bar_width, aortic_CO_breathing, bar_width, label='Breathing', color='#c43c70')

# Add labels, title, and legend
plt.xlabel('Beat Number', fontsize=12)
plt.ylabel('Cardiac Output (L/min)', fontsize=12)
plt.title('Comparison of aortic Cardiac Output for Each Beat', fontsize=14, fontweight='bold')

# Set x-ticks and y-axis limit
plt.xticks(index + bar_width / 2, range(1, n_beats+1))
plt.ylim(0, 7)  # Set y-axis maximum to 7

# Add a grid for better readability
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Add legend
plt.legend()

# Show the plot with a tight layout
plt.tight_layout()
plt.show()

#%% compare pulmonary CO's

# Define bar width and positions for the side-by-side comparison
bar_width = 0.35
index = np.arange(n_beats)

# Create the figure
plt.figure(4, figsize=(10, 6))

# Plot the two sets of data with custom colors
plt.bar(index, pulmonary_CO_no_breathing, bar_width, label='No Breathing', color='#1a2c5c')
plt.bar(index + bar_width, pulmonary_CO_breathing, bar_width, label='Breathing', color='#c43c70')

# Add labels, title, and legend
plt.xlabel('Beat Number', fontsize=12)
plt.ylabel('Cardiac Output (L/min)', fontsize=12)
plt.title('Comparison of pulmonary Cardiac Output for Each Beat', fontsize=14, fontweight='bold')

# Set x-ticks and y-axis limit
plt.xticks(index + bar_width / 2, range(1, n_beats+1))
plt.ylim(0, 7)  # Set y-axis maximum to 7

# Add a grid for better readability
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Add legend
plt.legend()

# Show the plot with a tight layout
plt.tight_layout()
plt.show()

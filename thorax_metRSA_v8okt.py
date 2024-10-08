import matplotlib.pyplot as plt
import numpy as np
import time
from heartrate import calculate_networktriggers

from _model_thorax import VanOsta2024_Breathing_Thorax
plt.close('all')
# %% determine how long you want to simulate (in this case, 2 breaths of 5 times a cardiac cycle of 0.8 sec)
n_beats = 5
t_cycle = 0.8       # 75 beats per minute
n_cycle = 2         # number of breathing cycles

# generate dictionary for saving the output of interest
output = {
    "No Breathing": {
        "LV": {"SV": [], "CO": []},
        "RV": {"SV": [], "CO": []}
    },
    "Breathing": {
        "LV": {"SV": [], "CO": []},
        "RV": {"SV": [], "CO": []}
    }
}

# %% Some other constants for simulating HR variability
include_hrv = True      
mean_hr = 75            # mean heart rate
delta_hr = 12           # increase of heart rate from max exhalation to max inspiration
breathing_ratios = [0.375,0.375,0.25]   # inhale:exhale:pause = 3:3:2

# %% Make model including the thorax and set the time to be simulated 
model = VanOsta2024_Breathing_Thorax()
model['General']['t_cycle'] = n_beats*t_cycle

# %% Set mechanical triggers to start from the RA (reflecting sinus rhythm)
for i in range(n_beats):
    model.add_component('NetworkTrigger', str(i), 'Network.Ra')
    
# Set the start of mechanical triggers (with or without HR variability) 
if include_hrv == False:
    
    # create array with cycle times for the calculation of the network trigger times
    cycle_times = np.array([0])     # first value has to be 0
    for i in range(n_beats):
        cycle_times = np.append(cycle_times, t_cycle)       
        
    model['NetworkTrigger']['time'] = np.cumsum(cycle_times[0:n_beats])
    model['General']['t_cycle'] = model['NetworkTrigger']['time'][-1] + 1
    
else:
    # calculate specific cycle times with HR variability
    cycle_times = calculate_networktriggers(n_beats, t_cycle, mean_hr, delta_hr, breathing_ratios)
    
    model['NetworkTrigger']['time'] = np.cumsum(cycle_times[0:n_beats])     
    model['General']['t_cycle'] = model['NetworkTrigger']['time'][-1] + 1
        

# %% Run hemodynamically stable to ensure 'fair' starting point
model['Solver']['store_beats'] = n_cycle
model['General']['t_cycle'] = t_cycle
model['Thorax']['p_ref'] = 0e3 # turn off pericardial function
model['Thorax']['p_max'] = 0e3 # turn off thorax for hemodynamic stability

model.run(stable=True)

# calculate length of breathing cycle depending on last trigger time and last cycle time 
# to ensure full last beat with the correct cycle time
model['General']['t_cycle'] = model['NetworkTrigger']['time'][-1] + cycle_times[-1] 
# and deactivate pressure flow control
model['PFC']['is_active'] = False

# %% run the model without breathing cycle and plot hemodynamics
model.run(n_cycle)
model.plot(plt.figure(1, clear=True))

# Calculate cardiac output per beat for RV and LV 
volumes = model['Cavity']['V'][:, ['cLv', 'cRv']]*1e6
V_lv, V_rv = volumes.T

# initialize arrays for stroke volume and cardiac output saving
timer = 0

for i in range(n_beats):
    cycle_time = cycle_times[i+1]*1e3  # cycle time for beat i [ms]
    
    # determine indices needed to slice the volume array for one beat
    start_index = int(timer/2)
    end_index = int((timer + cycle_time)/2)
    
    Vlv = V_lv[start_index:end_index]
    Vrv = V_rv[start_index:end_index]
    
    # calculate stroke volumes for LV and RV and add to dictionary
    SV_lv = max(Vlv) - min(Vlv)
    SV_rv = max(Vrv) - min(Vrv)
    
    output["No Breathing"]["LV"]["SV"].append(SV_lv.round(3))
    output["No Breathing"]["RV"]["SV"].append(SV_rv.round(3))
    
    # calculate cardiac outputs for LV and RV per beat and add to dictionary
    CO_lv = SV_lv*1e-3*(60/(cycle_time*1e-3))
    CO_rv = SV_rv*1e-3*(60/(cycle_time*1e-3))
    
    output["No Breathing"]["LV"]["CO"].append(CO_lv.round(3))
    output["No Breathing"]["RV"]["CO"].append(CO_rv.round(3))
    
    # set timer to next beat
    timer += cycle_time

# %% Parameterize thorax
model['Thorax']['dt'] = 0
model['Thorax']['p_max'] = -0.2666e3    # 2 mmHg is the amplitude so 0.2666e3 Pa
model['Thorax']['tr'] = (2/np.pi)*(n_beats*t_cycle*breathing_ratios[0])


# %% Run breathing cycle

model.run(n_cycle)
model.plot(plt.figure(2, clear=True))

# plot intrathoracic pressure curve
plt.figure(3)
plt.plot(model['Solver']['t']*1e3, model['Thorax']['p'][:, 0] / 133)
plt.xlabel('Time [ms]', fontsize = 12)
plt.ylabel('Pressure [mmHg]', fontsize=12)
plt.title('Intrathoracic pressure during breathing', fontweight='bold')

#  Calculate cardiac output per beat for RV and LV for the first breathing cycle

volumes = model['Cavity']['V'][:, ['cLv', 'cRv']]*1e6
V_lv, V_rv = volumes.T

# initialize arrays for stroke volume and cardiac output saving
timer = 0

for i in range(n_beats):
    cycle_time = cycle_times[i+1]*1e3  # cycle time for beat i [ms]
    
    # determine indices needed to slice the volume array for one beat
    # NOTE: stored dt interval is 2 ms so divide by 2 to determine indices
    start_index = int(timer/2)
    end_index = int((timer + cycle_time)/2)
    
    Vlv = V_lv[start_index:end_index]
    Vrv = V_rv[start_index:end_index]
    
    # calculate stroke volumes for LV and RV and add to dictionary
    SV_lv = max(Vlv) - min(Vlv)
    SV_rv = max(Vrv) - min(Vrv)
    
    output["Breathing"]["LV"]["SV"].append(SV_lv.round(3))
    output["Breathing"]["RV"]["SV"].append(SV_rv.round(3))
    
    # calculate cardiac outputs for LV and RV per beat and add to dictionary
    CO_lv = SV_lv*1e-3*(60/(cycle_time*1e-3))
    CO_rv = SV_rv*1e-3*(60/(cycle_time*1e-3))
    
    output["Breathing"]["LV"]["CO"].append(CO_lv.round(3))
    output["Breathing"]["RV"]["CO"].append(CO_rv.round(3))
    
    # set timer to next beat
    timer += t_cycle


# %% bar plots of cardiac outputs

x = np.array([1,2,3,4,5])
width = 0.40
  
# plot data in grouped manner of bar type 
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Plot the first subplot (simulation without breathing)
axes[0].bar(x - (0.5 * width), output["No Breathing"]["LV"]["CO"], width, color='#1a2c5c')
axes[0].bar(x + (0.5 * width), output["No Breathing"]["RV"]["CO"], width, color='#c43c70')
axes[0].set_xlabel("Beat number")
axes[0].set_ylabel("Cardiac output [L / min]")
axes[0].legend(["LV", "RV"])
axes[0].set_title("Cardiac output without breathing", fontweight='bold')
axes[0].set_ylim(0, 8)

# Plot the second subplot  (simulation with breathing)
axes[1].bar(x - (0.5 * width), output["Breathing"]["LV"]["CO"], width, color='#1a2c5c')
axes[1].bar(x + (0.5 * width), output["Breathing"]["RV"]["CO"], width, color='#c43c70')
axes[1].set_xlabel("Beat number")
axes[1].set_ylabel("Cardiac output [L / min]")
axes[1].legend(["LV", "RV"])
axes[1].set_title("Cardiac output with breathing", fontweight='bold')
axes[1].set_ylim(0, 8)

plt.show()




    

    



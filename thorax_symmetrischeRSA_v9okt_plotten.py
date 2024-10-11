import matplotlib.pyplot as plt
import numpy as np
import time

from _model_thorax import VanOsta2024_Breathing_Thorax
plt.close('all')


# %% load model including the thorax
model = VanOsta2024_Breathing_Thorax()

include_hrv = True

# %% Set mechanical triggers to start from the RA (reflecting sinus rhythm)

if include_hrv == True:
    cycle_times = [0, 0.857, 0.789, 0.732, 0.789, 0.857]
else:
    cycle_times = [0, 0.8, 0.8, 0.8, 0.8, 0.8]

# calculate length of breathing cycle
breath_cycle_time = np.cumsum(cycle_times)[-1]

for i in range(len(cycle_times)-1):
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

# %% run the model without breathing cycle and plot hemodynamics
model.run(2)
#model.plot(plt.figure(1, clear=True))

# %% Parameterize thorax
model['Thorax']['dt'] = 0
model['Thorax']['p_max'] = -0.2666e3  # 2 mmHg is the amplitude 
model['Thorax']['tr'] = (2/np.pi)*(1/2)*breath_cycle_time   # no pause

# Run for one cycle to get steady state

# Define colors
color1 = '#00BFFF'  # Light blue
color2 = '#00008B'  # Dark blue
color3 = 'cyan'
color4 = '#8B0000'  # Dark red
color5 = 'red'  # Firebrick
color6 = 'orange'  # Indian red

# Create a figure with a 4x2 grid layout to accommodate the new plot
fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, figsize=(10, 10))  # Adjust figsize as needed

# Right Heart Volume Plot: Right Atrium and Right Ventricle
ax1.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['V'][:, 'Ra'] * 1e6, 
         label="Right Atrium", color=color1)

ax1.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['V'][:, 'cRv'] * 1e6, 
         label="Right Ventricle", color=color2)

ax1.set_ylim(0, 125)
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Volume [ml]')
ax1.set_title('Right Heart', fontweight='bold')
ax1.legend()

# Left Heart Volume Plot: Left Atrium and Left Ventricle
ax2.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['V'][:, 'La'] * 1e6, 
         label="Left Atrium", color=color4)

ax2.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['V'][:, 'cLv'] * 1e6, 
         label="Left Ventricle", color=color5)

ax2.set_ylim(0, 125)
ax2.set_xlabel('Time [ms]')
ax2.set_ylabel('Volume [ml]')
ax2.set_title('Left Heart', fontweight='bold')
ax2.legend()

# Right Heart Pressure Plot: Right Atrium, Right Ventricle, Pulmonary Artery
ax3.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['p'][:, 'Ra'] / 133, 
         label="Right Atrium", color=color1)

ax3.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['p'][:, 'cRv'] / 133, 
         label="Right Ventricle", color=color2)

ax3.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['p'][:, 'PuArt'] / 133, 
         label="Pulmonary Artery", color=color3)

ax3.set_ylim(0, 125)
ax3.set_xlabel('Time [ms]')
ax3.set_ylabel('Pressure [mmHg]')
ax3.legend()

# Left Heart Pressure Plot: Left Atrium, Left Ventricle, Aorta
ax4.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['p'][:, 'La'] / 133, 
         label="Left Atrium", color=color4)

ax4.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['p'][:, 'cLv'] / 133, 
         label="Left Ventricle", color=color5)

ax4.plot(model['Solver']['t'] * 1e3, 
         model['Cavity']['p'][:, 'SyArt'] / 133, 
         label="Aorta", color=color6)

ax4.set_ylim(0, 125)
ax4.set_xlabel('Time [ms]')
ax4.set_ylabel('Pressure [mmHg]')
ax4.legend()

# Thorax Pressure Plot
ax5.plot(model['Solver']['t'] * 1e3, model['Thorax']['p'][:, 0] / 133)
ax5.grid(True)
ax5.set_xlabel('Time [ms]')
ax5.set_ylabel('Pressure relative to atmospheric pressure [mmHg]')
ax5.set_title('Thorax Pressure')

V_lv = model['Cavity']['V'][:, 'cLv']*1e6
p_lv = model['Cavity']['p'][:, 'cLv']*7.5e-3

# Left Ventricle Pressure-Volume Loop
ax6.plot(V_lv, p_lv, label='LV')
ax6.set_xlabel('Volume (ml)')
ax6.set_ylabel('Pressure (mmHg)')
ax6.set_title('Left Ventricle Pressure-Volume Loop')
ax6.legend()

amount = model['Solver']['store_beats']
bpm_values = [60 / cycle_time for cycle_time in cycle_times[1:]] 
bpm_values_repeated = bpm_values * amount 
single_cycle_time_points = np.cumsum(cycle_times[1:]) * 1e3  # Convert to milliseconds
time_points = np.concatenate([single_cycle_time_points + (i * breath_cycle_time * 1e3) 
                              for i in range(amount)])  # Adjust time points for each beat repetition

# Plot the BPM values against the calculated time points
ax7.plot(time_points, bpm_values_repeated, label="Interpolated BPM over time", color='blue')
ax7.grid(True)
ax7.set_xlabel('Time (ms)')
ax7.set_ylabel('BPM')
ax7.set_title('Heart rate over time')
ax7.legend()
# Remove empty subplot (ax8)
fig.delaxes(ax8)

# Adjust layout for better spacing
plt.tight_layout()

manager = plt.get_current_fig_manager()
manager.window.setGeometry(500, 100, 900, 900)
# Show the figure
plt.show()



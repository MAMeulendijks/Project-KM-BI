# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:27:15 2024

@author: 20182785
"""

import matplotlib.pyplot as plt 
import numpy as np
from _model_thorax import VanOsta2024_Breathing_Thorax
import circadapt

# Close any previous figures
plt.close('all')

# Determine how long you want to simulate (in this case, 10 times a cardiac cycle of 0.85 sec)
n_beats = 5
t_cycle = 0.8

# Make model including the thorax and set the time to be simulated 
model_thorax = VanOsta2024_Breathing_Thorax()
model_thorax['General']['t_cycle'] = n_beats * t_cycle

# Set mechanical triggers to start from the RA (reflecting sinus rhythm)
for i in range(n_beats):
    model_thorax.add_component('NetworkTrigger', str(i), 'Network.Ra')

# Set the start of mechanical triggers
model_thorax['NetworkTrigger']['time'] = np.cumsum([0, 0.8, 0.8, 0.8, 0.8])
model_thorax['General']['t_cycle'] = model_thorax['NetworkTrigger']['time'][-1] + 1

# Run hemodynamically stable to ensure a 'fair' starting point
model_thorax['Solver']['store_beats'] = 2
model_thorax['General']['t_cycle'] = t_cycle
model_thorax['Thorax']['p_ref'] = 0e3  # Turn off pericardial function
model_thorax['Thorax']['p_max'] = 0e3  # Turn off thorax for hemodynamic stability

model_thorax.run(stable=True)

# Set time to simulate back to initial values, and deactivate pressure flow control
model_thorax['General']['t_cycle'] = n_beats * t_cycle
model_thorax['PFC']['is_active'] = False

# Run the model without breathing cycle and plot hemodynamics
model_thorax.run(1)

# Parameterize thorax
model_thorax['Thorax']['dt'] = 0
model_thorax['Thorax']['p_max'] = -0.2666e3
model_thorax['Thorax']['tr'] = 0.9549

# Run breathing cycle
model_thorax.run(2)

# Initialize circadapt model
model = circadapt.VanOsta2024()

# Run for one cycle to get steady state
model.run(1)
model.run(stable=True)

# Define colors
color1 = '#00BFFF'  # Light blue
color2 = '#00008B'  # Dark blue
color3 = 'cyan'
color4 = '#8B0000'  # Dark red
color5 = 'red'  # Firebrick
color6 = 'orange'  # Indian red

# Create a figure with a 3x2 grid layout
fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(7, 9))  # Adjust figsize as needed

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

# Additional Plot: Pressure relative to atmospheric pressure
ax5.plot(model_thorax['Solver']['t'] * 1e3, model_thorax['Thorax']['p'][:, 0] / 133)
ax5.grid(True)
ax5.set_xlabel('Time [ms]')
ax5.set_ylabel('Pressure relative to atmospheric pressure [mmHg]')
ax5.set_title('Thorax Pressure')  # Add a title if needed

# get volume and pressure of LV
V_lv = model['Cavity']['V'][:, 'cLv']*1e6
p_lv = model['Cavity']['p'][:, 'cLv']*7.5e-3


# Plot PV loop for LV
ax6.plot(V_lv, p_lv, label='LV')

# Add labels and title
ax6.set_xlabel('Volume (ml)')
ax6.set_ylabel('Pressure (mmHg)')
ax6.set_title('Left Ventricle Pressure-Volume Loop')
ax6.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Show the figure
plt.show()



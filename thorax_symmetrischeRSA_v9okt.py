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
model.plot(plt.figure(1, clear=True))

# %% Parameterize thorax
model['Thorax']['dt'] = 0
model['Thorax']['p_max'] = -0.2666e3  # 2 mmHg is the amplitude 
model['Thorax']['tr'] = (2/np.pi)*(1/2)*breath_cycle_time   # no pause


# %% Run breathing cycle

model.run(2)
model.plot(plt.figure(2, clear=True))

plt.figure(3)
plt.plot(model['Solver']['t']*1e3, model['Thorax']['p'][:, 0] / 133)
plt.xlabel('Time [ms]', fontsize = 12)
plt.ylabel('Pressure [mmHg]', fontsize=12)
plt.title('Intrapleural pressure during breathing', fontweight='bold')



import matplotlib.pyplot as plt
import numpy as np
import time
from cardiac_calculations import CardiacCalculator
from plot_functions import HemodynamicPlotter

from _model_thorax import VanOsta2024_Breathing_Thorax
plt.close('all')


# %% load model including the thorax
model = VanOsta2024_Breathing_Thorax()

#%% Heartrate variability
include_hrv = 'off'    # on, off, or inversed

if include_hrv == 'on':
    cycle_times = [0, 0.857, 0.789, 0.732, 0.789, 0.857] #Set mechanical triggers to start from the RA (reflecting sinus rhythm)
elif include_hrv == 'inversed':
    cycle_times = [0, 0.750, 0.811, 0.882, 0.811, 0.750]
elif include_hrv == 'off':
    cycle_times = [0, 0.8, 0.8, 0.8, 0.8, 0.8]

# Calculate length of breathing cycle
breath_cycle_time = np.cumsum(cycle_times)[-1]
n_beats = len(cycle_times)-1

for i in range(n_beats):
    model.add_component('NetworkTrigger', str(i), 'Network.Ra')
    
# Set the start of mechanical triggers 
model['NetworkTrigger']['time'] = np.cumsum(cycle_times[0:-1])


# %% Run hemodynamically stable to ensure 'fair' starting point
model['Solver']['store_beats'] = 2
model['General']['t_cycle'] = breath_cycle_time / (len(cycle_times)-1)   # calculate mean cycle time
model['Thorax']['p_ref'] = 0e3 # turn off pericardial function
model['Thorax']['p_max'] = 0e3 # turn off thorax for hemodynamic stability

#%% Simulate Healthy, HFrEF of HFpEF
State = 'HFrEF'    #choose: Healthy, HFrEF of HFpEF

if State == 'HFrEF':
    model['Patch']['Sf_act'][['pLv0','pSv0']] *= 0.46
elif State == 'HFpEF':
    model['Patch']['k1'][['pLv0', 'pSv0']] *= 1.96
    
#%% Run model until stable
model.run(stable=True)

#%% set time to simulate back to inital values, and deactivate pressure flow control
model['General']['t_cycle'] = breath_cycle_time
model['PFC']['is_active']=False

# %% run the model without breathing cycle
model.run(10)

#%% tuning for LA
LA_p = np.mean(model['Cavity']['p'][:, 'La'] / 133)
#print('Mean LA pressure no breathing', LA_p)
#print()

#%%  Calculate cardiac parameters + plotting - No breathing
V_lv = model['Cavity']['V'][:, 'cLv']*1e6  
flow_aortic_valve = model['Valve']['q'][:,'LvSyArt'] 
flow_pulmonary_valve = model['Valve']['q'][:,'RvPuArt'] 
time_points = model['Solver']['t']
list_cycle_times = cycle_times[1:]

calculator = CardiacCalculator(time_points, cycle_times, n_beats, V_lv)


EFs_no_breathing = calculator.calculate_EF(flow_aortic_valve)
aortic_CO_no_breathing = calculator.calculate_CO(flow_aortic_valve)
pulmonary_CO_no_breathing = calculator.calculate_CO(flow_pulmonary_valve)
healthy_CO = calculator.calculate_CO(flow_aortic_valve)

print('No breathing EFs are ', EFs_no_breathing)
print()  # This creates a blank line

#%% Plot hemodynamic signals of interest - No breathing
plotter = HemodynamicPlotter(model, cycle_times, n_beats, breath_cycle_time)
plotter.plot_overview(aortic_CO_no_breathing, pulmonary_CO_no_breathing)

# %% Parameterize thorax
model['Thorax']['dt'] = 0
model['Thorax']['p_max'] = -0.2666e3  # 2 mmHg is the amplitude 
model['Thorax']['tr'] = (breath_cycle_time/np.pi)   # no pause


# %% Run the model with breathing
model.run(10)

#%%  Calculate cardiac parameters + plotting - Breathing
V_lv = model['Cavity']['V'][:, 'cLv']*1e6  
flow_aortic_valve = model['Valve']['q'][:,'LvSyArt'] 
flow_pulmonary_valve = model['Valve']['q'][:,'RvPuArt'] 
time_points = model['Solver']['t']
list_cycle_times = cycle_times[1:]

calculator = CardiacCalculator(time_points, cycle_times, n_beats, V_lv)

EFs_breathing = calculator.calculate_EF(flow_aortic_valve)
aortic_CO_breathing = calculator.calculate_CO(flow_aortic_valve)
pulmonary_CO_breathing = calculator.calculate_CO(flow_pulmonary_valve)

print('Breathing EFs are ', EFs_breathing)

#%% Caluculate cardiac parameters - Healthy breathing
V_lv = model['Cavity']['V'][:, 'cLv']*1e6  
flow_aortic_valve = model['Valve']['q'][:,'LvSyArt'] 
flow_pulmonary_valve = model['Valve']['q'][:,'RvPuArt'] 
time_points = model['Solver']['t']
list_cycle_times = cycle_times[1:]

calculator = CardiacCalculator(time_points, cycle_times, n_beats, V_lv)

#healthy_peak_stress_LA = calculator.calculate_CO()
#healthy_LA_pressure = calculator.calculate_CO()
healthy_aortic_CO = calculator.calculate_CO(flow_aortic_valve)
healthy_pulmonary_CO = calculator.calculate_CO(flow_pulmonary_valve)
print()  # This creates a blank line

#%% Caluculate cardiac parameters - HFpEF breathing
calculator = CardiacCalculator(time_points, cycle_times, n_beats, V_lv)

#HFpEF_peak_stress_LA = calculator.calculate_CO()
#HFpEF_LA_pressure = calculator.calculate_CO()
HFpEF_aortic_CO = calculator.calculate_CO(flow_aortic_valve)
HFpEF_pulmonary_CO = calculator.calculate_CO(flow_pulmonary_valve)
print()  # This creates a blank line

#%% Caluculate cardiac parameters - HFrEF breathing
calculator = CardiacCalculator(time_points, cycle_times, n_beats, V_lv)

#HFrEF_peak_stress_LA = calculator.calculate_CO()
#HFrEF_LA_pressure = calculator.calculate_CO()
HFrEF_aortic_CO = calculator.calculate_CO(flow_aortic_valve)
HFrEF_pulmonary_CO = calculator.calculate_CO(flow_pulmonary_valve)
print()  # This creates a blank line
#%% Plot hemodynamic signals of interest - No breathing
plotter = HemodynamicPlotter(model, cycle_times, n_beats, breath_cycle_time)
plotter.plot_overview(aortic_CO_breathing, pulmonary_CO_breathing)

#%% Compare aortic CO's
plotter.compare_CO(aortic_CO_no_breathing, aortic_CO_breathing, "Comparison of Aortic Cardiac Output", "Cardiac Output (L/min)")
plotter.compare_CO(pulmonary_CO_no_breathing, pulmonary_CO_breathing, "Comparison of Pulmonary Cardiac Output", "Cardiac Output (L/min)")

#%% Compare CO's for healthy, hfref and hfpef
plotter.compare_CO_3bars(healthy_aortic_CO, HFpEF_aortic_CO, HFrEF_aortic_CO,"Comparison of Aortic Cardiac Output", "Cardiac Output (L/min)")
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 06:39:28 2024

@author: 20182785
"""

import circadapt
import matplotlib.pyplot as plt
import numpy as np

from circadapt import VanOsta2024

### 1. Healthy reference
model = VanOsta2024()

model.run(stable = True)

# get all pressure signals 
pressures = model['Cavity']['p'][:, ['cLv', 'La', 'SyArt']]*7.5e-3
p_lv, p_la, p_ao = pressures.T

# get LV and LA volume
volumes = model['Cavity']['V'][:, ['cLv', 'La']]*1e6
V_lv, V_la = volumes.T

# get time
time = model['Solver']['t']*1e3

# Plot hemodynamics 

fig = plt.figure(1, figsize=(12, 4))
ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)

# Plot pressures
ax1.plot(time, p_lv, color = 'lightgrey', linestyle = '-', label = 'left ventricle')
ax1.plot(time, p_la, color = 'lightgrey', linestyle = '--', label = 'left atrium')
ax1.plot(time, p_ao, color = 'lightgrey', linestyle = ':', label = 'aorta')
ax1.legend()

# Plot volumes
ax2.plot(time, V_lv, color = 'lightgrey', linestyle = '-', label = 'left ventricle')
ax2.plot(time, V_la, color = 'lightgrey', linestyle = '--', label = 'left atrium')
ax2.legend()

# Plot PV loops
ax3.plot(V_lv, p_lv, color = 'lightgrey', linestyle = '-', label = 'reference')
ax3.legend()

# plot design, add labels
for ax in [ax1, ax2, ax3]:
    ax.spines[['right', 'top']].set_visible(False)
ax1.set_xlabel('Time [ms]', fontsize=12)
ax2.set_xlabel('Time [ms]', fontsize=12)
ax3.set_xlabel('Volume [mL]', fontsize=12)

ax1.set_ylabel('Pressure [mmHg]', fontsize=12)
ax2.set_ylabel('Volume [mL]', fontsize=12)
ax3.set_ylabel('Pressure [mmHg]', fontsize=12)

ax1.set_title('Pressures',
             fontsize=12, fontweight='bold')
ax2.set_title('Volumes',
             fontsize=12, fontweight='bold')
ax3.set_title('Left ventricular PV loops',
             fontsize=12, fontweight='bold')

fig.suptitle('Simulating global hemodynamics ',
             fontsize=15, fontweight='bold')

plt.tight_layout()
fig

### 2. Heart failure with reduced ejection fraction (HFrEF) --> = systolic heart failure!
### We reduce the contractile function of the left ventricle and intraventricular septum by 40%.

# get reference sfact values for the left ventricle and intraventricular septum --> wat is sfact?
model_hf = VanOsta2024() 

sfact_lv = model_hf['Patch']['Sf_act']['pLv0']
sfact_sv = model_hf['Patch']['Sf_act']['pSv0']

# reduce the value for sfact (linear active stress component) to 60% of its inital value --> wat wordt er gereduceerd? wat houdt linear active stress component in?
# Als ik het goed begrijp wordt Emax gereduceerd met 50%? Emax = p_ee/ (V_ee - V_0) --> V_0 = 0 kiezen we want we hebben niet meerdere loops?
model_hf['Patch']['Sf_act']['pLv0'] = 0.45*sfact_lv
model_hf['Patch']['Sf_act']['pSv0'] = 0.45*sfact_sv


print('The new sfact for the LV and SV equal ', model_hf['Patch']['Sf_act']['pLv0']*1e3, ' kPa and ', 1e3*model['Patch']['Sf_act']['pSv0'], ' kPa respectively.')

# run the model
model_hf.run(stable = True)

# obtain hemodynamics 

# get all pressure signals 
pressures = model_hf['Cavity']['p'][:, ['cLv', 'La', 'SyArt']]*7.5e-3
p_lv, p_la, p_ao = pressures.T

# get LV and LA volume
volumes = model_hf['Cavity']['V'][:, ['cLv', 'La']]*1e6
V_lv, V_la = volumes.T

# get time
time = model_hf['Solver']['t']*1e3

# plot hemodynamics 

# Plot pressures
ax1.plot(time, p_lv, color = 'darkred', linestyle = '-', label = 'left ventricle')
ax1.plot(time, p_la, color = 'darkred', linestyle = '--', label = 'left atrium')
ax1.plot(time, p_ao, color = 'darkred', linestyle = ':', label = 'aorta')

# Plot volumes
ax2.plot(time, V_lv, color = 'darkred', linestyle = '-', label = 'left ventricle')
ax2.plot(time, V_la, color = 'darkred', linestyle = '--', label = 'left atrium')

# Plot PV loops
ax3.plot(V_lv, p_lv, color = 'darkred', linestyle = '-', label = 'reduced contractility')
ax3.legend()

### It can be seen that for HFrEF, the LV is dilated and that the EF is reduced
fig

### Note: Systolic heart failure is another term for Heart Failure with Reduced
### Ejection Fraction (HFrEF). In HFrEF, the heart's ability to contract and pump 
### blood is impaired, leading to a reduced ejection fraction. This is contrasted with Heart 
### Failure with Preserved Ejection Fraction (HFpEF), where the heart's ability to contract 
### may be normal, but its ability to relax and fill with blood is impaired

### Ejection fraction = stroke volume divided by the maximum filling 
### Normal: 70/120 = 60%
### HF: 80/180 = 50%

#%% Stroke volume

flow_aortic_valve = model['Valve']['q'][:,'LvSyArt'] 
time_points = model['Solver']['t']
stroke_volume = np.trapezoid(flow_aortic_valve, time_points) * 1e6  # mL

#%% End diastolic volume (max volume in LV?)

V_lv_hf = model_hf['Cavity']['V'][:, 'cLv']*1e6  # Left ventricle volume (HFrEF)
EDV_hf = np.max(V_lv_hf)  # End Diastolic Volume

#%%

EF = stroke_volume/EDV_hf
print('The Ejection Fraction is ', EF)

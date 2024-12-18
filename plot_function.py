import matplotlib.pyplot as plt
import numpy as np

## ======= Plot hemodynamic signals of interest

def plot_overview(model, cycle_times, n_beats, breath_cycle_time, aortic_CO_list, pulmonary_CO_list):
    """
    Function to plot all signals of interest: 
        volumes: RA, LA, RV, LV
        pressures: RA, LA, RV, LV, Aorta, Pulm. Artery
        pressure-volume loop: LV
        transmural pressure: RA, LA, RV, LV minus the thorax pressure
        total stress: RA, LA, RV, LV
        thorax pressure
        heart rate function
        cardiac output for the first 5 beats
        
    Parameters:
    model: Model that was used in the simulation that contains all the data.
    cycle_times (list): List of cycle times for each beat.
    n_beats (int): Number of heartbeats.
    CO_list (list): List of cardiac output values for each beat.

    Returns:
    One figure with 13 subplots of the signals of interest .
    """
    
    # Define colors
    color1 = '#00BFFF'  # Light blue
    color2 = '#00008B'  # Dark blue
    color3 = 'cyan'
    color4 = '#8B0000'  # Dark red
    color5 = 'red'  # Firebrick
    color6 = 'orange'  # Indian red
    
    # Create a figure with a 4x2 grid layout to accommodate the new plot
    # fig, ((ax1, ax2, ax9, ax10), (ax3, ax4, ax11, ax12), (ax5, ax6, ax13, ax14), (ax7, ax8, ax15, ax16)) = plt.subplots(4, 4, figsize=(10, 10))  # Adjust figsize as needed
    
    fig = plt.figure(figsize=(10, 10))
    gs = fig.add_gridspec(4, 4)
    
    # Create subplots in the 4x4 grid
    ax1 = fig.add_subplot(gs[0, 0])  # Top-left
    ax2 = fig.add_subplot(gs[0, 1])  # Top
    ax9 = fig.add_subplot(gs[0, 2])  # Top
    ax10 = fig.add_subplot(gs[0, 3])  # Top-right
    
    ax3 = fig.add_subplot(gs[1, 0])  # 2nd row
    ax4 = fig.add_subplot(gs[1, 1])
    ax11 = fig.add_subplot(gs[1, 2])
    ax12 = fig.add_subplot(gs[1, 3])
    
    ax5 = fig.add_subplot(gs[2, 0])  # 3rd row
    ax6 = fig.add_subplot(gs[2, 1])
    
    ax7 = fig.add_subplot(gs[3, 0])  # 4th row
    ax8 = fig.add_subplot(gs[3, 1])
    
    # Use the 2x2 space on the lower right (axes 13-16)
    ax_larger = fig.add_subplot(gs[2:, 2:])  # Merge bottom-right 2x2
    
    # Right Heart Volume Plot: Right Atrium and Right Ventricle
    ax1.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['V'][:, 'Ra'] * 1e6, 
             label="RA", color=color1)
    
    ax1.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['V'][:, 'cRv'] * 1e6, 
             label="RV", color=color2)
    
    ax1.set_ylim(0, 150)
    ax1.set_yticks(np.arange(0, 151, 25))
    ax1.set_xlabel('Time [ms]')
    ax1.set_ylabel('Volume [ml]')
    ax1.set_title('Right Heart', fontweight='bold')
    ax1.legend(ncol=2, loc='upper right')
    
    # Left Heart Volume Plot: Left Atrium and Left Ventricle
    ax2.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['V'][:, 'La'] * 1e6, 
             label="LA", color=color4)
    
    ax2.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['V'][:, 'cLv'] * 1e6, 
             label="LV", color=color5)
    
    ax2.set_ylim(0, 250)
    ax2.set_yticks(np.arange(0,251, 50))
    ax2.set_xlabel('Time [ms]')
    ax2.set_ylabel('Volume [ml]')
    ax2.set_title('Left Heart', fontweight='bold')
    ax2.legend(ncol=2, loc='upper right')
    
    # Right Heart Pressure Plot: Right Atrium, Right Ventricle, Pulmonary Artery
    ax3.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['p'][:, 'Ra'] / 133, 
             label="RA", color=color1)
    
    ax3.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['p'][:, 'cRv'] / 133, 
             label="RV", color=color2)
    
    ax3.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['p'][:, 'PuArt'] / 133, 
             label="PA", color=color3)
    
    ax3.set_ylim(0, 150)
    ax3.set_yticks(np.arange(0, 151, 25))
    ax3.set_xlabel('Time [ms]')
    ax3.set_ylabel('Pressure [mmHg]')
    ax3.legend(ncol=3, loc='upper right')
    
    # Left Heart Pressure Plot: Left Atrium, Left Ventricle, Aorta
    ax4.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['p'][:, 'La'] / 133, 
             label="LA", color=color4)
    
    ax4.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['p'][:, 'cLv'] / 133, 
             label="LV", color=color5)
    
    ax4.plot(model['Solver']['t'] * 1e3, 
             model['Cavity']['p'][:, 'SyArt'] / 133, 
             label="AO", color=color6)
    
    ax4.set_ylim(0, 150)
    ax4.set_yticks(np.arange(0, 151, 25))
    ax4.set_xlabel('Time [ms]')
    ax4.set_ylabel('Pressure [mmHg]')
    ax4.legend(ncol=3, loc='upper right')
    
    # Right Heart Transmural Pressure Plot: Right Atrium and Right Ventricle
    p_ra = model['Cavity']['p'][:, 'Ra']*7.5e-3
    p_rv = model['Cavity']['p'][:, 'cRv']*7.5e-3
    p_thorax = model['Thorax']['p'][:, 0]*7.5e-3
    
    ax5.plot(model['Solver']['t'] * 1e3,
             p_ra-p_thorax,
             label="RA", color=color1)
    
    ax5.plot(model['Solver']['t'] * 1e3,
             p_rv-p_thorax,
             label="RV", color=color2)
    
    ax5.set_ylim(0, 150)
    ax5.set_yticks(np.arange(0, 151, 25))
    ax5.set_xlabel('Time [ms]')
    ax5.set_ylabel('Transmural pressure [mmHg]')
    ax5.legend(ncol=2, loc='upper right')
    
    
    # Left Heart Transmural Pressure Plot: Left Atrium and Left Ventricle
    p_la = model['Cavity']['p'][:, 'La']*7.5e-3 
    p_lv = model['Cavity']['p'][:, 'cLv']*7.5e-3
    
    ax6.plot(model['Solver']['t'] * 1e3,
             p_la-p_thorax,
             label="LA", color=color4)
    
    ax6.plot(model['Solver']['t'] * 1e3,
             p_lv-p_thorax,
             label="LV", color=color5)
    
    ax6.set_ylim(0, 150)
    ax6.set_yticks(np.arange(0, 151, 25))
    ax6.set_xlabel('Time [ms]')
    ax6.set_ylabel('Transmural pressure [mmHg]')
    ax6.legend(ncol=2, loc='upper right')

    # Right Heart Stress Plot: Right Atrium, Right Ventricle
    ax7.plot(model['Solver']['t'] * 1e3, 
             model['Patch']['Sf'][:, 'pRa0']*1e-3, 
             label="RA", color=color1)
    
    ax7.plot(model['Solver']['t'] * 1e3, 
             model['Patch']['Sf'][:, 'pRv0']*1e-3, 
             label="RV", color=color2)
    
    ax7.set_ylim(0, 100)
    ax7.set_yticks(np.arange(0, 101, 25))
    ax7.set_xlabel('Time [ms]')
    ax7.set_ylabel('Total stress [kPa]')
    ax7.legend(ncol=2, loc='upper right')

    # Left Heart Stress Plot: Right Atrium, Right Ventricle
    ax8.plot(model['Solver']['t'] * 1e3, 
             model['Patch']['Sf'][:, 'pLa0']*1e-3, 
             label="LA", color=color4)
    
    ax8.plot(model['Solver']['t'] * 1e3, 
             model['Patch']['Sf'][:, 'pLv0']*1e-3, 
             label="LV", color=color5)
    
    ax8.set_ylim(0, 100)
    ax8.set_yticks(np.arange(0, 151, 25))
    ax8.set_xlabel('Time [ms]')
    ax8.set_ylabel('Total stress [kPa]')
    ax8.legend(ncol=2, loc='upper right')

    # Thorax Pressure Plot
    ax9.plot(model['Solver']['t'] * 1e3, p_thorax, color='blue')
    ax9.grid(True)
    ax9.set_xlabel('Time [ms]')
    ax9.set_ylabel('Pressure [mmHg]')
    ax9.set_title('Thorax Pressure', fontweight='bold')
    
    # Plot the BPM values against the calculated time points
    amount = model['Solver']['store_beats']
    bpm_values = [60 / cycle_time for cycle_time in cycle_times[1:]] 
    bpm_values = np.append(bpm_values, bpm_values[-1]) # for plottin purposes
    bpm_values_repeated = np.tile(bpm_values, amount) 
    single_cycle_time_points = np.cumsum(cycle_times[0:]) * 1e3  # Convert to milliseconds
    time_points = np.concatenate([single_cycle_time_points + (i * breath_cycle_time * 1e3) 
                                  for i in range(amount)])  # Adjust time points for each beat repetition
    
    ax11.step(time_points, bpm_values_repeated, where='post', color='blue', linewidth=1.5)
    ax11.grid(True)
    ax11.set_xlabel('Time [ms]')
    ax11.set_ylabel('Heart rate [bpm]')
    ax11.set_title('Heart rate over time', fontweight='bold')
    
    # Cardiac output bar plot aorta
    ax12.bar(range(1, n_beats+1), aortic_CO_list,  color=color5)
    ax12.set_xlabel('Beat Number')
    ax12.set_ylabel('Cardiac Output (L/min)')
    ax12.set_title('CO - aorta', fontweight='bold') 
    
    # Cardiac output bar plot pulmonary artery
    ax10.bar(range(1, n_beats+1), pulmonary_CO_list,  color=color2)
    ax10.set_xlabel('Beat Number')
    ax10.set_ylabel('Cardiac Output (L/min)')
    ax10.set_title('CO - pulmonary', fontweight='bold') 
    
    # Left Ventricle Pressure-Volume Loop
    V_lv = model['Cavity']['V'][:, 'cLv']*1e6
    
    ax_larger.plot(V_lv, p_lv, label='Left Ventricle', color = color5)
    ax_larger.set_xlabel('Volume [ml]')
    ax_larger.set_ylabel('Pressure [mmHg]')
    ax_larger.set_title('LV Pressure-Volume Loop', fontweight='bold')
    
    # Adjust layout for better spacing
    plt.tight_layout()
    
    
    # fig.delaxes(ax14)
    # fig.delaxes(ax15)
    # fig.delaxes(ax16)
    
    manager = plt.get_current_fig_manager()
    manager.window.setGeometry(500, 100, 900, 900)
    
    # Show the figure
    plt.show()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Relaxation_Analysis.py
#
#   PURPOSE: Perform analysis on a relaxation segment
#
#   PURPOSE: Perform analysis on a compressive loading segment
#
#   INPUTS:
#       Raw         Raw Data Dictionary
#       Analysis    Analysis Dictionary
#       dir         Test Direction (e.g., 11, 22, etc.)
#       stage_num   number of the stage being analyzed
#       user_opts   user_options
#       plot_opt    plottong option
#   OUTPUTS:
#       Analysis    Populated Analysis Dictionary
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def Relaxation_Analysis(Raw, Analysis, dir, stage_num, user_opts, plot_opt):
    # Import Modules
    import numpy as np
    import scipy.stats
    import matplotlib.pyplot as plt
 
    # Define the vectors
    # -- Define the Indicies
    if stage_num == 0:
        start_idx = 0
    else:
        start_idx = Analysis['Stages']['End Index']['Value'][stage_num-1]+1
    end_idx = Analysis['Stages']['End Index']['Value'][stage_num]

    # -- Set time, strain, and stress
    time = np.array(Raw['Raw Data']['Time']['Value'][start_idx:end_idx+1])
    strain = np.array(Raw['Raw Data']['Strain-' + dir]['Value'][start_idx:end_idx+1])
    stress = np.array(Raw['Raw Data']['Stress-' + dir]['Value'][start_idx:end_idx+1])  
    
    # -- Filter the data
    from scipy.signal import savgol_filter
    strain_filt = savgol_filter(strain, 51, 3) # window size 51, polynomial order 3
    stress_filt = savgol_filter(stress, 51, 3) # window size 51, polynomial order 3

    # -- Set filtered, reduced arrays
    time_red = [time[0]]
    strain_red = [strain_filt[0]]
    stress_red = [strain_filt[0]]

    for k in range(len(strain_filt)):
        if k % 1 == 0:
            time_red.append(time[k])
            strain_red.append(strain_filt[k])
            stress_red.append(stress_filt[k])

    time = np.array(time_red)
    strain = np.array(strain_red)
    stress = np.array(stress_red)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#   STAGE ANALYSIS
#   Analysis on any stage with compressive loading
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Calculate Strain Rate and Stress Rate
    strain_rate_info = scipy.stats.linregress(time, strain)
    strain_rate = strain_rate_info.slope
    strain_rate_fit = strain_rate_info.rvalue

    stress_rate_info = scipy.stats.linregress(time, stress)
    stress_rate = stress_rate_info.slope
    stress_rate_fit = stress_rate_info.rvalue

    if len(Analysis['Stages']['Strain Rate-' + dir]['Value']) != len(Analysis['Stages']['Stage Name']['Value']):
        Analysis['Stages']['Strain Rate-' + dir]['Value'].append(strain_rate)
        Analysis['Stages']['Stress Rate-' + dir]['Value'].append(stress_rate)
    else:
        Analysis['Stages']['Strain Rate-' + dir]['Value'][stage_num] = strain_rate
        Analysis['Stages']['Stress Rate-' + dir]['Value'][stage_num] = stress_rate

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#   RELAXATION ANALYSIS
#   Relaxation Stage Analysis
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Determine Nominal Relaxation Strain
    relax_strain = round(np.average(strain),4)
    relax_time = time[-1] - time[0]
    relax_stress = stress[-1] - max(stress)
  
    if relax_strain < 0:
        if stage_num == 1:
            Analysis['Relaxation Analysis']['Compressive Relaxation Hold Strain-' + dir]['Value'] = relax_strain
            Analysis['Relaxation Analysis']['Compressive Relaxation Total Time']['Value'] = relax_time
            Analysis['Relaxation Analysis']['Compressive Relaxation Stress Drop-'+dir]['Value'] = relax_stress

            # Get the Relaxation Vectors
            Analysis['Relaxation Analysis']['Compressive Relaxation Time']['Value'] = time
            Analysis['Relaxation Analysis']['Compressive Relaxation Strain-' + dir]['Value'] = strain
            Analysis['Relaxation Analysis']['Compressive Relaxation Stress-' + dir]['Value'] = stress

        Analysis['Stages']['Relaxation Analysis']['Compressive Relaxation Hold Strain-' + dir]['Value'].append(relax_strain)
        Analysis['Stages']['Relaxation Analysis']['Compressive Relaxation Total Time']['Value'].append(relax_time)
        Analysis['Stages']['Relaxation Analysis']['Compressive Relaxation Stress Drop-'+dir]['Value'].append(relax_stress)

        # Get the Relaxation Vectors
        Analysis['Stages']['Relaxation Analysis']['Compressive Relaxation Time']['Value'].append(time)
        Analysis['Stages']['Relaxation Analysis']['Compressive Relaxation Strain-' + dir]['Value'].append(strain)
        Analysis['Stages']['Relaxation Analysis']['Compressive Relaxation Stress-' + dir]['Value'].append(stress)
    else:
        if dir[0] == dir[1]:
            if stage_num == 1:
                Analysis['Relaxation Analysis']['Relaxation Hold Strain-' + dir]['Value'] = relax_strain
                Analysis['Relaxation Analysis']['Relaxation Total Time']['Value'] = relax_time
                Analysis['Relaxation Analysis']['Relaxation Stress Drop-'+dir]['Value'] = relax_stress

                # Get the Relaxation Vectors
                Analysis['Relaxation Analysis']['Relaxation Time']['Value'] = time
                Analysis['Relaxation Analysis']['Relaxation Strain-' + dir]['Value'] = strain
                Analysis['Relaxation Analysis']['Relaxation Stress-' + dir]['Value'] = stress

            Analysis['Stages']['Relaxation Analysis']['Relaxation Hold Strain-' + dir]['Value'].append(relax_strain)
            Analysis['Stages']['Relaxation Analysis']['Relaxation Total Time']['Value'].append(relax_time)
            Analysis['Stages']['Relaxation Analysis']['Relaxation Stress Drop-'+dir]['Value'].append(relax_stress)

            # Get the Relaxation Vectors
            Analysis['Stages']['Relaxation Analysis']['Relaxation Time']['Value'].append(time)
            Analysis['Stages']['Relaxation Analysis']['Relaxation Strain-'+dir]['Value'].append(strain)
            Analysis['Stages']['Relaxation Analysis']['Relaxation Stress-'+dir]['Value'].append(stress)
        else:
            if stage_num == 1:
                Analysis['Relaxation Analysis']['Shear Relaxation Hold Strain-' + dir]['Value'] = relax_strain
                Analysis['Relaxation Analysis']['Shear Relaxation Total Time']['Value'] = relax_time
                Analysis['Relaxation Analysis']['Shear Relaxation Stress Drop-'+dir]['Value'] = relax_stress

                # Get the Relaxation Vectors
                Analysis['Relaxation Analysis']['Shear Relaxation Time']['Value'] = time
                Analysis['Relaxation Analysis']['Shear Relaxation Strain-' + dir]['Value'] = strain
                Analysis['Relaxation Analysis']['Shear Relaxation Stress-' + dir]['Value'] = stress

            Analysis['Stages']['Relaxation Analysis']['Shear Relaxation Hold Strain-' + dir]['Value'].append(relax_strain)
            Analysis['Stages']['Relaxation Analysis']['Shear Relaxation Total Time']['Value'].append(relax_time)
            Analysis['Stages']['Relaxation Analysis']['Shear Relaxation Stress Drop-'+dir]['Value'].append(relax_stress)

            # Get the Relaxation Vectors
            Analysis['Stages']['Relaxation Analysis']['Shear Relaxation Time']['Value'].append(time)
            Analysis['Stages']['Relaxation Analysis']['Shear Relaxation Strain-' + dir]['Value'].append(strain)
            Analysis['Stages']['Relaxation Analysis']['Shear Relaxation Stress-' + dir]['Value'].append(stress)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PLOT
# Create additional plotting
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if stage_num == 1:
        if plot_opt == 1:
            # Plot Strain Time
            plt.subplot(1, 2, 1)
            plt.plot(np.array(Raw['Raw Data']['Time']['Value'][0:end_idx+1]), np.array(Raw['Raw Data']['Strain-' + dir]['Value'][0:end_idx+1]), 'k', label = 'Raw Data')
            plt.plot([0, max(time)],[relax_strain, relax_strain],'r--',label = 'Relaxation Hold Strain')

            plt.legend()
            plt.xlabel('Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']')
            plt.ylabel('Strain [' + Raw['Raw Data']['Units']['Strain']['Value']+ ']')

            # Plot Relaxation Stress Strain
            plt.subplot(1, 2, 2)
            plt.plot(time, stress, 'k', label = 'Relaxation Raw Data')
            plt.plot([max(time),max(time)], [min(stress),max(stress)], 'r', label = 'Relaxation Stress Change')

            plt.legend()
            plt.xlabel('Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']')
            plt.ylabel('Stress [' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')

            plt.show()

    return Raw, Analysis
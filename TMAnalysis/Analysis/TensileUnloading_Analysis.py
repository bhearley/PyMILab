#-----------------------------------------------------------------------------------------
#
#   TensileUnloading_Analysis.py
#
#   PURPOSE: Perform analysis on a tensile unloading segment
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
#-----------------------------------------------------------------------------------------
def TensileUnloading_Analysis(Raw, Analysis, dir, stage_num, user_opts, plot_opt):
    # Import Modules
    import numpy as np
    import scipy.interpolate
    import scipy.stats
    from scipy.signal import argrelextrema
    import matplotlib.pyplot as plt

    # Define the vectors
    # -- Define the Indicies
    if stage_num == 0:
        start_idx = 0
    else:
        start_idx = Analysis['Stages']['End Index']['Value'][stage_num-1]+1
    end_idx = Analysis['Stages']['End Index']['Value'][stage_num]

    time = np.array(Raw['Raw Data']['Time']['Value'][start_idx:end_idx+1])
    strain = np.array(Raw['Raw Data']['Strain-' + dir]['Value'][start_idx:end_idx+1])
    if dir == '11':
        diam_dir= '22'
        pr_dir = '12'
    if dir == '22':
        diam_dir= '22'
        pr_dir = '12'
    if Raw['Raw Data']['Strain-' + diam_dir]['Value'] != None:
        diamstrain = np.array(Raw['Raw Data']['Strain-' + diam_dir]['Value'][start_idx:end_idx+1])
    else:
        diamstrain = []
    stress = np.array(Raw['Raw Data']['Stress-' + dir]['Value'][start_idx:end_idx+1])  
    
    # -- Filter the data
    from scipy.signal import savgol_filter
    strain_filt = savgol_filter(strain, 51, 3) # window size 51, polynomial order 3
    stress_filt = savgol_filter(stress, 51, 3) # window size 51, polynomial order 3
    if len(diamstrain) != 0:
        diamstrain_filt = savgol_filter(diamstrain, 51, 3) # window size 51, polynomial order 3

    time_red = [time[0]]
    strain_red = [strain_filt[0]]
    stress_red = [strain_filt[0]]
    if len(diamstrain) != 0:
        diamstrain_red = [diamstrain_filt[0]]
    for k in range(len(strain_filt)):
        if k % 1 == 0:
            time_red.append(time[k])
            strain_red.append(strain_filt[k])
            stress_red.append(stress_filt[k])
            if len(diamstrain) != 0:
                diamstrain_red.append(diamstrain_filt[k])
    time = np.array(time_red)
    strain = np.array(strain_red)
    stress = np.array(stress_red)
    if len(diamstrain) != 0:
        diamstrain = np.array(diamstrain_red)

    #-----------------------------------------------------------------------------------------------------
    #   STAGE ANALYSIS
    #   Analysis on any stage with tensile unloading
    #-----------------------------------------------------------------------------------------------------

    # Calculate Strain Rate and Stress Rate
    strain_rate_info = scipy.stats.linregress(time, strain)
    strain_rate = strain_rate_info.slope
    strain_rate_fit = strain_rate_info.rvalue

    stress_rate_info = scipy.stats.linregress(time, stress)
    stress_rate = stress_rate_info.slope
    stress_rate_fit = stress_rate_info.rvalue

    if strain_rate_fit > stress_rate_fit:
        if len(Analysis['Stages']['Strain Rate-' + dir]['Value']) != len(Analysis['Stages']['Stage Name']['Value']):
            Analysis['Stages']['Strain Rate-' + dir]['Value'].append(strain_rate)
            Analysis['Stages']['Stress Rate-' + dir]['Value'].append(None)
        else:
            Analysis['Stages']['Strain Rate-' + dir]['Value'][stage_num] = strain_rate
            Analysis['Stages']['Stress Rate-' + dir]['Value'][stage_num] = None
    else:
        if len(Analysis['Stages']['Strain Rate-' + dir]['Value']) != len(Analysis['Stages']['Stage Name']['Value']):
            Analysis['Stages']['Strain Rate-' + dir]['Value'].append(None)
            Analysis['Stages']['Stress Rate-' + dir]['Value'].append(stress_rate)
        else:
            Analysis['Stages']['Strain Rate-' + dir]['Value'][stage_num] = None
            Analysis['Stages']['Stress Rate-' + dir]['Value'][stage_num] = stress_rate


    #-----------------------------------------------------------------------------------------------------
    #   TENSILE ANALYSIS
    #   Analysis on the second stage only - no load history

    #-------------------------------------------------------------------------------------------------
    # Linear Elastic Behavior
    #   Automatically calculate elastic unloading modulus
    #
    from Analysis.Linear_Analysis import Linear_Analysis
    mod_info = scipy.stats.linregress(strain, stress)

    if stage_num == 1:
        Analysis['Tensile Analysis']['Unloading Modulus-' + dir]['Value'] = mod_info.slope

    Analysis['Stages']['Tensile Analysis']['Unloading Modulus-' + dir]['Value'].append(mod_info.slope)

    #-------------------------------------------------------------------------------------------------
    # Reversible and Irreversible Strain
    if abs(stress[-1]) < 1:
        if stage_num == 1:
            Analysis['Tensile Analysis']['Reversible Strain-' + dir]['Value'] = abs(strain[0]-strain[-1])
            Analysis['Tensile Analysis']['Irreversible Strain-' + dir]['Value'] = strain[-1]

        Analysis['Stages']['Tensile Analysis']['Reversible Strain-' + dir]['Value'].append(abs(strain[0]-strain[-1]))
        Analysis['Stages']['Tensile Analysis']['Irreversible Strain-' + dir]['Value'].append(strain[-1])

    #-------------------------------------------------------------------------------------------------
    # PLOT
    #   Create additional plotting
    #
    if stage_num == 1:
        if plot_opt == 1:
            # -- Plot the raw data
            plt_strain = np.array(Raw['Raw Data']['Strain-' + dir]['Value'][0:end_idx+1])
            plt_stress = np.array(Raw['Raw Data']['Stress-' + dir]['Value'][0:end_idx+1])
            plt.plot(plt_strain,plt_stress,'k',label = 'Raw Data')

            # -- Plot the linear fit
            if Analysis['Tensile Analysis']['Unloading Modulus-' + dir]['Value'] != None:
                stress_lin = strain*mod_info.slope + mod_info.intercept
                plt.plot(strain,stress_lin,'r--',label='Linear Fit')

            # -- Plot Reversible and Irreversible Strain
            if Analysis['Tensile Analysis']['Irreversible Strain-' + dir]['Value'] != None:
                plt.plot([0,Analysis['Tensile Analysis']['Irreversible Strain-' + dir]['Value']],[0,0],'g',label='Irreversible Strain')
            if Analysis['Tensile Analysis']['Irreversible Strain-' + dir]['Value'] != None:
                plt.plot([Analysis['Tensile Analysis']['Irreversible Strain-' + dir]['Value'],Analysis['Tensile Analysis']['Irreversible Strain-' + dir]['Value']+Analysis['Tensile Analysis']['Reversible Strain-' + dir]['Value']],[0,0],'b',label='Reversible Strain')

            plt.legend()
            plt.xlabel('Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']')
            plt.ylabel('Stress [' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')
            plt.show()


    return Raw, Analysis
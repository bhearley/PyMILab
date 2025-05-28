#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   ShearLoading_Analysis.py
#
#   PURPOSE: Perform analysis on a shear loading segment
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
def ShearLoading_Analysis(Raw, Analysis, dir, stage_num, user_opts, plot_opt):
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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#   SHEAR ANALYSIS
#   Shear Stage Analysis
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if stage_num == 0:
        # Strain and Stress Rate
        if strain_rate_fit > stress_rate_fit:
            Analysis['Shear Analysis']['Shear Strain Rate']['Value'] = strain_rate
            Analysis['Shear Analysis']['Shear Stress Rate']['Value'] = None
        else:
            Analysis['Shear Analysis']['Shear Strain Rate']['Value'] = None
            Analysis['Shear Analysis']['Shear Stress Rate']['Value'] = stress_rate

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Linear Elastic Behavior
    #   Automatically calculate elastic modulus and proportional limit
    #
    # Import Lienar Analysis Module
    from Analysis.Linear_Analysis import Linear_Analysis
    mod, prop, prop_e, PR, lin_idx, mod_info = Linear_Analysis(strain, stress, [])

    # Save First Stage Info
    if stage_num == 0:
        if user_opts['UserEdit']['Modulus'] == 0:
            Analysis['Shear Analysis']['Shear Modulus-' + dir]['Value'] = mod
        if user_opts['UserEdit']['Prop'] == 0:
            Analysis['Shear Analysis']['Shear Proportional Limit-' + dir]['Value'] = prop
            Analysis['Shear Analysis']['Shear Proportional Limit Strain-' + dir]['Value'] = prop_e
        
    # Save All Stage Info
    Analysis['Stages']['Shear Analysis']['Shear Modulus-' + dir]['Value'].append(mod)
    Analysis['Stages']['Shear Analysis']['Shear Proportional Limit-' + dir]['Value'].append(prop)
    Analysis['Stages']['Shear Analysis']['Shear Proportional Limit Strain-' + dir]['Value'].append(prop_e)

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Yield Behavior
    #   Check if custom offset yield exist and store
    #
    if stage_num == 0:
        # Delete Previous Calculations
        Analysis['Shear Analysis']['Shear Yield-' + dir]['Offset Strain']['Value'] = []
        Analysis['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'] = []
        Analysis['Shear Analysis']['Shear Yield-' + dir]['Strain at Yield Strength']['Value'] = []

        if "Yield Offset" in list(user_opts.keys()):
            if lin_idx[1] < end_idx-start_idx:
                from Analysis.CustomYield import CustomYield
                for i in range(len(user_opts["Yield Offset"])):
                    ystress, ystrain= CustomYield(strain, stress, Analysis['Shear Analysis']['Shear Modulus-' + dir]['Value'], user_opts["Yield Offset"][i])
                    
                    if ystress != None:
                        if ystress < max(stress) and ystress > prop:
                            Analysis['Shear Analysis']['Shear Yield-' + dir]['Offset Strain']['Value'].append(user_opts["Yield Offset"][i])
                            Analysis['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'].append(ystress)
                            Analysis['Shear Analysis']['Shear Yield-' + dir]['Strain at Yield Strength']['Value'].append(ystrain)

    # Delete Previous Calculations
    Analysis['Stages']['Shear Analysis']['Shear Yield-' + dir]['Offset Strain']['Value'] = []
    Analysis['Stages']['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'] = []
    Analysis['Stages']['Shear Analysis']['Shear Yield-' + dir]['Strain at Yield Strength']['Value'] = []

    if "Yield Offset" in list(user_opts.keys()):
        if lin_idx[1] < end_idx-start_idx:
            from Analysis.CustomYield import CustomYield
            for i in range(len(user_opts["Yield Offset"])):
                ystress, ystrain= CustomYield(strain, stress, Analysis['Shear Analysis']['Shear Modulus-' + dir]['Value'], user_opts["Yield Offset"][i])
                    
                if ystress != None:
                    if ystress < max(stress) and ystress > prop:
                        Analysis['Stages']['Shear Analysis']['Shear Yield-' + dir]['Offset Strain']['Value'].append(user_opts["Yield Offset"][i])
                        Analysis['Stages']['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'].append(ystress)
                        Analysis['Stages']['Shear Analysis']['Shear Yield-' + dir]['Strain at Yield Strength']['Value'].append(ystrain)
                 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Ultimate Strength
    #   Only calculate ultimate strength if tested to failure
    #
    # Save Max Strength Otherwise to Property Information if 1st Stage and tested to failure
    if stage_num == 0:
        if stage_num == len(Analysis['Stages']['Stage Name']['Value'])-1:
            if user_opts['Additional Information'][0] == 'Yes':
                Analysis['Shear Analysis']['Shear Ultimate Strength-' + dir]['Value'] = max(stress)
                Analysis['Shear Analysis']['Shear Strain at UTS-' + dir]['Value'] = strain[np.where(stress == max(stress))[0][0]]

    # Save Max Strength Otherwise to Stage Information
    Analysis['Stages']['Shear Analysis']['Shear Ultimate Strength-' + dir]['Value'].append(max(stress))
    Analysis['Stages']['Shear Analysis']['Shear Strain at UTS-' + dir]['Value'].append(strain[np.where(stress == max(stress))[0][0]])

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Failure Strength
    #   Only calculate ultimate strength if tested to failure
    #
    if stage_num == 0:
        if stage_num == len(Analysis['Stages']['Stage Name']['Value'])-1:
            if user_opts['Additional Information'][0] == 'Yes':
                fail_idx = len(stress)-1 # Initially assume last point is failure

                # Check for a large load drop
                for k in range(1,len(stress)-1):
                    if (stress[k]-stress[k-1])/Analysis['Shear Analysis']['Shear Ultimate Strength-'+dir]['Value'] < -0.5:
                        fail_idx = k
                        break

                Analysis['Shear Analysis']['Shear Failure Strength-'+dir]['Value'] = stress[fail_idx]
                Analysis['Shear Analysis']['Shear Strain at Failure-'+dir]['Value'] = strain[fail_idx]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PLOT
# Create additional plotting
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if stage_num == 0:
        if plot_opt == 1:
            # -- Plot the raw data
            plt.plot(strain,stress,'k',label = 'Raw Data')
            # -- Plot the linear fit
            if Analysis['Shear Analysis']['Shear Modulus-' + dir]['Value'] != None:
                strain_lin_end = (stress[-1]-stress[0])/Analysis['Shear Analysis']['Shear Modulus-' + dir]['Value']+strain[0]
                strain_lin = np.linspace(strain[0],strain_lin_end,100)
                stress_lin = strain_lin*mod_info.slope + mod_info.intercept
                plt.plot(strain_lin,stress_lin,'r--',label='Linear Fit')

            # -- Plot Proportional Limit
            if Analysis['Shear Analysis']['Shear Proportional Limit-' + dir]['Value'] != None:
                plt.plot(Analysis['Shear Analysis']['Shear Proportional Limit Strain-' + dir]['Value'],Analysis['Shear Analysis']['Shear Proportional Limit-' + dir]['Value'],'ro',label='Proportional Limit')

            # -- Plot Yield Behavior
            if Analysis['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'] != None:
                for i in range(len(Analysis['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'])):
                    plt.plot(Analysis['Shear Analysis']['Shear Yield-' + dir]['Strain at Yield Strength']['Value'][i], Analysis['Shear Analysis']['Shear Yield-' + dir]['Yield Strength']['Value'][i],'o',
                             label = str(Analysis['Shear Analysis']['Shear Yield-' + dir]['Offset Strain']['Value'][i]) + Raw['Raw Data']['Units']['Strain']['Value'] + ' Offset Yield') 

            # -- Plot Ultimate Strength
            if Analysis['Shear Analysis']['Shear Ultimate Strength-' + dir]['Value'] != None:
                plt.plot(Analysis['Shear Analysis']['Shear Strain at UTS-' + dir]['Value'], Analysis['Shear Analysis']['Shear Ultimate Strength-' + dir]['Value'],'mo',label='Ultimate Strength')

            # -- Plot Failure Strength
            if Analysis['Shear Analysis']['Shear Failure Strength-' + dir]['Value'] != None:
                plt.plot(Analysis['Shear Analysis']['Shear Strain at Failure-'+dir]['Value'],Analysis['Shear Analysis']['Shear Failure Strength-'+dir]['Value'],'co',label='Failure Strength')

            plt.legend()
            plt.xlabel('Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']')
            plt.ylabel('Stress [' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')
            plt.show()

    return Raw, Analysis
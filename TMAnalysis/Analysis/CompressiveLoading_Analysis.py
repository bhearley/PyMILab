#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   CompressiveLoading_Analysis.py
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
def CompressiveLoading_Analysis(Raw, Analysis, dir, stage_num, user_opts, plot_opt):
    # Import Modules
    import numpy as np
    import scipy.stats
    import matplotlib.pyplot as plt

    # Import Functions
    from Analysis.CustomYield import CustomYield
    from Analysis.Linear_Analysis import Linear_Analysis

    # Define the vectors
    # -- Define the Indicies
    if stage_num == 0:
        start_idx = 0
    else:
        start_idx = Analysis['Stages']['End Index']['Value'][stage_num-1]+1
    end_idx = Analysis['Stages']['End Index']['Value'][stage_num]

    # -- Set time, strain, transverse strain, and stress
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

    # -- Set filtered, reduced arrays
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
#   COMPRESSIVE ANALYSIS
#   Compressive Stage Analysis
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # FLIP STRAIN AND STRESS FOR TENSILE CODE TO WORK
    strain = -strain
    stress = -stress
    if len(diamstrain) != 0:
        diamstrain = -diamstrain

    if stage_num == 0:
        # Strain and Stress Rate
        if strain_rate_fit > stress_rate_fit:
            Analysis['Compressive Analysis']['Compressive Strain Rate']['Value'] = strain_rate
            Analysis['Compressive Analysis']['Compressive Stress Rate']['Value'] = None
        else:
            Analysis['Compressive Analysis']['Compressive Strain Rate']['Value'] = None
            Analysis['Compressive Analysis']['Compressive Stress Rate']['Value'] = stress_rate

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Linear Elastic Behavior
    #   Automatically calculate elastic modulus and proportional limit
    #
    # Import Linear Analysis Module

    mod, prop, prop_e, PR, lin_idx, mod_info = Linear_Analysis(strain, stress, diamstrain)

    # Save First Stage Info
    if stage_num == 0:
        if user_opts['UserEdit']['Modulus'] == 0:
            Analysis['Compressive Analysis']['Compressive Modulus-' + dir]['Value'] = mod
        if user_opts['UserEdit']['Prop'] == 0:
            Analysis['Compressive Analysis']['Compressive Proportional Limit-' + dir]['Value'] = prop
            Analysis['Compressive Analysis']['Compressive Proportional Limit Strain-' + dir]['Value'] = prop_e
        Analysis['Compressive Analysis']['Compressive Poissons Ratio-'+pr_dir]['Value'] = PR

    # Save Any Stage Info
    Analysis['Stages']['Compressive Analysis']['Compressive Modulus-' + dir]['Value'].append(mod)
    Analysis['Stages']['Compressive Analysis']['Compressive Proportional Limit-' + dir]['Value'].append(prop)
    Analysis['Stages']['Compressive Analysis']['Compressive Proportional Limit Strain-' + dir]['Value'].append(prop_e)
    Analysis['Stages']['Compressive Analysis']['Compressive Poissons Ratio-'+pr_dir]['Value'].append(PR)
        
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Yield Behavior
    #   Check if custom offset yield exist and store
    #
    if stage_num == 0:
        # Delete Previous Calculations
        Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Offset Strain']['Value'] = []
        Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'] = []
        Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Strain at Yield Strength']['Value'] = []

        if "Yield Offset" in list(user_opts.keys()):
            if lin_idx[1] < end_idx-start_idx:
                for i in range(len(user_opts["Yield Offset"])):
                    ystress, ystrain= CustomYield(strain, stress, Analysis['Compressive Analysis']['Compressive Modulus-' + dir]['Value'] , user_opts["Yield Offset"][i])
                    
                    if ystress != None:
                        if ystress < max(stress) and ystress > prop:
                            Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Offset Strain']['Value'].append(user_opts["Yield Offset"][i])
                            Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'].append(ystress)
                            Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Strain at Yield Strength']['Value'].append(ystrain)

    # Delete Previous Calculations
    Analysis['Stages']['Compressive Analysis']['Compressive Yield-' + dir]['Offset Strain']['Value'] = []
    Analysis['Stages']['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'] = []
    Analysis['Stages']['Compressive Analysis']['Compressive Yield-' + dir]['Strain at Yield Strength']['Value'] = []

    if "Yield Offset" in list(user_opts.keys()):
        if lin_idx[1] < end_idx-start_idx:
            for i in range(len(user_opts["Yield Offset"])):
                ystress, ystrain= CustomYield(strain, stress, Analysis['Compressive Analysis']['Compressive Modulus-' + dir]['Value'] , user_opts["Yield Offset"][i])
                    
                if ystress != None:
                    if ystress < max(stress) and ystress > prop:
                        Analysis['Stages']['Compressive Analysis']['Compressive Yield-' + dir]['Offset Strain']['Value'].append(user_opts["Yield Offset"][i])
                        Analysis['Stages']['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'].append(ystress)
                        Analysis['Stages']['Compressive Analysis']['Compressive Yield-' + dir]['Strain at Yield Strength']['Value'].append(ystrain)
                 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Ultimate Strength
    #
    # Save Max Strength Otherwise to Property Information if 1st Stage and tested to failure
    if stage_num == 0:
        if stage_num == len(Analysis['Stages']['Stage Name']['Value'])-1:
            if user_opts['Additional Information'][0] == 'Yes':
                Analysis['Compressive Analysis']['Compressive Ultimate Strength-' + dir]['Value'] = max(stress)
                Analysis['Compressive Analysis']['Compressive Strain at UTS-' + dir]['Value'] = strain[np.where(stress == max(stress))[0][0]]

    # Save Max Strength Otherwise to Stage Information
    Analysis['Stages']['Compressive Analysis']['Compressive Ultimate Strength-' + dir]['Value'].append(max(stress))
    Analysis['Stages']['Compressive Analysis']['Compressive Strain at UTS-' + dir]['Value'].append(strain[np.where(stress == max(stress))[0][0]])

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
                    if (stress[k]-stress[k-1])/Analysis['Compressive Analysis']['Compressive Ultimate Strength-'+dir]['Value'] < -0.5:
                        fail_idx = k
                        break

                Analysis['Compressive Analysis']['Compressive Failure Strength-'+dir]['Value'] = stress[fail_idx]
                Analysis['Compressive Analysis']['Compressive Strain at Failure-'+dir]['Value'] = strain[fail_idx]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PLOT
# Create additional plotting
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if stage_num == 0:
        if plot_opt == 1:
            # -- Plot the raw data
            plt.plot(strain,stress,'k',label = 'Raw Data')
            # -- Plot the linear fit
            if Analysis['Compressive Analysis']['Compressive Modulus-' + dir]['Value'] != None:
                strain_lin_end = (stress[-1]-stress[0])/Analysis['Compressive Analysis']['Compressive Modulus-' + dir]['Value']+strain[0]
                strain_lin = np.linspace(strain[0],strain_lin_end,100)
                stress_lin = strain_lin*mod_info.slope + mod_info.intercept
                plt.plot(strain_lin,stress_lin,'r--',label='Linear Fit')

            # -- Plot Proportional Limit
            if Analysis['Compressive Analysis']['Compressive Proportional Limit-' + dir]['Value'] != None:
                plt.plot(Analysis['Compressive Analysis']['Compressive Proportional Limit Strain-' + dir]['Value'],Analysis['Compressive Analysis']['Compressive Proportional Limit-' + dir]['Value'],'ro',label='Proportional Limit')

            # -- Plot Yield Behavior
            if Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'] != None:
                for i in range(len(Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'])):
                    plt.plot(Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Strain at Yield Strength']['Value'][i], Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Yield Strength']['Value'][i],'o',
                             label = str(Analysis['Compressive Analysis']['Compressive Yield-' + dir]['Offset Strain']['Value'][i]) + Raw['Raw Data']['Units']['Strain']['Value'] + ' Offset Yield') 

            # -- Plot Ultimate Strength
            if Analysis['Compressive Analysis']['Compressive Ultimate Strength-' + dir]['Value'] != None:
                plt.plot(Analysis['Compressive Analysis']['Compressive Strain at UTS-' + dir]['Value'], Analysis['Compressive Analysis']['Compressive Ultimate Strength-' + dir]['Value'],'mo',label='Ultimate Strength')

            # -- Plot Failure Strength
            if Analysis['Compressive Analysis']['Compressive Failure Strength-' + dir]['Value'] != None:
                plt.plot(Analysis['Compressive Analysis']['Compressive Strain at Failure-'+dir]['Value'],Analysis['Compressive Analysis']['Compressive Failure Strength-'+dir]['Value'],'co',label='Failure Strength')

            plt.legend()
            plt.xlabel('Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']')
            plt.ylabel('Stress [' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')
            plt.show()

    return Raw, Analysis
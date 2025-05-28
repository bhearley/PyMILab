#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Creep_Analysis.py
#
#   PURPOSE: Perform analysis on a creep segment
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
def Creep_Analysis(Raw, Analysis, dir, stage_num, user_opts, plot_opt):
    # Import Modules
    import numpy as np
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

    if len(Analysis['Stages']['Strain Rate-' + dir]['Value']) != len(Analysis['Stages']['Stage Name']['Value']):
        Analysis['Stages']['Strain Rate-' + dir]['Value'].append(strain_rate)
        Analysis['Stages']['Stress Rate-' + dir]['Value'].append(stress_rate)
    else:
        Analysis['Stages']['Strain Rate-' + dir]['Value'][stage_num] = strain_rate
        Analysis['Stages']['Stress Rate-' + dir]['Value'][stage_num] = stress_rate

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#   CREEP ANALYSIS
#   Creep Stage Analysis
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Set Flag for Loading Type
    # 0 - Preallocate
    # 1 - Tensile Creep
    # 2 - Compressive Creep
    # 3 - Shear Creep
    flag = 0
        
    # Determine Nominal Creep Stress
    creep_stress = round(np.average(stress),2)
    creep_time = time[-1] - time[0]

    # Identify Creep Zones
    if user_opts['UserEdit']['Creep'] == 0:
        # -- Set Flags
        prim_flag = 1
        sec_flag = 0
        tert_flag = 0

        #-- Find the true start of the creep zone (max in the first half of the data)
        dedt = np.gradient(np.gradient(strain, time),time)

        # Identify Creep Zones
        # -- Set Flags
        prim_flag = 1
        sec_flag = 0
        tert_flag = 0


        #-- Find the true start of the creep zone (max in the first half of the data)
        dedt = np.gradient(strain)
        max_val = max(dedt[0:int(0.5*len(dedt))])
        idx_start1 = np.where(dedt == max_val)[0][0]

        # -- Identify time and de/dt vectors (and filter)   
        time_crp = time[idx_start1:]
        time_crp = (time_crp-min(time_crp))/(max(time_crp)-min(time_crp))
        dedt = np.gradient(strain[idx_start1:],time_crp)
        dedt = savgol_filter(dedt, 51, 3)
        dedt = np.gradient(dedt,time_crp)
        dedt = savgol_filter(dedt, 51, 3)

        # Set the tolerance
        tol = -1E-5
        idx_start2 = np.where(dedt < -tol)[0][0]
        time_crp = time_crp[idx_start2:]
        dedt = dedt[idx_start2:]

        # Find the End of Primay Creep
        prim_end = len(time_crp) -1
        idx_temp = 0
        while idx_temp < len(time_crp):
            if dedt[idx_temp] > tol:
                prim_end = idx_temp
                sec_end = len(time_crp) -1
                sec_flag= 1
                break
            else:
                idx_temp = idx_temp+1

        # Find the end of secondary creep
        try:
            if sec_flag == 1:
                loc_max = argrelextrema(dedt[prim_end:], np.greater)
                if len(loc_max) > 0:
                    loc_min = argrelextrema(dedt[loc_max[0][0]:], np.less)
                    if len(loc_min) > 0:
                        idx_temp = prim_end + loc_min[0][0]

                # Calculate the new tolerance
                tol = max([0.1,1.5*max(dedt[idx_temp:idx_temp+10])])
                while idx_temp < len(time_crp):
                    if dedt[idx_temp] > tol:
                        sec_end = idx_temp
                        tert_end = len(time_crp) -1
                        tert_flag= 1
                        break
                    else:
                        idx_temp = idx_temp+1
        except:
            temp=1 # Do nothing

        # Identify the Creep Indices
        primary_idx= np.linspace(0,idx_start2+prim_end,idx_start2+prim_end+1,dtype=int)
        primary_rate = scipy.stats.linregress(time[int(primary_idx[0]):int(primary_idx[-1])], strain[int(primary_idx[0]):int(primary_idx[-1])])
        if sec_flag == 1:
            secondary_idx = np.linspace(idx_start2+prim_end+1,idx_start2+sec_end,(sec_end-prim_end),dtype=int)
            secondary_rate = scipy.stats.linregress(time[int(secondary_idx[0]):int(secondary_idx[-1])], strain[int(secondary_idx[0]):int(secondary_idx[-1])])
        else:
            secondary_idx = []
        if tert_flag == 1:
            tertiary_idx = np.linspace(idx_start2+sec_end+1,len(strain)-1,(len(strain)-1-idx_start2-sec_end),dtype=int)
            tertiary_rate = scipy.stats.linregress(time[int(tertiary_idx[0]):int(tertiary_idx[-1])], strain[int(tertiary_idx[0]):int(tertiary_idx[-1])])
        else:
            tertiary_idx = []


        # Get Type of Creep (Tensile, Shear, or Compressive Hold Stress)
        if creep_stress < -5: # Offset of -5 for noise
            flag = 2

            # - Overall
            if stage_num == 1:
            
                Analysis['Creep Analysis']['Compressive Creep Hold Stress-' + dir]['Value'] = creep_stress
                Analysis['Creep Analysis']['Compressive Creep Total Time']['Value'] = creep_time
                Analysis['Creep Analysis']['Compressive Creep Time']['Value'] = time
                Analysis['Creep Analysis']['Compressive Creep Strain-' + dir]['Value'] = strain
                Analysis['Creep Analysis']['Compressive Creep Stress-' + dir]['Value'] = stress

            Analysis['Stages']['Creep Analysis']['Compressive Creep Hold Stress-' + dir]['Value'].append(creep_stress)
            Analysis['Stages']['Creep Analysis']['Compressive Creep Total Time']['Value'].append(creep_time)
            Analysis['Stages']['Creep Analysis']['Compressive Creep Time']['Value'].append(time)
            Analysis['Stages']['Creep Analysis']['Compressive Creep Strain-' + dir]['Value'].append(strain)
            Analysis['Stages']['Creep Analysis']['Compressive Creep Stress-' + dir]['Value'].append(stress)

            # - Primary Creep
            if stage_num == 1:
                Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Time']['Value'] = time[int(primary_idx[0]):int(primary_idx[-1])]
                Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Strain']['Value'] = strain[int(primary_idx[0]):int(primary_idx[-1])]
                Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Stress']['Value'] = stress[int(primary_idx[0]):int(primary_idx[-1])]
                Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Index']['Value'] = primary_idx
                Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Strain Rate']['Value'] = primary_rate.slope

            Analysis['Stages']['Creep Analysis']['Compressive Primary Creep-' +dir]['Time']['Value'].append(time[int(primary_idx[0]):int(primary_idx[-1])])
            Analysis['Stages']['Creep Analysis']['Compressive Primary Creep-' +dir]['Strain']['Value'].append(strain[int(primary_idx[0]):int(primary_idx[-1])])
            Analysis['Stages']['Creep Analysis']['Compressive Primary Creep-' +dir]['Stress']['Value'].append(stress[int(primary_idx[0]):int(primary_idx[-1])])
            Analysis['Stages']['Creep Analysis']['Compressive Primary Creep-' +dir]['Index']['Value'].append(primary_idx)
            Analysis['Stages']['Creep Analysis']['Compressive Primary Creep-' +dir]['Strain Rate']['Value'].append(primary_rate.slope)

            # - Secondary Creep
            if len(secondary_idx) > 0:
                if stage_num == 1:
                    Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Time']['Value'] = time[int(secondary_idx[0]):int(secondary_idx[-1])]
                    Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Strain']['Value'] = strain[int(secondary_idx[0]):int(secondary_idx[-1])]
                    Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Stress']['Value'] = stress[int(secondary_idx[0]):int(secondary_idx[-1])]
                    Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Index']['Value'] = secondary_idx
                    Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Strain Rate']['Value'] = secondary_rate.slope

                Analysis['Stages']['Creep Analysis']['Compressive Secondary Creep-' +dir]['Time']['Value'].append(time[int(secondary_idx[0]):int(secondary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Compressive Secondary Creep-' +dir]['Strain']['Value'].append(strain[int(secondary_idx[0]):int(secondary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Compressive Secondary Creep-' +dir]['Stress']['Value'].append(stress[int(secondary_idx[0]):int(secondary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Compressive Secondary Creep-' +dir]['Index']['Value'].append(secondary_idx)
                Analysis['Stages']['Creep Analysis']['Compressive Secondary Creep-' +dir]['Strain Rate']['Value'].append(secondary_rate.slope)

            # - Tertiary Creep
            if len(tertiary_idx) > 0:
                if stage_num == 1:
                    Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Time']['Value'] = time[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                    Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Strain']['Value'] = strain[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                    Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Stress']['Value'] = stress[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                    Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Index']['Value'] = tertiary_idx
                    Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Strain Rate']['Value'] = tertiary_rate.slope

                Analysis['Stages']['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Time']['Value'].append(time[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Strain']['Value'].append(strain[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Stress']['Value'].append(stress[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Index']['Value'].append(tertiary_idx)
                Analysis['Stages']['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Strain Rate']['Value'].append(tertiary_rate.slope)
        else:
            if dir[0] == dir[1]:
                flag = 1

                # - Overall
                if stage_num == 1:
                    Analysis['Creep Analysis']['Creep Hold Stress-' + dir]['Value'] = creep_stress
                    Analysis['Creep Analysis']['Creep Total Time']['Value'] = creep_time
                    Analysis['Creep Analysis']['Creep Time']['Value'] = time
                    Analysis['Creep Analysis']['Creep Strain-' + dir]['Value'] = strain
                    Analysis['Creep Analysis']['Creep Stress-' + dir]['Value'] = stress

                Analysis['Stages']['Creep Analysis']['Creep Hold Stress-' + dir]['Value'].append(creep_stress)
                Analysis['Stages']['Creep Analysis']['Creep Total Time']['Value'].append(creep_time)
                Analysis['Stages']['Creep Analysis']['Creep Time']['Value'].append(time)
                Analysis['Stages']['Creep Analysis']['Creep Strain-' + dir]['Value'].append(strain)
                Analysis['Stages']['Creep Analysis']['Creep Stress-' + dir]['Value'].append(stress)

                # - Primary Creep
                if stage_num == 1:
                    Analysis['Creep Analysis']['Primary Creep-' +dir]['Time']['Value'] = time[int(primary_idx[0]):int(primary_idx[-1])]
                    Analysis['Creep Analysis']['Primary Creep-' +dir]['Strain']['Value'] = strain[int(primary_idx[0]):int(primary_idx[-1])]
                    Analysis['Creep Analysis']['Primary Creep-' +dir]['Stress']['Value'] = stress[int(primary_idx[0]):int(primary_idx[-1])]
                    Analysis['Creep Analysis']['Primary Creep-' +dir]['Index']['Value'] = primary_idx
                    Analysis['Creep Analysis']['Primary Creep-' +dir]['Strain Rate']['Value'] = primary_rate.slope

                Analysis['Stages']['Creep Analysis']['Primary Creep-' +dir]['Time']['Value'].append(time[int(primary_idx[0]):int(primary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Primary Creep-' +dir]['Strain']['Value'].append(strain[int(primary_idx[0]):int(primary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Primary Creep-' +dir]['Stress']['Value'].append(stress[int(primary_idx[0]):int(primary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Primary Creep-' +dir]['Index']['Value'].append(primary_idx)
                Analysis['Stages']['Creep Analysis']['Primary Creep-' +dir]['Strain Rate']['Value'].append(primary_rate.slope)

                # - Secondary Creep
                if len(secondary_idx) > 0:
                    if stage_num == 1:
                        Analysis['Creep Analysis']['Secondary Creep-' +dir]['Time']['Value'] = time[int(secondary_idx[0]):int(secondary_idx[-1])]
                        Analysis['Creep Analysis']['Secondary Creep-' +dir]['Strain']['Value'] = strain[int(secondary_idx[0]):int(secondary_idx[-1])]
                        Analysis['Creep Analysis']['Secondary Creep-' +dir]['Stress']['Value'] = stress[int(secondary_idx[0]):int(secondary_idx[-1])]
                        Analysis['Creep Analysis']['Secondary Creep-' +dir]['Index']['Value'] = secondary_idx
                        Analysis['Creep Analysis']['Secondary Creep-' +dir]['Strain Rate']['Value'] = secondary_rate.slope

                    Analysis['Stages']['Creep Analysis']['Secondary Creep-' +dir]['Time']['Value'].append(time[int(secondary_idx[0]):int(secondary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Secondary Creep-' +dir]['Strain']['Value'].append(strain[int(secondary_idx[0]):int(secondary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Secondary Creep-' +dir]['Stress']['Value'].append(stress[int(secondary_idx[0]):int(secondary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Secondary Creep-' +dir]['Index']['Value'].append(secondary_idx)
                    Analysis['Stages']['Creep Analysis']['Secondary Creep-' +dir]['Strain Rate']['Value'].append(secondary_rate.slope)

                # - Tertiary Creep
                if len(tertiary_idx) > 0:
                    if stage_num == 1:
                        Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Time']['Value'] = time[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                        Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Strain']['Value'] = strain[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                        Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Stress']['Value'] = stress[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                        Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Index']['Value'] = tertiary_idx
                        Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Strain Rate']['Value'] = tertiary_rate.slope

                    Analysis['Stages']['Creep Analysis']['Tertiary Creep-' +dir]['Time']['Value'].append(time[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Tertiary Creep-' +dir]['Strain']['Value'].append(strain[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Tertiary Creep-' +dir]['Stress']['Value'].append(stress[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Tertiary Creep-' +dir]['Index']['Value'].append(tertiary_idx)
                    Analysis['Stages']['Creep Analysis']['Tertiary Creep-' +dir]['Strain Rate']['Value'].append(tertiary_rate.slope)
            else:
                flag = 3

                # - Overall
                if stage_num == 1:
                    Analysis['Creep Analysis']['Shear Creep Hold Stress-' + dir]['Value'] = creep_stress
                    Analysis['Creep Analysis']['Shear Creep Total Time']['Value'] = creep_time
                    Analysis['Creep Analysis']['Shear Creep Time']['Value'] = time
                    Analysis['Creep Analysis']['Shear Creep Strain-' + dir]['Value'] = strain
                    Analysis['Creep Analysis']['Shear Creep Stress-' + dir]['Value'] = stress

                Analysis['Stages']['Creep Analysis']['Shear Creep Hold Stress-' + dir]['Value'].append(creep_stress)
                Analysis['Stages']['Creep Analysis']['Shear Creep Total Time']['Value'].append(creep_time)
                Analysis['Stages']['Creep Analysis']['Shear Creep Time']['Value'].append(time)
                Analysis['Stages']['Creep Analysis']['Shear Creep Strain-' + dir]['Value'].append(strain)
                Analysis['Stages']['Creep Analysis']['Shear Creep Stress-' + dir]['Value'].append(stress)

                # - Primary Creep
                if stage_num == 1:
                    Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Time']['Value'] = time[int(primary_idx[0]):int(primary_idx[-1])]
                    Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Strain']['Value'] = strain[int(primary_idx[0]):int(primary_idx[-1])]
                    Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Stress']['Value'] = stress[int(primary_idx[0]):int(primary_idx[-1])]
                    Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Index']['Value'] = primary_idx
                    Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Strain Rate']['Value'] = primary_rate.slope

                Analysis['Stages']['Creep Analysis']['Shear Primary Creep-' +dir]['Time']['Value'].append(time[int(primary_idx[0]):int(primary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Shear Primary Creep-' +dir]['Strain']['Value'].append(strain[int(primary_idx[0]):int(primary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Shear Primary Creep-' +dir]['Stress']['Value'].append(stress[int(primary_idx[0]):int(primary_idx[-1])])
                Analysis['Stages']['Creep Analysis']['Shear Primary Creep-' +dir]['Index']['Value'].append(primary_idx)
                Analysis['Stages']['Creep Analysis']['Shear Primary Creep-' +dir]['Strain Rate']['Value'].append(primary_rate.slope)

                # - Secondary Creep
                if len(secondary_idx) > 0:
                    if stage_num == 1:
                        Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Time']['Value'] = time[int(secondary_idx[0]):int(secondary_idx[-1])]
                        Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Strain']['Value'] = strain[int(secondary_idx[0]):int(secondary_idx[-1])]
                        Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Stress']['Value'] = stress[int(secondary_idx[0]):int(secondary_idx[-1])]
                        Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Index']['Value'] = secondary_idx
                        Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Strain Rate']['Value'] = secondary_rate.slope

                    Analysis['Stages']['Creep Analysis']['Shear Secondary Creep-' +dir]['Time']['Value'].append(time[int(secondary_idx[0]):int(secondary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Shear Secondary Creep-' +dir]['Strain']['Value'].append(strain[int(secondary_idx[0]):int(secondary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Shear Secondary Creep-' +dir]['Stress']['Value'].append(stress[int(secondary_idx[0]):int(secondary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Shear Secondary Creep-' +dir]['Index']['Value'].append(secondary_idx)
                    Analysis['Stages']['Creep Analysis']['Shear Secondary Creep-' +dir]['Strain Rate']['Value'].append(secondary_rate.slope)

                # - Tertiary Creep
                if len(tertiary_idx) > 0:
                    if stage_num == 1:
                        Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Time']['Value'] = time[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                        Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Strain']['Value'] = strain[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                        Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Stress']['Value'] = stress[int(tertiary_idx[0]):int(tertiary_idx[-1])]
                        Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Index']['Value'] = tertiary_idx
                        Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Strain Rate']['Value'] = tertiary_rate.slope

                    Analysis['Stages']['Creep Analysis']['Shear Tertiary Creep-' +dir]['Time']['Value'].append(time[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Shear Tertiary Creep-' +dir]['Strain']['Value'].append(strain[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Shear Tertiary Creep-' +dir]['Stress']['Value'].append(stress[int(tertiary_idx[0]):int(tertiary_idx[-1])])
                    Analysis['Stages']['Creep Analysis']['Shear Tertiary Creep-' +dir]['Index']['Value'].append(tertiary_idx)
                    Analysis['Stages']['Creep Analysis']['Shear Tertiary Creep-' +dir]['Strain Rate']['Value'].append(tertiary_rate.slope)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PLOT
# Create additional plotting
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if stage_num == 1:
        if plot_opt == 1:
            # Plot Stress Strain
            plt.subplot(1, 2, 1)
            plt.plot(np.array(Raw['Raw Data']['Strain-' + dir]['Value'][0:end_idx+1]), np.array(Raw['Raw Data']['Stress-' + dir]['Value'][0:end_idx+1]), 'k', label = 'Raw Data')
            plt.plot([0, max(strain)],[creep_stress, creep_stress],'r--',label = 'Creep Stress')

            plt.legend()
            plt.xlabel('Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']')
            plt.ylabel('Stress [' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')

            # Plot Creep Zones
            plt.subplot(1, 2, 2)
            if flag == 1:
                # Tensile
                if Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
                    plt.plot(Analysis['Creep Analysis']['Primary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Primary Creep-' +dir]['Strain']['Value'],'b',label = 'Primary Creep')
                    if secondary_idx != []:
                        plt.plot(Analysis['Creep Analysis']['Secondary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Secondary Creep-' +dir]['Strain']['Value'],'r',label = 'Secondary Creep')
                    if tertiary_idx != []:
                        plt.plot(Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Tertiary Creep-' +dir]['Strain']['Value'],'g',label = 'Tertiary Creep')

                # Compressive
                if Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
                    plt.plot(Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Compressive Primary Creep-' +dir]['Strain']['Value'],'b',label = 'Primary Creep')
                    if secondary_idx != []:
                        plt.plot(Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Compressive Secondary Creep-' +dir]['Strain']['Value'],'r',label = 'Secondary Creep')
                    if tertiary_idx != []:
                        plt.plot(Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Compressive Tertiary Creep-' +dir]['Strain']['Value'],'g',label = 'Tertiary Creep')

                # Shear
                if Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
                    plt.plot(Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Shear Primary Creep-' +dir]['Strain']['Value'],'b',label = 'Primary Creep')
                    if secondary_idx != []:
                        plt.plot(Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Shear Secondary Creep-' +dir]['Strain']['Value'],'r',label = 'Secondary Creep')
                    if tertiary_idx != []:
                        plt.plot(Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Time']['Value'], Analysis['Creep Analysis']['Shear Tertiary Creep-' +dir]['Strain']['Value'],'g',label = 'Tertiary Creep')

            plt.legend()
            plt.xlabel('Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']')
            plt.ylabel('Strain Rate [' + Raw['Raw Data']['Units']['Strain']['Value']+ '/' + Raw['Raw Data']['Units']['Time']['Value']+ ']')
            plt.show()
   
    return Raw, Analysis
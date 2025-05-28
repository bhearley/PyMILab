#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   DefinedSegmentation.py
#
#   PURPOSE: Perform segmentation defined by user
#
#   INPUTS:
#       Raw      = Raw Data Dictionary
#       Analysis = Analysis Dictionary
#       dir      = Test Direction (e.g., 11, 22, etc.)
#   OUTPUTS:
#       Analysis = Populated Stages Dictionary
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def DefinedSegmentation(Raw, Analysis, dir):
    # Import Modules
    import numpy as np
    import scipy.stats

    # Loop Through Defined Stages
    for i in range(len(Analysis['Stages']['End Index']['Value'])):
        # Rename all of the stages
        Analysis['Stages']['Stage Name']['Value'][i] = 'Stage_' + str(i)

        if Analysis['Stages']['Control Mode']['Value'][i] == None or Analysis['Stages']['Control Mode']['Value'][i] == '':
            # Know no information - Perform Automatic Analysis on the Segment
            if i == 0:
                start_idx = 0
            else:
                start_idx = Analysis['Stages']['End Index']['Value'][i-1]
            if i == len(Analysis['Stages']['Control Mode']['Value'])-1:
                end_idx = len(Raw['Raw Data']['Time']['Value'])-1
            else:
                end_idx = Analysis['Stages']['End Index']['Value'][i]

            # Define Vectors
            time = Raw['Raw Data']['Time']['Value'][start_idx:end_idx]
            strain = Raw['Raw Data']['Strain-'+dir]['Value'][start_idx:end_idx]
            stress = Raw['Raw Data']['Stress-'+dir]['Value'][start_idx:end_idx]

            # Get Control Mode
            # Calculate Strain Rate and Stress Rate
            strain_rate_info = scipy.stats.linregress(time, strain)
            strain_rate = strain_rate_info.slope
            strain_rate_fit = strain_rate_info.rvalue

            stress_rate_info = scipy.stats.linregress(time, stress)
            stress_rate = stress_rate_info.slope
            stress_rate_fit = stress_rate_info.rvalue

            if strain_rate_fit > stress_rate_fit:
                Analysis['Stages']['Control Mode']['Value'][i] = 'Strain'
            else:
                Analysis['Stages']['Control Mode']['Value'][i] = 'Stress'

            if Analysis['Stages']['Control Mode']['Value'][i] == 'Stress':
                # Check for constant stress
                if abs(stress_rate) < 1e-4:
                    Analysis['Stages']['Stage Type']['Value'][i] = 'Creep'
                    Analysis['Stages']['Target Stress-'+dir]['Value'][i] = round(np.average(np.array(stress)))
                else:
                    if stress_rate > 0 and stress[-1] > 0:
                        if dir[0] == dir[1]:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Tensile Loading'
                        else:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Shear Loading'
                    elif stress_rate > 0 and stress[-1] < 0:
                        Analysis['Stages']['Stage Type']['Value'][i] = 'Compressive Unloading'
                    elif stress_rate < 0 and stress[-1] > 0:
                        if dir[0] == dir[1]:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Tensile Unloading'
                        else:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Shear Unloading'
                    if stress_rate < 0 and stress[-1] < 0:
                        Analysis['Stages']['Stage Type']['Value'][i] = 'Compressive Loading'
                    Analysis['Stages']['Target Stress-'+dir]['Value'][i] = round(stress[-1])
            else:
                # Check for constant strain
                if abs(strain_rate) < 1e-8:
                    Analysis['Stages']['Stage Type']['Value'][i] = 'Relaxation'
                    Analysis['Stages']['Target Strain-'+dir]['Value'][i] = round(np.average(np.array(strain)))
                else:
                    if strain_rate > 0 and strain[-1] > 0:
                        if dir[0] == dir[1]:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Tensile Loading'
                        else:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Shear Loading'
                    elif strain_rate > 0 and strain[-1] < 0:
                        Analysis['Stages']['Stage Type']['Value'][i] = 'Compressive Unloading'
                    elif strain_rate < 0 and strain[-1] > 0:
                        if dir[0] == dir[1]:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Tensile Unloading'
                        else:
                            Analysis['Stages']['Stage Type']['Value'][i] = 'Shear Unloading'
                    if strain_rate < 0 and strain[-1] < 0:
                        Analysis['Stages']['Stage Type']['Value'][i] = 'Compressive Loading'
                    Analysis['Stages']['Target Strain-'+dir]['Value'][i] = round(strain[-1])

    return Raw, Analysis
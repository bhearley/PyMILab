#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   AssistedSegmentation.py
#
#   PURPOSE: Perform segmentation with known control mode and target values
#
#   INPUTS:
#       Raw      = Raw Data Dictionary
#       Analysis = Analysis Dictionary
#       dir      = Test Direction (e.g., 11, 22, etc.)
#   OUTPUTS:
#       Analysis = Populated Stages Dictionary
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def AssistedSegmentation(Raw, Analysis, dir):
    # Import Modules
    import numpy as np
    from scipy.signal import argrelextrema

    # Import Function
    from Segmentation.KneePoint import KneePoint

    # Initialize Previous Index
    idx_prev = 0
    target_stress_prev = 0
    target_strain_prev = 0

    # Loop through defined turn points
    for i in range(len(Raw['Control Information']['Control Mode']['Value'])):
        # -- Identify the control method and target value
        control_method = Raw['Control Information']['Control Mode']['Value'][i]
        control_var_opts = ['Target Time',
                            'Target Strain-11','Target Strain-22','Target Strain-33','Target Strain-12','Target Strain-13','Target Strain-23',
                            'Target Stress-11','Target Stress-22','Target Stress-33','Target Stress-12','Target Stress-13','Target Stress-23',
                            'Target Temperature']
        for j in range(len(control_var_opts)):
            if len(Raw['Control Information'][control_var_opts[j]]['Value']) > 0 and np.isnan(Raw['Control Information'][control_var_opts[j]]['Value'][i]) == False:
                target_val = Raw['Control Information'][control_var_opts[j]]['Value'][i]
                target_var = control_var_opts[j][len('Target '):]

        # -- CASE 1A: LOAD (Stress Target)
        if 'Stress' in target_var and target_val > target_stress_prev:
            # Set the target value with tolerance
            target_val_tol = target_val *0.95

            # Find the first instance where the target value is found
            temp_idx = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])>=target_val_tol)
            if len(temp_idx[0]) > 0:
                idx = temp_idx[0][0]+idx_prev

                # Look 5% forward to determine if a local maximum exists
                span = idx-idx_prev
                fval = Raw['Raw Data'][target_var]['Value'][int(idx+0.1*span)]
                if fval > 1.05*target_val:
                    # Load up continues - find the first instance where the true target is met
                    idx_opt = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])>=target_val)[0][0]+idx_prev
                else:
                    # Load is either steady or reversed - find the first local maximum
                    loc_max = argrelextrema(np.array(Raw['Raw Data'][target_var]['Value'][idx:]), np.greater)
                    if len(loc_max[0]) > 0:
                        loc_max = loc_max[0][0]
                    else:
                        loc_max = 0
                    idx_opt = idx+loc_max
            else:
                idx_opt = len(Raw['Raw Data'][target_var]['Value'])-1

            if target_val < 0:
                StageType = 'Compressive Unloading'
            else:
                if dir[0] == dir[1]:
                    StageType = 'Tensile Loading'
                else:
                    StageType = 'Shear Loading'

        # -- CASE 1B: LOAD (Strain Target)
        if 'Strain' in target_var and target_val > target_strain_prev:
            # Set the target value with tolerance
            target_val_tol = target_val *0.95

            # Find the first instance where the target value is found
            temp_idx = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])>=target_val_tol)
            if len(temp_idx[0]) > 0:
                idx = temp_idx[0][0]+idx_prev

                # Look 5% forward to determine if a local maximum exists
                span = idx-idx_prev
                chk_val = int(idx+0.1*span)
                if chk_val > len(Raw['Raw Data'][target_var]['Value']):
                    chk_val = idx
                fval = Raw['Raw Data'][target_var]['Value'][chk_val]
                if fval > 1.05*target_val:
                    # Load up continues - find the first instance where the true target is met
                    idx_opt = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])>=target_val)[0][0]+idx_prev
                else:
                    # Load is either steady or reversed - find the first local maximum
                    loc_max = argrelextrema(np.array(Raw['Raw Data'][target_var]['Value'][idx:]), np.greater)
                    if len(loc_max[0]) > 0:
                        loc_max = loc_max[0][0]
                    else:
                        loc_max = 0
                    idx_opt = idx+loc_max

            else:
                idx_opt = len(Raw['Raw Data'][target_var]['Value'])-1

            if target_val < 0:
                StageType = 'Compressive Unloading'
            else:
                if dir[0] == dir[1]:
                    StageType = 'Tensile Loading'
                else:
                    StageType = 'Shear Loading'


        # -- CASE 2A: UNLOAD (Stress Target)
        if 'Stress' in target_var and target_val < target_stress_prev:
            # Set the target value with tolerance
            target_val_tol = target_val *1.05

            # Find the first instance where the target value is found
            temp_idx = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])<=target_val_tol)
            if len(temp_idx[0]) > 0 :
                idx = temp_idx[0][0]+idx_prev
                # Look 5% forward to determine if a local maximum exists
                span = idx-idx_prev
                fval = Raw['Raw Data'][target_var]['Value'][int(idx+0.1*span)]
                if fval < 0.95*target_val:
                    # Unload continues - find the first instance where the true target is met
                    idx_opt = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])<=target_val)[0][0]+idx_prev
                else:
                    # Load is either steady or reversed - find the first local minimum
                    loc_min = argrelextrema(np.array(Raw['Raw Data'][target_var]['Value'][idx:]), np.less)
                    if len(loc_min[0]) > 0:
                        loc_min = loc_min[0][0]
                    else:
                        loc_min = 0
                    idx_opt = idx+loc_min
            else:
                idx_opt = len(Raw['Raw Data'][target_var]['Value'])-1

            if target_val < 0:
                StageType = 'Compressive Loading'
            else:
                if dir[0] == dir[1]:
                    StageType = 'Tensile Unloading'
                else:
                    StageType = 'Shear Unloading'

        # -- CASE 2B: UNLOAD (Strain Target)
        if 'Strain' in target_var and target_val < target_strain_prev:
            # Set the target value with tolerance
            target_val_tol = target_val *1.05


            # Find the first instance where the target value is found
            temp_idx = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])<=target_val_tol)
            if len(temp_idx[0]) > 0 :
                idx = temp_idx[0][0]+idx_prev
                if i == len(Raw['Control Information']['Control Mode']['Value']):
                    idx = len(Raw['Raw Data']['Strain-' + dir]['Value'])

                # Look 5% forward to determine if a local maximum exists
                span = idx-idx_prev
                fval = Raw['Raw Data'][target_var]['Value'][int(idx+0.1*span)]
                if fval < 0.95*target_val:
                    # Unload continues - find the first instance where the true target is met
                    idx_opt = np.where(np.array(Raw['Raw Data'][target_var]['Value'][idx_prev:])<=target_val)[0][0]+idx_prev
                else:
                    # Load is either steady or reversed - find the first local minimum
                    loc_min = argrelextrema(np.array(Raw['Raw Data'][target_var]['Value'][idx:]), np.less)
                    if len(loc_min[0]) > 0:
                        loc_min = loc_min[0][0]
                    else:
                        loc_min = 0
                    idx_opt = idx+loc_min
            else:
                idx_opt = len(Raw['Raw Data'][target_var]['Value'])-1

            if target_val < 0:
                StageType = 'Compressive Loading'
            else:
                if dir[0] == dir[1]:
                    StageType = 'Tensile Unloading'
                else:
                    StageType = 'Shear Unloading'

        # -- CASE 3: CONSTANT STRESS (Time Target)
        if 'Time' in target_var and control_method == 'Stress':
            # Find where the load begins to go up or down
            stress_vec = np.absolute(np.array(Raw['Raw Data']['Stress-' + dir]['Value'][idx_prev:]) - target_stress_prev)
            temp_idx = np.where(stress_vec>=target_stress_prev*0.05)
            if len(temp_idx[0]) > 0:
                idx = temp_idx[0][0]+idx_prev
                if i+1 == len(Raw['Control Information']['Control Mode']['Value']):
                    idx = len(Raw['Raw Data']['Stress-' + dir]['Value'])-1

                # Condition data for Knee Point Algorithm
                x = np.linspace(idx_prev,idx,idx-idx_prev)
                y = np.array(Raw['Raw Data']['Stress-' + dir]['Value'][idx_prev:idx])
                # -- Mirror X Only
                if Raw['Raw Data']['Stress-'+dir]['Value'][idx] < Raw['Raw Data']['Stress-'+dir]['Value'][idx_prev]:
                    x = x[0] - (x-x[0])
                # -- Mirror X and Y
                else:
                    x = x[0] - (x-x[0])
                    y = y[0] - (y-y[0])

                # Run Knee Point Algorithm
                from Segmentation.KneePoint import KneePoint
                idx_knee = KneePoint(x,y)

                # Update Stage Index
                idx_opt = idx_prev + idx_knee[0][0]

            else:
                idx_opt = len(Raw['Raw Data'][target_var]['Value'])-1

            StageType = 'Creep'

        # -- CASE 3: CONSTANT STRAIN (Time Target)
        if 'Time' in target_var and control_method == 'Strain':
            # Find where the load begins to go up or down
            strain_vec = np.absolute(np.array(Raw['Raw Data']['Strain-' + dir]['Value'][idx_prev:]) - target_strain_prev)
            temp_idx = np.where(strain_vec>=target_strain_prev*0.05)
            if len(temp_idx[0]) > 0:
                idx = temp_idx[0][0]+idx_prev

                # Condition data for Knee Point Algoirthm
                x = np.linspace(idx_prev,idx,idx-idx_prev)
                y = np.array(Raw['Raw Data']['Strain-' + dir]['Value'][idx_prev:idx])
                # -- Mirror X Only
                if Raw['Raw Data']['Strain-' + dir]['Value'][idx] < Raw['Raw Data']['Strain-' + dir]['Value'][idx_prev]:
                    x = x[0] - (x-x[0])
                # -- Mirror X and Y
                else:
                    x = x[0] - (x-x[0])
                    y = y[0] - (y-y[0])

                # Run Knee Point Algorithm
                idx_knee = KneePoint(x,y)

                # Update Stage Index
                idx_opt = idx_prev + idx_knee[0][0]

            else:
                idx_opt = len(Raw['Raw Data'][target_var]['Value'])-1

            StageType = 'Relaxation'

        # Populate Stage Table
        if Raw['Control Information']['Stage Name']['Value'] != []:
            Analysis['Stages']['Stage Name']['Value'].append(Raw['Control Information']['Stage Name']['Value'][i])
        else:
            Analysis['Stages']['Stage Name']['Value'].append('Stage_' + str(i))

        Analysis['Stages']['Stage Type']['Value'].append(StageType)
        Analysis['Stages']['Control Mode']['Value'].append(Raw['Control Information']['Control Mode']['Value'][i])
        Analysis['Stages']['End Index']['Value'].append(idx_opt)
        for j in range(len(control_var_opts)):
            if control_var_opts[j] == target_var:
                Analysis['Stages'][control_var_opts[j]]['Value'].append(target_val)
            else:
                Analysis['Stages'][control_var_opts[j]]['Value'].append(None)

        # Reset the index
        idx_prev = idx_opt
        target_strain_prev = Raw['Raw Data']['Strain-' + dir]['Value'][idx_opt]
        target_stress_prev = Raw['Raw Data']['Stress-' + dir]['Value'][idx_opt]

    # Set the Last Stage End Index
    Analysis['Stages']['End Index']['Value'][len(Raw['Control Information']['Control Mode']['Value'])-1] = len(Raw['Raw Data']['Time']['Value'])-1

    # Write the Target Information
    Analysis['Stages']['Target Time']['Value'] = Raw['Control Information']['Target Time']['Value']
    Analysis['Stages']['Target Strain-' + dir]['Value'] = Raw['Control Information']['Target Strain-' + dir]['Value']
    Analysis['Stages']['Target Stress-' + dir]['Value'] = Raw['Control Information']['Target Stress-' + dir]['Value']

    return Raw, Analysis
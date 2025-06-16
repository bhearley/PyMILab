#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   RawSegmentation.py
#
#   PURPOSE: Perform segmentation with known control mode and target values
#
#   INPUTS:
#       Raw        Raw Data Dictionary
#       Analysis   Analysis Dictionary
#       dir        Test Direction (e.g., 11, 22, etc.)
#   OUTPUTS:
#       Analysis   Populated Stages Dictionary
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def RawSegmentation(Raw, Analysis, dir):
    # Import Modules
    import numpy as np
    import scipy.stats
    from Segmentation.KneePoint import KneePoint

    # Get Index, Time, Strain, and Stress Vectors
    time = np.array(Raw['Raw Data']['Time']['Value'])
    strain = Raw['Raw Data']['Strain-' + dir]['Value']
    stress = Raw['Raw Data']['Stress-'+dir]['Value']

    index = np.linspace(0,len(time)-1, len(time), dtype=int)
    Raw['Raw Data']['Index']['Value'] = index

    # Filter the Data
    from scipy.signal import savgol_filter
    strain = savgol_filter(strain, 51, 3) # window size 51, polynomial order 3
    stress = savgol_filter(stress, 51, 3) # window size 51, polynomial order 3

    # Find end of each stage
    step = int(0.005*max(index))
    minmax_step = 3*step
    start_idx = step
    end_idx = int(3/2*step)
    stage_idx = []
    ct = 0 # Counter for stage name
    const_flag = 0 #Is the current stage constant stress or strain
    max_flag = 0 #Indicates if max index has been reached
    step_vals = []

    while end_idx < max(index):
        if const_flag == 0:
            # Start at start index and find whether stress or strain deviates from linear wrt time first
            lin_flag = 0
            while lin_flag == 0:
                step_vals.append(end_idx)
                # -- Get Linear fits and evaluate linearity
                strain_fit = scipy.stats.linregress(time[start_idx:end_idx], strain[start_idx:end_idx])
                stress_fit = scipy.stats.linregress(time[start_idx:end_idx], stress[start_idx:end_idx])

                if strain_fit.rvalue**2 < 0.975 and stress_fit.rvalue**2 < 0.975:
                    lin_flag = 1

                # -- Update end index
                end_idx = end_idx + step
                if end_idx >= max(index):
                    end_idx = max(index)
                    max_flag = 1
                    break
        else:
            # Look for a 5% increase/decrease in stress and strain
            lin_flag = 0
            while lin_flag == 0:
                # -- Get Change in strain and stress
                if abs(strain[end_idx]/strain[start_idx]) < 0.95 or abs(strain[end_idx]/strain[start_idx]) > 1.05:
                    if abs(stress[end_idx]/stress[start_idx]) < 0.95 or abs(stress[end_idx]/stress[start_idx]) > 1.05:
                        if abs(stress[end_idx]) > 5:
                            lin_flag = 1

                # -- Update end index
                end_idx = end_idx + step
                if end_idx >= max(index):
                    end_idx = max(index)
                    max_flag = 1
                    break

        # Get the Segment Vectors
        xseg = np.array(time[start_idx:end_idx])

        if const_flag == 0:
            if strain_fit.rvalue**2 > stress_fit.rvalue**2:
                yseg = np.array(strain[start_idx:end_idx])
                control = 'Strain'
            else:
                yseg = np.array(stress[start_idx:end_idx])
                control = 'Stress'
        else:
            time_norm = np.array(time[start_idx:int((end_idx-start_idx)*0.5+start_idx)])
            time_norm = (time_norm-min(time))/(max(time)-min(time))

            strain_norm = np.array(strain[start_idx:int((end_idx-start_idx)*0.5+start_idx)])
            strain_norm = (strain_norm-min(strain))/(max(strain)-min(strain))

            stress_norm = np.array(stress[start_idx:int((end_idx-start_idx)*0.5+start_idx)])
            stress_norm = (stress_norm-min(stress))/(max(stress)-min(stress))

            strain_fit = scipy.stats.linregress(time_norm, strain_norm)
            stress_fit = scipy.stats.linregress(time_norm, stress_norm)

            if abs(strain_fit.slope) < abs(stress_fit.slope):
                yseg = np.array(strain[start_idx:end_idx])
                control = 'Strain'
            else:
                yseg = np.array(stress[start_idx:end_idx])
                control = 'Stress'


        # Determine the Stage Fit Type
        # -- See Documentation for 6 Stage Types
        if yseg[0] < yseg[-1]:
            if const_flag == 1:
                fit_type = 3
            elif abs(max(yseg)/yseg[-1]) > 0.95 and abs(max(yseg)/yseg[-1]) < 1.05:
                fit_type = 2
            else:
                fit_type = 1
        else:
            if const_flag == 1:
                fit_type = 6
            elif abs(yseg[0]/yseg[int(0.1*len(yseg))]) > 0.95 and abs(yseg[0]/yseg[int(0.1*len(yseg))]) < 1.05:
                fit_type = 5
            else:
                fit_type = 4

        # Get the Stage End for Each Fit Type
        if fit_type == 1:
            end_stage = np.where(yseg==max(yseg))[0][0]
            if yseg[0] < -1:
                stage_type = 'Compressive Unloading'
            else:
                if dir[0] == dir[1]:
                    stage_type = 'Tensile Loading'
                else:
                    stage_type = 'Shear Loading'
            const_flag = 0

        if fit_type == 2:
            # - Run Knee Point
            knee = KneePoint(xseg,yseg)[0][0]

            # -- Check for Local Max near knee
            lmax = np.where(yseg[knee-step:knee+minmax_step] == max(yseg[knee-step:knee+minmax_step]))
            if len(lmax[0]) > 0:
                end_stage = knee-step + lmax[0][0]
            else:
                end_stage = knee

            if yseg[0] < -1:
                stage_type = 'Compressive Unloading'
            else:
                if dir[0] == dir[1]:
                    stage_type = 'Tensile Loading'
                else:
                    stage_type = 'Shear Loading'
            const_flag = 1

        if fit_type == 3:
            # - Flip Horizontally
            xseg_temp = []
            for k in range(len(xseg)):
                d = xseg[k]-xseg[0]
                xseg_temp.append(xseg[k]-2*d)
            xseg = np.array(xseg_temp)

            # - Flip Vertically
            yseg_temp = []
            for k in range(len(yseg)):
                d = yseg[k]-yseg[0]
                yseg_temp.append(yseg[k]-2*d)
            yseg = np.array(yseg_temp)

            # - Run Knee Point
            knee = KneePoint(xseg,yseg)[0][0]

            # -- Check for Local Max near knee
            lmax = np.where(yseg[knee-step:knee+minmax_step] == max(yseg[knee-step:knee+minmax_step]))
            if len(lmax[0]) > 0:
                end_stage = knee-step + lmax[0][0]
            else:
                end_stage = knee

            if control == 'Strain':
                stage_type = 'Relaxation'
            else:
                stage_type = 'Creep'
            const_flag = 0

        if fit_type == 4:
            end_stage = np.where(yseg==min(yseg))[0][0]

            if yseg[end_stage] < -1:
                stage_type = 'Compressive Loading'
            else:
                if dir[0] == dir[1]:
                    stage_type = 'Tensile Unloading'
                else:
                    stage_type = 'Shear Unloading'
            const_flag = 0

        if fit_type == 5:
            # - Flip Vertically
            yseg_temp = []
            for k in range(len(yseg)):
                d = yseg[k]-yseg[0]
                yseg_temp.append(yseg[k]-2*d)
            yseg = np.array(yseg_temp)

            # - Run Knee Point
            knee = KneePoint(xseg,yseg)[0][0]

            # -- Check for Local Max near knee
            lmax = np.where(yseg[knee-step:knee+minmax_step] == max(yseg[knee-step:knee+minmax_step]))
            if len(lmax[0]) > 0:
                end_stage = knee-step + lmax[0][0]
            else:
                end_stage = knee

            if yseg[end_stage] < -1:
                stage_type = 'Compressive Loading'
            else:
                if dir[0] == dir[1]:
                    stage_type = 'Tensile Unloading'
                else:
                    stage_type = 'Shear Unloading'
            const_flag = 1

        if fit_type == 6:
            # - Flip Horizontally
            xseg_temp = []
            for k in range(len(xseg)):
                d = xseg[k]-xseg[0]
                xseg_temp.append(xseg[k]-2*d)
            xseg = np.array(xseg_temp)

            # - Run Knee Point
            knee = KneePoint(xseg,yseg)[0][0]

            # -- Check for Local Max near knee
            lmax = np.where(yseg[knee-step:knee+minmax_step] == max(yseg[knee-step:knee+minmax_step]))
            if len(lmax[0]) > 0:
                end_stage = knee-step + lmax[0][0]
            else:
                end_stage = knee

            if control == 'Strain':
                stage_type = 'Relaxation'
            else:
                stage_type = 'Creep'
            const_flag = 0

        # Populate Stage Table
        
        if Raw['Control Information']['Stage Name']['Value'] != []:
            Analysis['Stages']['Stage Name']['Value'].append(Raw['Control Information']['Stage Name']['Value'][ct])
        else:
            Analysis['Stages']['Stage Name']['Value'].append('Stage_' + str(ct))

        Analysis['Stages']['Stage Type']['Value'].append(stage_type)
        Analysis['Stages']['Control Mode']['Value'].append(control)
        if max_flag == 1:
            end_stage = max(index) - start_idx
        Analysis['Stages']['End Index']['Value'].append(end_stage+start_idx)

        stage_idx.append(end_stage+start_idx)

        # Reset Start and Stop
        start_idx = end_stage + start_idx + 2*step
        end_idx = start_idx + step
        ct = ct+1

    return Raw, Analysis
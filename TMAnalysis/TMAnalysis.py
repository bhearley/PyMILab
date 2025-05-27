#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   TMAnalysis.py
#   Brandon Hearley - NASA GRC - LMS
#   6/13/24
#
#   PURPOSE: Perform automatic segmentation and analysis of thermomechanical tests
#
#   INPUTS:
#       Raw:          Raw Data JSON File
#       Analysis      Analysis JSON File or 0
#                       Enter 0 if it is a brand new analysis, or supply the analysis file if editing a previous analysis
#                       through the GUI
#       user_opts     Additional options input by the user (see documentation)
#   OUTPUTS:
#       Analysis      Analysis JSON File
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def TMAnalysis(Raw_file, Analysis_file, user_opts):
    # Import Modules
    import os
    import json
    import numpy as np
    import matplotlib.pyplot as plt

    # Set the plotting option
    # -- 0 - no plots
    # -- 1 - plots (for debugging/checking outside of GUI)
    plot_opt = 0
    if "plot" in list(user_opts.keys()):
        if user_opts["plot"] == True:
            plot_opt = 1

    # Open the Raw File
    f = open(Raw_file) 
    Raw = json.load(f) 

    # Open the Analysis File
    if Analysis_file == 0:
        # -- Open an empty Analysis File
        f = open(os.path.join(os.getcwd(),'Templates','Analysis_Template.json'))
    else:
        # -- Open an existing Analysis File
        f = open(Analysis_file)
    Analysis = json.load(f) 

    # Error Checking
    # -- To run the code, a vector must exist for either displacement or strain and load or stress in 1 of the 6 directions, 
    #    as well as time data
    err_flag = 0 # 0 = no error, 1 = errors (do not run analysis)
    err_msg = [] # empty list to store error messages

    # - For each direciton, check if displacement or strain is defined. If defined, check there is a corresponding load
    #   or stress vector. The chk value represents:
    #                       0 - neither displacement/strain or load/stress data is defined
    #                       1 - load/stress data is  present bt displacement/strain data is not present
    #                       2 - both displacement/strain or load/stress data is defined
    #  load_dir stores the found loading direction if there are no errors:
    #       1 - 11 direction
    #       2 - 22 direction
    #       3 - 33 direction
    #       4 - 23 direction
    #       5 - 13 direction
    #       6 - 12 direction

    load_dir = 0
    dir_opt = ['11','22','33','23','13','12']
    load_opt = ['Load-11','Load-22','Load-33','Load-23','Load-13','Load-12']
    stress_opt = ['Stress-11','Stress-22','Stress-33','Stress-23','Stress-13','Stress-12']
    disp_opt = ['Displacement-11','Displacement-22','Displacement-33','Deformation-23','Deformation-13','Deformation-12']
    strain_opt = ['Strain-11','Strain-22','Strain-33','Strain-23','Strain-13','Strain-12']

    # Check for Time Data
    if len(Raw['Raw Data']['Time']['Value']) < 1:
        err_flag = 1
        err_msg.append('No time data given')

    # Check for Load DAta
    for i in range(6):
        chk = 0
        if len(Raw['Raw Data'][load_opt[i]]['Value']) < 1:
            if len(Raw['Raw Data'][stress_opt[i]]['Value']) > 1:
                chk = 1
        else:
            chk = 1

        if chk == 1:
            if len(Raw['Raw Data'][disp_opt[i]]['Value']) < 1:
                if len(Raw['Raw Data'][strain_opt[i]]['Value']) > 1:
                    chk = 2
            else:
                chk = 2

        if chk == 2 and load_dir == 0:
            # Calculate Stress if necessary
            if len(Raw['Raw Data'][load_opt[i]]['Value']) > 1 and len(Raw['Raw Data'][stress_opt[i]]['Value']) < 1:
                if Raw['Specimen Information']['Gauge Area']['Value'] == None:
                    err_flag = 1
                    err_msg.append('Load is given in the ' + dir_opt[i] + ' direction, but no cross-secitonal area is given.')
                else:
                    Raw['Raw Data'][stress_opt[i]]['Value'] = Raw['Raw Data'][load_opt[i]]['Value']/Raw['Specimen Information']['Gauge Area']['Value'] 
                    Raw['Raw Data']['Units']['Stress']['Value'] = Raw['Raw Data']['Units']['Load']['Value']/Raw['Specimen Information']['Units']['Area']['Value']
                    # ~~~~ Future Feature - Add library of units (i.e., so that lb/in^2 -> psi)
            if len(Raw['Raw Data'][disp_opt[i]]['Value']) > 1 and len(Raw['Raw Data'][strain_opt[i]]['Value']) < 1:
                if Raw['Specimen Information']['Gauge Length']['Value'] == None:
                    err_flag = 1
                    err_msg.append('Displacement is given in the ' + dir_opt[i] + ' direction, but no gauage length is given.')
                else:
                    Raw['Raw Data'][disp_opt[i]]['Value'] = Raw['Raw Data'][disp_opt[i]]['Value']/Raw['Specimen Information']['Gauge Length']['Value'] 
                    Raw['Raw Data']['Units']['Strain']['Value'] = Raw['Raw Data']['Units']['Load']['Value']/Raw['Specimen Information']['Units']['Length']['Value']
                    # ~~~~ Future Feature - Add library of units (i.e., so that in/in -> -)
            if err_flag == 0:
                load_dir = dir_opt[i]

    # Segmentation
    if err_flag == 0:
        # -- Check if turn points are defined by the program
        if len(Analysis['Stages']['End Index']['Value']) > 0:
            # -- Call Defined Segmentation algorithm if user has them fully defined (i.e., Analysis file was input)
            from Segmentation.DefinedSegmentation import DefinedSegmentation
            Raw, Analysis = DefinedSegmentation(Raw, Analysis, load_dir)

        elif Raw['Control Information']['Defined']['Value'] == True:
            # -- Call Assisted Segmentation algorithm if turn points are defined
            from Segmentation.AssistedSegmentation import AssistedSegmentation
            Raw, Analysis = AssistedSegmentation(Raw, Analysis, load_dir)

        else:
            # -- Call Raw Segmentation algorithm if turn points are not defined
            from Segmentation.RawSegmentation import RawSegmentation
            Raw, Analysis = RawSegmentation(Raw, Analysis, load_dir)
  
        # Plot the Stages
        if plot_opt == 1:
            # -- Create the counters for each stage type
            TypeCt = {
            'Tensile Loading':1,
            'Tensile Unloading':1,
            'Compressive Loading':1,
            'Compresive Unloading':1,
            'Shear Loading':1,
            'Shear Unloading':1,
            'Creep':1,
            'Relaxation':1
            }

            # -- Create the plots
            fig, axs = plt.subplots(2,2)
            color_opts = ['royalblue','darkorange','limegreen','red','orchid','maroon','deeppink','steelblue','saddlebrown']
            color_ct = 0
            strain_scale = max(np.array(Raw['Raw Data']['Strain-' + load_dir]['Value']))
            stress_scale = max(np.array(Raw['Raw Data']['Stress-' + load_dir]['Value']))

            for k in range(len(Analysis['Stages']['Stage Name']['Value'])):
                color = color_opts[color_ct]
                if k == 0:
                    idx_prev = 0
                else:
                    idx_prev = Analysis['Stages']['End Index']['Value'][k-1]
                index = np.linspace(idx_prev,Analysis['Stages']['End Index']['Value'][k],Analysis['Stages']['End Index']['Value'][k]-idx_prev)
                time  = np.array(Raw['Raw Data']['Time']['Value'][idx_prev:Analysis['Stages']['End Index']['Value'][k]])
                strain = np.array(Raw['Raw Data']['Strain-' + load_dir]['Value'][idx_prev:Analysis['Stages']['End Index']['Value'][k]])
                stress = np.array(Raw['Raw Data']['Stress-' + load_dir]['Value'][idx_prev:Analysis['Stages']['End Index']['Value'][k]])
                axs[0,0].plot(strain,stress,label = Analysis['Stages']['Stage Type']['Value'][k] + ' ' + str(TypeCt[Analysis['Stages']['Stage Type']['Value'][k]]), color = color)
                axs[0,1].plot(time,stress,label = Analysis['Stages']['Stage Type']['Value'][k] + ' ' + str(TypeCt[Analysis['Stages']['Stage Type']['Value'][k]]), color = color)
                axs[1,0].plot(time,strain,label = Analysis['Stages']['Stage Type']['Value'][k] + ' ' + str(TypeCt[Analysis['Stages']['Stage Type']['Value'][k]]),linestyle='dashed', color = color)
                axs[1,1].plot(index,stress/stress_scale,label = Analysis['Stages']['Stage Type']['Value'][k] + ' ' + str(TypeCt[Analysis['Stages']['Stage Type']['Value'][k]]), color = color)
                axs[1,1].plot(index,strain/strain_scale,label = Analysis['Stages']['Stage Type']['Value'][k] + ' ' + str(TypeCt[Analysis['Stages']['Stage Type']['Value'][k]]), linestyle='dashed', color = color)
                TypeCt[Analysis['Stages']['Stage Type']['Value'][k]] = TypeCt[Analysis['Stages']['Stage Type']['Value'][k]]+1
                color_ct = color_ct + 1
                if color_ct == len(color_opts):
                    color_ct = 0

            # -- Format the plots
            axs[0,0].set_xlabel('Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']')
            axs[0,0].set_ylabel('Stress [ ' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')
            axs[0,1].set_xlabel('Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']')
            axs[0,1].set_ylabel('Stress [ ' + Raw['Raw Data']['Units']['Stress']['Value']+ ']')
            axs[1,0].set_xlabel('Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']')
            axs[1,0].set_ylabel('Strain [ ' + Raw['Raw Data']['Units']['Strain']['Value']+ ']')
            axs[1,1].set_xlabel('Index')
            axs[1,1].set_ylabel('Normalized Stress and Strain')
            lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
            lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
            fig.legend(lines, labels[0:k+1], loc='upper center', ncol=4)
            plt.show()

        # Perform Stage Analysis given each type
        for i in range(len(Analysis['Stages']['Stage Name']['Value'])):
            # -- Tensile Loading
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Tensile Loading':
                from Analysis.TensileLoading_Analysis import TensileLoading_Analysis
                Raw, Analysis = TensileLoading_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Tensile Unloading
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Tensile Unloading':
                from Analysis.TensileUnloading_Analysis import TensileUnloading_Analysis
                Raw, Analysis = TensileUnloading_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Compressive Loading
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Compressive Loading':
                from Analysis.CompressiveLoading_Analysis import CompressiveLoading_Analysis
                Raw, Analysis = CompressiveLoading_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Compressive Unloading
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Compressive Unloading':
                from Analysis.CompressiveUnloading_Analysis import CompressiveUnloading_Analysis
                Raw, Analysis = CompressiveUnloading_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Shear Loading
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Shear Loading':
                from Analysis.ShearLoading_Analysis import ShearLoading_Analysis
                Raw, Analysis = ShearLoading_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Shear Unloading
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Shear Unloading':
                from Analysis.ShearUnloading_Analysis import ShearUnloading_Analysis
                Raw, Analysis = ShearUnloading_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Creep
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Creep':
                from Analysis.Creep_Analysis import Creep_Analysis
                Raw, Analysis = Creep_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)

            # -- Relaxation
            if Analysis['Stages']['Stage Type']['Value'][i] == 'Relaxation':
                from Analysis.Relaxation_Analysis import Relaxation_Analysis
                Raw, Analysis = Relaxation_Analysis(Raw, Analysis, load_dir, i, user_opts, plot_opt)
            
        msg = 'Analysis Complete'

        # Write the output JSON file
        dname = os.path.dirname(Raw_file)
        fname = os.path.basename(Raw_file)
        Analysis_file = os.path.join(dname, fname[0:len(fname)-5] + '_Analyzed.json')

        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                dtypes = (np.datetime64, np.complexfloating)
                if isinstance(obj, dtypes):
                    return str(obj)
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    if any([np.issubdtype(obj.dtype, i) for i in dtypes]):
                        return obj.astype(str).tolist()
                    return obj.tolist()
                return super(NpEncoder, self).default(obj)

        with open(Raw_file, "w") as outfile: 
            json.dump(Raw, outfile, cls=NpEncoder)
            
        with open(Analysis_file, "w") as outfile: 
            json.dump(Analysis, outfile, cls=NpEncoder)

        return Raw, Analysis, load_dir, err_flag, msg, Analysis_file

    else:
        msg = 'Incomplete input data. Ensure the Raw Data JSON file is correct.'
        Analysis = {}

        return Raw, Analysis, load_dir, err_flag, msg, Analysis_file
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   CheckStages.py
#
#   PURPOSE: Check an edited stage dictionary before passing to the analysis code
#
#   INPUTS:
#       Stages_new    New Stage Dictionary to check
#       Stages_old    Previous working Stage Dictionary
#       Rdict         Raw Data Dictionary
#
#   OUTPUTS: 
#       Stages_new    Working Stage Dictionary
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CheckStages(Analysis_new, Analysis_old, Raw):
    # Import Modules
    from tkinter import messagebox

    # Initialize error check to 0
    err_stage = 0

    # Check #1 - All indices are in order
    for k in range(len(Analysis_new['Stages']['End Index']['Value'])-1):
        if Analysis_new['Stages']['End Index']['Value'][k] > Analysis_new['Stages']['End Index']['Value'][k+1]:
            err_stage = 1
            messagebox.showinfo(title='Stage Table Error', message='Stage indices are not in order - ensure "End Index" for each stage is correct before proceeding')
            return Analysis_old

    # Check #2 - All indices are within bounds
    if Analysis_new['Stages']['End Index']['Value'][0] < 0:
        Analysis_new['Stages']['End Index']['Value'][0] = 0
    if Analysis_new['Stages']['End Index']['Value'][-1] > Raw['Raw Data']['Index']['Value'][-1]:
        Analysis_new['Stages']['End Index']['Value'][-1] = Raw['Raw Data']['Index']['Value'][-1]

    # Check #3 - Stage Type and Control Mode are both defined
    type_list = ['Tensile Loading','Tensile Unloading','Compressive Loading','Compressive Unloading','Shear Loading','Shear Unloading', 'Creep', 'Relaxation']
    control_list = ['Stress','Strain']
    for k in range(len(Analysis_new['Stages']['End Index']['Value'])):
        if Analysis_new['Stages']['Control Mode']['Value'][k] in control_list and Analysis_new['Stages']['Stage Type']['Value'][k] not in type_list:
            messagebox.showinfo(title='Stage Table Warning', message='Stage Type not defined - program controlled analysis will be used.')
            Analysis_new['Stages']['Control Mode']['Value'][k] = ''
            Analysis_new['Stages']['Stage Type']['Value'][k] = ''
        if Analysis_new['Stages']['Control Mode']['Value'][k] not in control_list and Analysis_new['Stages']['Stage Type']['Value'][k] in type_list:
            messagebox.showinfo(title='Stage Table Warning', message='Control Mode not defined - program controlled analysis will be used.')
            Analysis_new['Stages']['Control Mode']['Value'][k] = ''
            Analysis_new['Stages']['Stage Type']['Value'][k] = ''
    return Analysis_new
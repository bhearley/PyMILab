#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
# TMAnalysis_GUI.py
#   Brandon Hearley - LMS
#   brandon.l.hearley@nasa.gov
#
# PURPOSE: Run the TMAnalysis GUI. See documentation for all TMAnalysis features
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Import Modules
import json
import numpy as np
import os
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tksheet
import scipy.stats
import shutil

# Import Functions
from GUI.BuildPropTable import *
from GUI.BuildStageTable import *
from GUI.CheckStages import *
from GUI.DeletePages import *
from GUI.FileSelection import *
from GUI.GeneralAnalysis import *
from GUI.GetStyles import *
from GUI.Placement import *
from GUI.UserOptions import *
from TMAnalysisEngine import *

# Set Directories
home = os.getcwd()

# Define Images
title_img = os.path.join(home,'TMAnalysis','GUI','Images','TitleHeader.png') # Set the title image path
logo_img = os.path.join(home,'TMAnalysis','GUI','Images','NasaLogo.png')     # Set the logo image path

#Create the GUI
class TMAnalysis_GUI:
    #Initialize
    def __init__(self):
        global window
        #Create Background Window
        window = tk.Tk()
        window.title("TMAnalysis")
        window.state('zoomed')
        window.configure(bg='white')

        # Get Placement Information
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        Placements(self, str(screen_width) + "x" + str(screen_height))

        # Get Styles
        GetStyles(self)

        #Add the Title
        self.img_hdr = ImageTk.PhotoImage(Image.open(title_img))
        self.panel_hdr = tk.Label(window, image = self.img_hdr, bg = 'white')
        self.panel_hdr.place(
                            anchor = 'n', 
                            relx = self.Placement['HomePage']['Title'][0], 
                            rely = self.Placement['HomePage']['Title'][1]
                            )

        #Add the NASA Logo
        self.img_nasa = ImageTk.PhotoImage(Image.open(logo_img))
        self.panel_nasa = tk.Label(window, image = self.img_nasa, bg = 'white')
        self.panel_nasa.place(
                            anchor = 'e',
                            relx = self.Placement['HomePage']['Logo'][0], 
                            rely = self.Placement['HomePage']['Logo'][1]
                            )

        # Build the File Selection Page
        FileSelection(self,window)

        #Main Loop
        window.mainloop()

    # Button Functions
    # -- Select the Raw Data JSON file
    def get_raw_json(self):
        # Create File selection
        self.raw_files = filedialog.askopenfilenames(initialdir=home, title="Select the raw data JSON files", filetypes=(("Json File", "*.json"),))

        # Initialize output files
        self.outfiles = []  # Initialize lust of output files
        self.fcount = 0     #Initialize file counter

        # Delete Previous Page
        DeletePages(self,'FileSelection')

        # Build the User Options Page
        UserOptions(self,window)

    # -- Begin Analysis
    def begin_analysis(self):
        # Get User Options
        if self.fcount == 0:
            # -- Plotting
            user_options = {}
            user_options['plot'] = self.UO_chkval1.get()

            # -- Yield
            if hasattr(self,"yield_table") == True:
                yield_vals = []
                table_data = self.yield_table.data
                for k in range(len(table_data)):
                    try:
                       float(table_data[k][0])
                       yield_vals.append(float(table_data[k][0]))
                    except:
                        temp=1 # do nothing with that value
                if len(yield_vals) >0 :
                    user_options['Yield Offset'] = yield_vals

            # -- Additional Information (all tests)
            self.add_info = table_data = self.test_info_extra.data
   
            # Delete Previous Page
            DeletePages(self,'UserOptions')

        # -- Additional Information (current test)
        user_options['Additional Information'] = [self.add_info[self.fcount][1],self.add_info[self.fcount][2],self.add_info[self.fcount][3]]

        # -- Set User Edit Flags
        user_options['UserEdit'] = {}
        user_options['UserEdit']['Modulus'] = 0
        user_options['UserEdit']['Prop'] = 0
        user_options['UserEdit']['Creep'] = 0
        
        # Store user options to self
        self.user_opt = user_options

        # Import TMAnalysis
        
        
        # Load the Input File
        self.f= open(self.raw_files[self.fcount])  #Get the first file
        self.Raw = json.load(self.f) 

        # Perform the analysis
        self.Raw, self.Analysis, self.dir, err_flag, msg, self.Analysis_file = TMAnalysis(self.raw_files[self.fcount], 0, self.user_opt)

        if err_flag == 0:
            GeneralAnalysis(self, window)

        else:
            # Raw Data incorrect - display error message and continue
            messagebox.showinfo(title='Error', message='Error in test ' + self.raw_files[self.fcount] + ':' + msg)
            self.continue_analysis()

    # -- Create the Stage Table and Stage Plot
    def create_stage_table(self):
        Build_Stage_Table(self, window)

    # -- Create The Properties Table and Properties Plot
    def create_prop_table(self):
        Build_Prop_Table(self, window)

    # -- Reanalyze the raw data from user defined stages
    def reanalyze_stages(self):
        # Unpack Rdict and Stages
        Raw = self.Raw
        Analysis = self.Analysis
        Analysis_old = Analysis.copy()
        dir = self.dir

        # Perform check on indices
        table_data = self.stage_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)
        index_flag = 0
        for i in range(len(table_data)-1):
            if table_data[i][6] == '' or table_data[i+1][6] == '':
                index_flag = 1
                break
            elif int(table_data[i][6]) > int(table_data[i+1][6]):
                index_flag = 1
                break

        # Perform check on stage type
        type_list = ['Tensile Loading','Tensile Unloading','Compressive Loading','Compressive Unloading', 'Shear Loading','Shear Unloading', 'Creep', 'Relaxation']
        for i in range(len(table_data)):
            if table_data[i][1] not in type_list:
                index_flag = 2
                break

        # Perform check on control mode
        control_list = ['Stress','Strain']
        for i in range(len(table_data)):
            if table_data[i][2] not in control_list:
                index_flag = 3
                break

        # Display Error Message to User or Continue
        if index_flag == 1:
            messagebox.showinfo(title='Stage Table Error', message='Stage indices are not in order - ensure "End Index" for each stage is correct before proceeding')
        elif index_flag == 2:
            messagebox.showinfo(title='Stage Table Error', message='Stage Type must be defined for all stages')
        elif index_flag == 3:
            messagebox.showinfo(title='Stage Table Error', message='Control Mode must be defined for all stages')
        else:
            # Redefine Stages Dictionary
            stage_keys = list(Analysis_old['Stages'].keys())
            Analysis_new = Analysis_old.copy()

            # Option 1 - Same number of Stages
            if len(table_data) == len(Analysis_new['Stages']['Stage Name']['Value']):
                for k in range(len(table_data)):
                    Analysis_new['Stages']['Stage Name']['Value'][k]=table_data[k][0]
                    Analysis_new['Stages']['Stage Type']['Value'][k]=table_data[k][1]
                    Analysis_new['Stages']['Control Mode']['Value'][k]=table_data[k][2]
                    if table_data[k][3] == '':
                        Analysis_new['Stages']['Target Strain-' + dir]['Value'][k] = 0
                    else:
                        Analysis_new['Stages']['Target Strain-' + dir]['Value'][k]=float(table_data[k][3])
                    if table_data[k][4] == '':
                        Analysis_new['Stages']['Target Stress-' + dir]['Value'][k] = 0
                    else:
                        Analysis_new['Stages']['Target Stress-' + dir]['Value'][k]=float(table_data[k][4])
                    if table_data[k][4] == '':
                        Analysis_new['Stages']['Target Time']['Value'][k] = 0
                    else:
                        Analysis_new['Stages']['Target Time']['Value'][k]=float(table_data[k][5])
                    Analysis_new['Stages']['End Index']['Value'][k]=int(table_data[k][6])

            # Option 2 - Deleted a Stage or Added Stage
            else: 
                # Initialize Stages
                for j in range(len(stage_keys)):
                    if len(Analysis_new['Stages'][stage_keys[j]]['Value']) > 0:
                        Analysis_new['Stages'][stage_keys[j]]['Value'] = []
                        for k in range(len(table_data)):
                            Analysis_new['Stages'][stage_keys[j]]['Value'].append(None)

                # Repopulate Stages
                for k in range(len(table_data)):
                    Analysis_new['Stages']['Stage Name']['Value'][k]=table_data[k][0]
                    Analysis_new['Stages']['Stage Type']['Value'][k]=table_data[k][1]
                    Analysis_new['Stages']['Control Mode']['Value'][k]=table_data[k][2]
                    if table_data[k][3] == '':
                        Analysis_new['Stages']['Target Strain-'+dir]['Value'][k] = 0
                    else:
                        Analysis_new['Stages']['Target Strain-'+dir]['Value'][k]=float(table_data[k][3])
                    if table_data[k][4] == '':
                        Analysis_new['Stages']['Target Stress-'+dir]['Value'][k] = 0
                    else:
                        Analysis_new['Stages']['Target Stress-'+dir]['Value'][k]=float(table_data[k][4])
                    if table_data[k][4] == '':
                        Analysis_new['Stages']['Target Time']['Value'][k] = 0
                    else:
                        Analysis_new['Stages']['Target Time']['Value'][k]=float(table_data[k][5])
                    Analysis_new['Stages']['End Index']['Value'][k]=int(table_data[k][6])

            # Check Stages
            Analysis_new = CheckStages(Analysis_new, Analysis_old, Raw)
            self.Analysis = Analysis_new

            # Resave Analysis File to JSON
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

            with open(self.Analysis_file, "w") as outfile: 
                json.dump(self.Analysis, outfile, cls=NpEncoder)

            # Call Analysis Code
            from TMAnalysis import TMAnalysisEngine
            self.Raw, self.Analysis, self.dir, err_flag, msg, self.Analysis_file = TMAnalysisEngine(self.raw_files[self.fcount], self.Analysis_file, self.user_opt)

            # Check the error flag
            if err_flag == 1:
                messagebox.showinfo(title='Analysis Error', message=msg)
                self.Analysis = Analysis_old
           
            # Rebuild Stage Table Page
            Build_Stage_Table(self, window)

    # -- Insert Stage Above In Stage Table
    def insert_stage_above(self):
        # Unpack for conveniance
        Analysis = self.Analysis
        Raw = self.Raw
        dir = self.dir

        # Get the selected row
        self.selected_row = list(self.stage_table.get_selected_rows())[0]

        # Get the table data
        table_data = self.stage_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)
        self.stage_table.destroy()

        # Recreate the Stage Table
        hdrs =  ['Stage Name', 'Stage Type', 'Control Mode', 'Target Strain-'+dir, 'Target Stress-'+dir, 'Target Time', 'End Index']
        self.stage_table = tksheet.Sheet(
                                        window, 
                                        total_rows = len(Analysis['Stages']['End Index']['Value'])+1, 
                                        total_columns = 7, 
                                        headers = ['Stage Name', 'Stage Type', 'Control Mode', 'Target Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']', 
                                               'Target Stress [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']', 'End Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']', 
                                               'End Index'],
                                        width = self.Placement['StageTable']['Sheet1'][2], 
                                        height = self.Placement['StageTable']['Sheet1'][3], 
                                        show_x_scrollbar = False, 
                                        show_y_scrollbar = True
                                        )
        self.stage_table.place(
                            anchor = 'n', 
                            relx = self.Placement['StageTable']['Sheet1'][0], 
                            rely = self.Placement['StageTable']['Sheet1'][1]
                            )

        # Set Stage Table Drop Down Lists
        for k in range(len(Analysis['Stages']['End Index']['Value'])+1):
            self.stage_table.create_dropdown(r=k, c = 2,values=['',
                                                                'Stress', 
                                                                'Strain'])
            self.stage_table.create_dropdown(r=k, c = 1,values=['',
                                                                'Tensile Loading', 
                                                                'Tensile Unloading',
                                                                'Compressive Unloading',
                                                                'Compressive Unloading',
                                                                'Shear Loading',
                                                                'Shear Unloading',
                                                                'Creep',
                                                                'Relaxation'])

        # Repopulate Stage Table
        flg = 0
        for i in range(len(table_data)+1):
            for j in range(7):
                if i < self.selected_row:
                    self.stage_table.set_cell_data(i,j,table_data[i][j])
                elif i > self.selected_row:
                    self.stage_table.set_cell_data(i,j,table_data[i-1][j])

        # -- Format
        self.stage_table.column_width(column = 0, width = 80, redraw = True)
        self.stage_table.column_width(column = 1, width = 140, redraw = True)
        self.stage_table.column_width(column = 2, width = 90, redraw = True)
        self.stage_table.column_width(column = 3, width = 120, redraw = True)
        self.stage_table.column_width(column = 4, width = 120, redraw = True)
        self.stage_table.column_width(column = 5, width = 100, redraw = True)
        self.stage_table.column_width(column = 6, width = 80, redraw = True)

        # -- Enable Bindings
        self.stage_table.enable_bindings(bindings = 'all')

        # -- Add Custom button for adding and removing stages
        self.stage_table.disable_bindings(bindings = "rc_insert_row")
        self.stage_table.popup_menu_add_command('Insert Stage Above', self.insert_stage_above, table_menu = True, index_menu = True, header_menu = True)
        self.stage_table.popup_menu_add_command('Insert Stage Below', self.insert_stage_below, table_menu = True, index_menu = True, header_menu = True)

        # -- Enable Editing Rows
        self.selected_row = -1
        self.stage_table.popup_menu_add_command('Edit Stage Start Point with Plot', self.edit_stage_start, table_menu = True, index_menu = True, header_menu = True)
        self.stage_table.popup_menu_add_command('Edit Stage End Point with Plot', self.edit_stage_end, table_menu = True, index_menu = True, header_menu = True)

    # -- Insert Stage Below In Stage Table
    def insert_stage_below(self):
        # Unpack  for conveniance
        Analysis = self.Analysis
        Raw = self.Raw
        dir = self.dir

        # Get the selected row
        self.selected_row = list(self.stage_table.get_selected_rows())[0]

        # Get the table data
        table_data = self.stage_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)
        self.stage_table.destroy()

        # Recreate the Stage Table
        hdrs =  ['Stage Name', 'Stage Type', 'Control Mode', 'Target Strain-'+dir, 'Target Stress-'+dir, 'Target Time', 'End Index']
        self.stage_table = tksheet.Sheet(window, total_rows = len(Analysis['Stages']['End Index']['Value'])+1, total_columns = 7, 
                                    headers = ['Stage Name', 'Stage Type', 'Control Mode', 'Target Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']', 
                                               'Target Stress [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']', 'End Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']', 
                                               'End Index'],
                                    width = 790, height = 550, show_x_scrollbar = False, show_y_scrollbar = True)
        self.stage_table.place(anchor = 'n', relx = 0.26, rely = 0.30)

        # Set Stage Table Drop Down Lists
        for k in range(len(Analysis['Stages']['End Index']['Value'])+1):
            self.stage_table.create_dropdown(r=k, c = 2,values=['',
                                                                'Stress', 
                                                                'Strain'])
            self.stage_table.create_dropdown(r=k, c = 1,values=['',
                                                                'Tensile Loading', 
                                                                'Tensile Unloading',
                                                                'Compressive Unloading',
                                                                'Compressive Unloading',
                                                                'Shear Loading',
                                                                'Shear Unloading',
                                                                'Creep',
                                                                'Relaxation'])

        # Repopulate Stage Table
        flg = 0
        for i in range(len(table_data)+1):
            for j in range(7):
                if i < self.selected_row+1:
                    self.stage_table.set_cell_data(i,j,table_data[i][j])
                elif i > self.selected_row+1:
                    self.stage_table.set_cell_data(i,j,table_data[i-1][j])

        # -- Format
        self.stage_table.column_width(column = 0, width = 80, redraw = True)
        self.stage_table.column_width(column = 1, width = 140, redraw = True)
        self.stage_table.column_width(column = 2, width = 90, redraw = True)
        self.stage_table.column_width(column = 3, width = 120, redraw = True)
        self.stage_table.column_width(column = 4, width = 120, redraw = True)
        self.stage_table.column_width(column = 5, width = 100, redraw = True)
        self.stage_table.column_width(column = 6, width = 80, redraw = True)

        # -- Enable Bindings
        self.stage_table.enable_bindings('all')

        # -- Add Custom button for adding and removing stages
        self.stage_table.disable_bindings("rc_insert_row")
        self.stage_table.popup_menu_add_command('Insert Stage Above', self.insert_stage_above, table_menu = True, index_menu = True, header_menu = True)
        self.stage_table.popup_menu_add_command('Insert Stage Below', self.insert_stage_below, table_menu = True, index_menu = True, header_menu = True)

        # -- Enable Editing Rows
        self.selected_row = -1
        self.stage_table.popup_menu_add_command('Edit Stage Start Point with Plot', self.edit_stage_start, table_menu = True, index_menu = True, header_menu = True)
        self.stage_table.popup_menu_add_command('Edit Stage End Point with Plot', self.edit_stage_end, table_menu = True, index_menu = True, header_menu = True)


    # -- Stage Table Popupmenu Button - Edit the start point of a stage
    def edit_stage_start(self):
        self.selected_row = list(self.stage_table.get_selected_rows())[0] # Get the selected row
        self.clicked_pt = 1                                               # Set to 1 (indicates editing start points)
        self.clicked_idx = -1                                             # Initialize index to -1
        # Add binding for the button press
        self.plot1.figure.canvas.mpl_connect('button_press_event', self.on_button_press)

    # -- Stage Table Popupmenu Button - Edit the end point of a stage
    def edit_stage_end(self):
        self.selected_row = list(self.stage_table.get_selected_rows())[0] # Get the selected row
        self.clicked_pt = 2                                               # Set to 2 (indicates editing end points)
        self.clicked_idx = -1                                             # Initialize index to -1
        # Add binding for the button press
        self.plot1.figure.canvas.mpl_connect('button_press_event', self.on_button_press)

    # -- Update the Stage Table if a Start Point was Changed
    def update_table_start(self, event):
        # Get the Stage Table Data
        table_data = self.stage_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)

        # Unpack
        Raw = self.Raw
        Analysis_old = self.Analysis
        Analysis_new = Analysis_old.copy()
        stage_keys = list(Analysis_old['Stages'].keys())
        dir = self.dir

        # Option 1 - New Stage Was Added
        if len(Analysis_old['Stages']['Stage Name']['Value']) < len(table_data):
            # Check if last stage
            if self.selected_row == len(table_data)-1:
                if table_data[self.selected_row][6] == '':
                    table_data[self.selected_row][6] = table_data[self.selected_row-1][6]
                    table_data[self.selected_row-1][6] = None

            # Initialize Stages
            for j in range(len(stage_keys)):
                if "Value" in list(Analysis_new['Stages'][stage_keys[j]].keys()):
                    if len(Analysis_new['Stages'][stage_keys[j]]['Value']) > 0:
                        Analysis_new['Stages'][stage_keys[j]]['Value'] = []
                        for k in range(len(table_data)):
                            Analysis_new['Stages'][stage_keys[j]]['Value'].append(None)

            # Repopulate Stage Table
            for k in range(len(table_data)):
                Analysis_new['Stages']['Stage Name']['Value'][k]=table_data[k][0]
                Analysis_new['Stages']['Stage Type']['Value'][k]=table_data[k][1]
                Analysis_new['Stages']['Control Mode']['Value'][k]=table_data[k][2]
                if table_data[k][3] == '':
                    Analysis_new['Stages']['Target Strain-' + dir]['Value'][k] = 0
                else:
                    Analysis_new['Stages']['Target Strain-' + dir]['Value'][k]=float(table_data[k][3])
                if table_data[k][4] == '':
                    Analysis_new['Stages']['Target Stress-' + dir]['Value'][k] = 0
                else:
                    Analysis_new['Stages']['Target Stress-' + dir]['Value'][k]=float(table_data[k][4])
                if table_data[k][4] == '':
                    Analysis_new['Stages']['Target Time']['Value'][k] = 0
                else:
                    Analysis_new['Stages']['Target Time']['Value'][k]=float(table_data[k][5])

                # For Selected Row use the defined point
                if k != self.selected_row-1:
                    Analysis_new['Stages']['End Index']['Value'][k]=int(table_data[k][6])
                else:
                    Analysis_new['Stages']['End Index']['Value'][k]=self.clicked_idx

        # Option 2 - Existing Stage was changed
        elif len(Analysis_old['Stages']['Stage Name']['Value']) == len(table_data):
            Analysis_new['Stages']['End Index']['Value'][self.selected_row-1] = self.clicked_idx 

        # Check Stages
        Analysis_new = CheckStages(Analysis_new, Analysis_old, Raw)
        self.Analysis = Analysis_new

        # Resave Analysis File to JSON
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
            
        with open(self.Analysis_file, "w") as outfile: 
            json.dump(self.Analysis, outfile, cls=NpEncoder)

        # Call Analysis Code
        self.Raw, self.Analysis, self.dir, err_flag, msg, self.Analysis_file = TMAnalysis(self.raw_files[self.fcount], self.Analysis_file, self.user_opt)

        # Check the error flag
        if err_flag == 1:
            messagebox.showinfo(title='Analysis Error', message=msg)
            self.Analysis = Analysis_old

        # Rebuild Stage Table Page
        Build_Stage_Table(self, window)

    # -- Update the Stage Table if a Start Point was Changed
    def update_table_end(self, event):
        # Get the Stage Table Data
        table_data = self.stage_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)

        # Unpack
        Raw = self.Raw
        Analysis_old = self.Analysis
        Analysis_new = Analysis_old.copy()
        stage_keys = list(Analysis_old['Stages'].keys())
        dir = self.dir

        # Option 1 - New Stage Was Added
        if len(Analysis_old['Stages']['Stage Name']['Value']) < len(table_data):
            # Initialize Stages
            for j in range(len(stage_keys)):
                if len(Analysis_new['Stages'][stage_keys[j]]['Value']) > 0:
                    Analysis_new['Stages'][stage_keys[j]]['Value'] = []
                    for k in range(len(table_data)):
                        Analysis_new['Stages'][stage_keys[j]]['Value'].append(None)

            # Repopulate Stage Table
            for k in range(len(table_data)):
                Analysis_new['Stages']['Stage Name']['Value'][k]=table_data[k][0]
                Analysis_new['Stages']['Stage Type']['Value'][k]=table_data[k][1]
                Analysis_new['Stages']['Control Mode']['Value'][k]=table_data[k][2]
                if table_data[k][3] == '':
                    Analysis_new['Stages']['Target Strain-' + dir]['Value'][k] = 0
                else:
                    Analysis_new['Stages']['Target Strain-' + dir]['Value'][k]=float(table_data[k][3])
                if table_data[k][4] == '':
                    Analysis_new['Stages']['Target Stress-' + dir]['Value'][k] = 0
                else:
                    Analysis_new['Stages']['Target Stress-' + dir]['Value'][k]=float(table_data[k][4])
                if table_data[k][4] == '':
                    Analysis_new['Stages']['Target Time']['Value'][k] = 0
                else:
                    Analysis_new['Stages']['Target Time']['Value'][k]=float(table_data[k][5])
                # For Selected Row use the defined point
                if k != self.selected_row:
                    Analysis_new['Stages']['End Index']['Value'][k]=int(table_data[k][6])
                else:
                    Analysis_new['Stages']['End Index']['Value'][k]=self.clicked_idx

        # Option 2 - Existing Stage was changed
        elif len(Analysis_old['Stages']['Stage Name']['Value']) == len(table_data):
            Analysis_new['Stages']['End Index']['Value'][self.selected_row] = self.clicked_idx 

        # Check Stages
        Analysis_new = CheckStages(Analysis_new, Analysis_old, Raw)
        self.Analysis = Analysis_new

        # Resave Analysis File to JSON
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
            
        with open(self.Analysis_file, "w") as outfile: 
            json.dump(self.Analysis, outfile, cls=NpEncoder)

        # Call Analysis Code
        from TMAnalysis import TMAnalysisEngine
        self.Raw, self.Analysis, self.dir, err_flag, msg, self.Analysis_file = TMAnalysisEngine(self.raw_files[self.fcount], self.Analysis_file, self.user_opt)

        # Check the error flag
        if err_flag == 1:
            messagebox.showinfo(title='Analysis Error', message=msg)
            self.Analysis = Analysis_old

        # Rebuild Stage Table Page
        Build_Stage_Table(self, window)

    # -- Move Point Right on Stage Table
    def move_right(self,event):
        # Remove the Previous Point
        self.plot1.lines.pop(len(self.plot1.lines)-1)
        self.canvas.draw()

        # Get the labels
        xlabel = self.x_plot_opt.get()
        ylabel = self.y_plot_opt.get()

        # Update the index
        mind_i = self.clicked_idx + 1
        if mind_i == len(self.Raw['Raw Data'][xlabel]['Value']):
            mind_i = mind_i-1

        # Define the Point
        xc = self.Raw['Raw Data'][xlabel]['Value'][mind_i]
        yc = self.Raw['Raw Data'][ylabel]['Value'][mind_i]
        self.clicked_idx = mind_i

        # Plot
        self.plot1.plot(xc,yc,'ko')
        self.canvas.draw()

    # -- Move Point Left on Stage Table
    def move_left(self,event):
        # Remove the Previous Point
        self.plot1.lines.pop(len(self.plot1.lines)-1)
        self.canvas.draw()

        # Get the labels
        xlabel = self.x_plot_opt.get()
        ylabel = self.y_plot_opt.get()

        # Update the index
        mind_i = self.clicked_idx - 1
        if mind_i == 0:
            mind_i = mind_i+1

        # Define the Point
        xc = self.Raw['Raw Data'][xlabel]['Value'][mind_i]
        yc = self.Raw['Raw Data'][ylabel]['Value'][mind_i]
        self.clicked_idx = mind_i

        # Plot
        self.plot1.plot(xc,yc,'ko')
        self.canvas.draw()
        
    # -- Get user defined stage point from left click
    def on_button_press(self, event):
        # Check that a row was selected
        if self.selected_row >= 0:
            # Check that Edit Stage with Plot Button was Pressed
            if self.clicked_pt > 0:
                # Get the selected point
                self.x = event.xdata
                self.y= event.ydata

                # Get the x and y
                xlabel = self.x_plot_opt.get()
                ylabel = self.y_plot_opt.get()

                # Find the closest point to the point selected
                mind = 1e5
                mind_i = -1
                for i in range(len(self.Raw['Raw Data'][xlabel]['Value'])):
                    dist = ((self.x - self.Raw['Raw Data'][xlabel]['Value'][i])**2+(self.y-self.Raw['Raw Data'][ylabel]['Value'][i])**2)**0.5
                    if dist < mind:
                        mind = dist
                        mind_i = i
            
                # Define the Point
                xc = self.Raw['Raw Data'][xlabel]['Value'][mind_i]
                yc = self.Raw['Raw Data'][ylabel]['Value'][mind_i]
                self.clicked_idx = mind_i

                # Plot
                self.plot1.plot(xc,yc,'ko')
                self.canvas.draw()

                # Bind the Right and Left Arrow Keys
                self.canvas.get_tk_widget().bind("<Right>", self.move_right)
                self.canvas.get_tk_widget().bind("<Left>", self.move_left)

                # For editing start point, ensure the first row isn't selected and bind 'Return'
                if self.clicked_pt == 1 and self.selected_row >= 1:
                    self.canvas.get_tk_widget().bind("<Return>", self.update_table_start)

                # For editing end point, ensure the last row isn't selected and bind 'Return'
                elif self.clicked_pt == 2 and self.selected_row < len(self.stage_table.get_sheet_data(return_copy = False, get_header = False, get_index = False))-1: 
                    self.canvas.get_tk_widget().bind("<Return>", self.update_table_end)

                self.canvas.get_tk_widget().focus_set() # Set Bindings
                self.clicked_pt = 0                     # Turn off binding for left click

    # -- Property Table Popupmenu Button - Editing Proportional Limit
    def edit_prop_lim(self):
        if self.prop_plot_opt.get() == "Stress vs Strain":
            self.clicked_prop = 0   # Initialize to 0
            # Add binding for the button press
            self.plot1.figure.canvas.mpl_connect('button_press_event', self.on_button_press_prop)


    # -- Get user defined proportional limit from click
    def on_button_press_prop(self, event):
         # Check that Edit Stage with Plot Button was Pressed
            if self.clicked_prop == 0:
                self.clicked_prop = 1

                # Get the selected point
                self.x = event.xdata
                self.y= event.ydata

                # Get the x and y
                xdata = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]
                ydata = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]

                # Find the closest point to the point selected
                mind = 1e5
                mind_i = -1
                for i in range(len(xdata)):
                    dist = ((self.x - xdata[i])**2+(self.y-ydata[i])**2)**0.5
                    if dist < mind:
                        mind = dist
                        mind_i = i
            
                # Define the Point
                xc = xdata[mind_i]
                yc = ydata[mind_i]
                self.clicked_idx = mind_i

                # Plot
                self.plot1.plot(xc,yc,'ko')
                self.canvas.draw()

                # Bind the Right and Left Arrow Keys
                self.canvas.get_tk_widget().bind("<Right>", self.move_right_prop)
                self.canvas.get_tk_widget().bind("<Left>", self.move_left_prop)
                self.canvas.get_tk_widget().bind("<Return>", self.update_prop)
                self.canvas.get_tk_widget().focus_set() # Set Bindings

    # -- Move proportional limit right
    def move_right_prop(self,event):
        # Remove the Previous Point
        self.plot1.lines.pop(len(self.plot1.lines)-1)
        self.canvas.draw()

        # Update the index
        mind_i = self.clicked_idx + 1
        if mind_i == len(self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]):
            mind_i = mind_i-1

        # Define the Point
        xc = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][mind_i]
        yc = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][mind_i]
        self.clicked_idx = mind_i

        # Plot
        self.plot1.plot(xc,yc,'ko')
        self.canvas.draw()

    # -- Move proportional limit left
    def move_left_prop(self,event):
        # Remove the Previous Point
        self.plot1.lines.pop(len(self.plot1.lines)-1)
        self.canvas.draw()

        # Update the index
        mind_i = self.clicked_idx - 1
        if mind_i == 0:
            mind_i = mind_i+1

        # Define the Point
        xc = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][mind_i]
        yc = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][mind_i]
        self.clicked_idx = mind_i

        # Plot
        self.plot1.plot(xc,yc,'ko')
        self.canvas.draw()

    # -- Update the user defined proportional limit
    def update_prop(self, event):
        # Turn on user edit flag
        self.user_opt['UserEdit']['Prop'] = 1
        self.clicked_prop = 0

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            # Set the Proportional Limit and Proportional Limit Strain
            self.Analysis['Tensile Analysis']['Proportional Limit Strain-' + self.dir]['Value'] = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][self.clicked_idx]
            self.Analysis['Tensile Analysis']['Proportional Limit-' + self.dir]['Value'] = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][self.clicked_idx]

            # Update the properties table
            self.prop_table.set_cell_data(3,1,str(round(self.Analysis['Tensile Analysis']['Proportional Limit Strain-' + self.dir]['Value'],2)))
            self.prop_table.set_cell_data(2,1,str(round(self.Analysis['Tensile Analysis']['Proportional Limit-' + self.dir]['Value'],2)))
            self.prop_table.redraw()

            # Replot the Tensile Analysis
            from GUI.TensilePropertyPlot import TensilePropertyPlot
            TensilePropertyPlot(self, window)

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            # Set the Proportional Limit and Proportional Limit Strain
            self.Analysis['Compressive Analysis']['Compressive Proportional Limit Strain-' + self.dir]['Value'] = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][self.clicked_idx]
            self.Analysis['Compressive Analysis']['Compressive Proportional Limit-' + self.dir]['Value'] = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][self.clicked_idx]

            # Update the properties table
            self.prop_table.set_cell_data(3,1,str(round(self.Analysis['Compressive Analysis']['Compressive Proportional Limit Strain-' + self.dir]['Value'],2)))
            self.prop_table.set_cell_data(2,1,str(round(self.Analysis['Compressive Analysis']['Compressive Proportional Limit-' + self.dir]['Value'],2)))
            self.prop_table.redraw()

            # Replot the Tensile Analysis
            from GUI.CompressivePropertyPlot import CompressivePropertyPlot
            CompressivePropertyPlot(self, window)

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            # Set the Proportional Limit and Proportional Limit Strain
            self.Analysis['Shear Analysis']['Shear Proportional Limit Strain-' + self.dir]['Value'] = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][self.clicked_idx]
            self.Analysis['Shear Analysis']['Shear Proportional Limit-' + self.dir]['Value'] = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]][self.clicked_idx]

            # Update the properties table
            self.prop_table.set_cell_data(3,1,str(round(self.Analysis['Shear Analysis']['Shear Proportional Limit Strain-' + self.dir]['Value'],2)))
            self.prop_table.set_cell_data(2,1,str(round(self.Analysis['Shear Analysis']['Shear Proportional Limit-' + self.dir]['Value'],2)))
            self.prop_table.redraw()

            # Replot the Tensile Analysis
            from GUI.ShearPropertyPlot import ShearPropertyPlot
            ShearPropertyPlot(self, window)

        # Reanalyze the stages
        self.reanalyze_stages()

        # Reload the Page
        self.create_prop_table()

        from GUI.PropDisplay import PropDisplay
        PropDisplay(self, window)

    # -- Property Table Popupmenu Button - Editing Modulus Limit
    def edit_modulus(self):
        if self.prop_plot_opt.get() == "Stress vs Strain":
            # Get the current modulus
            table_data = self.prop_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)
            self.curr_mod = float(table_data[0][1])
            self.curr_mod_del = 0.01*float(table_data[0][1])

            # Bind the Right and Left Arrow Keys
            self.canvas.get_tk_widget().bind("<Right>", self.move_right_mod)
            self.canvas.get_tk_widget().bind("<Left>", self.move_left_mod)
            self.canvas.get_tk_widget().bind("<Return>", self.update_mod)
            self.canvas.get_tk_widget().focus_set() # Set Bindings

    # -- Rotate Modulus clockwise (right arrow key)
    def move_right_mod(self,event):
        # Get the line ID
        for i in range(len(self.plot1.lines)):
            clr = str(self.plot1.lines[i].get_color())
            style = str(self.plot1.lines[i].get_linestyle())

            if clr == 'r' and style == '--':
                mod_line_id = i

        # Remove the Previous Point
        self.plot1.lines.pop(mod_line_id)
        self.canvas.draw()

        # -- Unpack stress and strain for convenience
        strain = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]
        stress = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]
       
        # -- Update modulus
        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            mod = self.Analysis['Tensile Analysis']['Modulus-' + self.dir]['Value']
            if mod > 0:
                mod = mod - self.curr_mod_del
            else:
                mod = mod + self.curr_mod_del
            self.Analysis['Tensile Analysis']['Modulus-' + self.dir]['Value'] = mod

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            mod = self.Analysis['Compressive Analysis']['Compressive Modulus-' + self.dir]['Value']
            if mod > 0:
                mod = mod - self.curr_mod_del
            else:
                mod = mod + self.curr_mod_del
            self.Analysis['Compressive Analysis']['Compressive Modulus-' + self.dir]['Value'] = mod

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            mod = self.Analysis['Shear Analysis']['Shear Modulus-' + self.dir]['Value']
            if mod > 0:
                mod = mod - self.curr_mod_del
            else:
                mod = mod + self.curr_mod_del
            self.Analysis['Shear Analysis']['Shear Modulus-' + self.dir]['Value'] = mod

        # -- Plot the modulus
        strain_lin_end = min([(stress[-1]-stress[0])/mod+strain[0], strain[-1]])
        strain_lin = np.linspace(strain[0],strain_lin_end,100)
        stress_lin = stress[0]+mod*(strain_lin-strain[0])
        self.plot1.plot(strain_lin,stress_lin,'r--',label='Modulus')

        # -- Redrdaw Canvas
        self.canvas.draw()

    # -- Rotate Modulus counter clockwise (left arrow key)
    def move_left_mod(self,event):
        # Get the line ID
        for i in range(len(self.plot1.lines)):
            clr = str(self.plot1.lines[i].get_color())
            style = str(self.plot1.lines[i].get_linestyle())

            if clr == 'r' and style == '--':
                mod_line_id = i

        # Remove the Previous Point
        self.plot1.lines.pop(mod_line_id)
        self.canvas.draw()

        # -- Unpack stress and strain for convenience
        strain = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]
        stress = self.Raw['Raw Data']['Stress-'+self.dir]['Value'][0:self.Analysis['Stages']['End Index']['Value'][0]]
       
        # -- Update the modulus
        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            mod = self.Analysis['Tensile Analysis']['Modulus-' + self.dir]['Value']
            if mod < 0:
                mod = mod - self.curr_mod_del
            else:
                mod = mod + self.curr_mod_del
            self.Analysis['Tensile Analysis']['Modulus-' + self.dir]['Value'] = mod

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            mod = self.Analysis['Compressive Analysis']['Compressive Modulus-' + self.dir]['Value']
            if mod < 0:
                mod = mod - self.curr_mod_del
            else:
                mod = mod + self.curr_mod_del
            self.Analysis['Compressive Analysis']['Compressive Modulus-' + self.dir]['Value'] = mod

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            mod = self.Analysis['Shear Analysis']['Shear Modulus-' + self.dir]['Value']
            if mod < 0:
                mod = mod - self.curr_mod_del
            else:
                mod = mod + self.curr_mod_del
            self.Analysis['Shear Analysis']['Shear Modulus-' + self.dir]['Value'] = mod

        # -- Plot the modulus
        strain_lin_end = min([(stress[-1]-stress[0])/mod+strain[0], strain[-1]])
        strain_lin = np.linspace(strain[0],strain_lin_end,100)
        stress_lin = stress[0]+mod*(strain_lin-strain[0])
        self.plot1.plot(strain_lin,stress_lin,'r--',label='Modulus')

        # -- Redraw the canvas
        self.canvas.draw()

    # -- Update the user defined modulus
    def update_mod(self, event):
        # Turn on user edit flag
        self.user_opt['UserEdit']['Modulus'] = 1

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            # Update the properties table
            self.prop_table.set_cell_data(0,1,f'{self.Analysis["Tensile Analysis"]["Modulus-" + self.dir]["Value"]:.3e}')
            self.prop_table.redraw()

            # Replot the Tensile Analysis
            from GUI.TensilePropertyPlot import TensilePropertyPlot
            TensilePropertyPlot(self, window)

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            # Update the properties table
            self.prop_table.set_cell_data(0,1,f'{self.Analysis["Compressive Analysis"]["Compressive Modulus-" + self.dir]["Value"]:.3e}')
            self.prop_table.redraw()

            # Replot the Compressive Analysis
            from GUI.CompressivePropertyPlot import CompressivePropertyPlot
            CompressivePropertyPlot(self, window)

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            # Update the properties table
            self.prop_table.set_cell_data(0,1,f'{self.Analysis["Shear Analysis"]["Shear Modulus-" + self.dir]["Value"]:.3e}')
            self.prop_table.redraw()

            # Replot the Shear Analysis
            from GUI.ShearPropertyPlot import ShearPropertyPlot
            ShearPropertyPlot(self, window)

        # Reanalyze the stages
        self.reanalyze_stages()

        # Reload the Page
        self.create_prop_table()

        from GUI.PropDisplay import PropDisplay
        PropDisplay(self, window)


    # -- Property Table Popupmenu Button - Editing Creeo Zones
    def edit_creep(self):
        if self.prop_plot_opt.get() == "Creep Strain vs Time":
            if self.creep_edit_opt.get() != "Select Zone to Edit Endpoint":
                self.clicked_creep = 0 # Initialize to 0
                # Add binding for the button press
                self.plot1.figure.canvas.mpl_connect('button_press_event', self.on_button_press_creep)

    # -- Get user defined creep end point from left click
    def on_button_press_creep(self, event):
         # Check that Edit Stage with Plot Button was Pressed
        if self.clicked_creep == 0:
            self.clicked_creep = 1

            # Get the selected point
            self.x = event.xdata
            self.y= event.ydata

            # -- Get the selected value
            zone = self.creep_edit_opt.get()
            if zone == 'Primary':
                self.color = 'r'
            else:
                self.color = 'b'

            # Get Max Index
            # -- Determine if its tensile, compressive, or shear creep
            if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
                primary = self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]
                secondary = self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]
                tertiary = self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]

            if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
                primary = self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]
                secondary = self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]
                tertiary = self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]

            if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
                primary = self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]
                secondary = self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]
                tertiary = self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]

            if primary['Index']['Value'] != []:
                self.max_idx_crp = max(primary['Index']['Value']) - 1
            if secondary['Index']['Value'] != []:
                self.max_idx_crp = max(secondary['Index']['Value'])  -1
            if tertiary['Index']['Value'] != []:
                self.max_idx_crp = max(tertiary['Index']['Value']) - 1

            # Get the x and y
            xdata = self.Raw['Raw Data']['Time']['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]]
            ydata = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]]

            # Find the closest point to the point selected
            mind = 1e5
            mind_i = -1
            for i in range(len(xdata)):
                dist = ((self.x - xdata[i])**2+(self.y-ydata[i])**2)**0.5
                if dist < mind:
                    mind = dist
                    mind_i = i
            
            # Define the Point
            if mind_i > self.max_idx_crp:
                mind_i = self.max_idx_crp

            xc = xdata[mind_i]
            yc = ydata[mind_i]
            self.clicked_idx = mind_i

            # Plot
            self.plot1.plot(xc,yc,self.color + 'o')
            self.canvas.draw()

            # Bind the Right and Left Arrow Keys
            self.canvas.get_tk_widget().bind("<Right>", self.move_right_creep)
            self.canvas.get_tk_widget().bind("<Left>", self.move_left_creep)
            self.canvas.get_tk_widget().bind("<Return>", self.update_creep)
            self.canvas.get_tk_widget().focus_set() # Set Bindings

    # -- Move creep zone end point right
    def move_right_creep(self, event):
        # Remove the Previous Point
        self.plot1.lines.pop(len(self.plot1.lines)-1)
        self.canvas.draw()

        # Update the index
        mind_i = self.clicked_idx + 1
        if mind_i == self.max_idx_crp:
            mind_i = mind_i-1

        # Define the Point
        xc = self.Raw['Raw Data']['Time']['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][mind_i]
        yc = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][mind_i]
        self.clicked_idx = mind_i

        # Plot
        self.plot1.plot(xc,yc,self.color + 'o')
        self.canvas.draw()

    # -- Move creep zone end point left
    def move_left_creep(self, event):
        # Remove the Previous Point
        self.plot1.lines.pop(len(self.plot1.lines)-1)
        self.canvas.draw()

        # Update the index
        mind_i = self.clicked_idx - 1
        if mind_i == 0:
            mind_i = mind_i+1

        # Define the Point
        xc = self.Raw['Raw Data']['Time']['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][mind_i]
        yc = self.Raw['Raw Data']['Strain-'+self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][mind_i]
        self.clicked_idx = mind_i

        # Plot
        self.plot1.plot(xc,yc,self.color + 'o')
        self.canvas.draw()

    # -- Update the user defined creep zone end point
    def update_creep(self, event):
        # Turn on user edit flag
        self.user_opt['UserEdit']['Creep'] = 1

        # Determine if its tensile, compressive, or shear creep
        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            primary = self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]
            secondary = self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]
            tertiary = self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            primary = self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]
            secondary = self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]
            tertiary = self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            primary = self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]
            secondary = self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]
            tertiary = self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]

        # Get the current end points
        curr_idx = []
        if primary['Index']['Value'] != []:
            curr_idx.append(primary['Index']['Value'][-1])
        else:
            curr_idx.append(-1)
        if secondary['Index'] != []:
            curr_idx.append(secondary['Index']['Value'][-1])
        else:
            curr_idx.append(-1)

        # Get the selected value
        zone = self.creep_edit_opt.get()
        if zone == 'Primary':
           curr_idx[0] = self.clicked_idx
        else:
            curr_idx[1] = self.clicked_idx

        # Reset Values
        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Strain Rate']['Value'] = None

            self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Strain Rate']['Value'] = None

            self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Strain Rate']['Value'] = None

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Strain Rate']['Value'] = None

            self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Strain Rate']['Value'] = None

            self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Strain Rate']['Value'] = None

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Strain Rate']['Value'] = None

            self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Strain Rate']['Value'] = None

            self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Time']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Strain']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Stress']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Index']['Value'] = []
            self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Strain Rate']['Value'] = None

        # Set Primary Creep Values Manually
        time = []
        strain = []
        stress = []
        index = []
        for i in range(curr_idx[0]):
            time.append(self.Raw['Raw Data']['Time']['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
            strain.append(self.Raw['Raw Data']['Strain-' + self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
            stress.append(self.Raw['Raw Data']['Stress-' + self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
            index.append(i)

        strain_rate_info = scipy.stats.linregress(time, strain)

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Time']['Value'] = time
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Strain']['Value'] = strain
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Stress']['Value'] = stress
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Index']['Value'] = index
            self.Analysis['Creep Analysis']['Primary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['ime']['Value'] = time
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Strain']['Value'] = strain
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Stress']['Value'] = stress
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Index']['Value'] = index
            self.Analysis['Creep Analysis']['Compressive Primary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

        if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['ime']['Value'] = time
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Strain']['Value'] = strain
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Stress']['Value'] = stress
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Index']['Value'] = index
            self.Analysis['Creep Analysis']['Shear Primary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

         # Set Secondary Creep Values Manually
        if curr_idx[1] > curr_idx[0]+1:
            time = []
            strain = []
            stress = []
            index = []
            for i in range(curr_idx[0], curr_idx[1]):
                time.append(self.Raw['Raw Data']['Time']['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
                strain.append(self.Raw['Raw Data']['Strain-' + self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
                stress.append(self.Raw['Raw Data']['Stress-' + self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
                index.append(i)

            strain_rate_info = scipy.stats.linregress(time, strain)

            if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
                self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Time']['Value'] = time
                self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Strain']['Value'] = strain
                self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Stress']['Value'] = stress
                self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Index']['Value'] = index
                self.Analysis['Creep Analysis']['Secondary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

            if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
                self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['ime']['Value'] = time
                self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Strain']['Value'] = strain
                self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Stress']['Value'] = stress
                self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Index']['Value'] = index
                self.Analysis['Creep Analysis']['Compressive Secondary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

            if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
                self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['ime']['Value'] = time
                self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Strain']['Value'] = strain
                self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Stress']['Value'] = stress
                self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Index']['Value'] = index
                self.Analysis['Creep Analysis']['Shear Secondary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

            # Set Tertiary Creep Manually
            if curr_idx[1] < self.max_idx_crp-1:
                time = []
                strain = []
                stress = []
                index = []

                for i in range(curr_idx[1], self.max_idx_crp):
                    time.append(self.Raw['Raw Data']['Time']['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
                    strain.append(self.Raw['Raw Data']['Strain-' + self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
                    stress.append(self.Raw['Raw Data']['Stress-' + self.dir]['Value'][self.Analysis['Stages']['End Index']['Value'][0]:self.Analysis['Stages']['End Index']['Value'][1]][i])
                    index.append(i)

                strain_rate_info = scipy.stats.linregress(time, strain)

                if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Tensile Loading':
                    self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Time']['Value'] = time
                    self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Strain']['Value'] = strain
                    self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Stress']['Value'] = stress
                    self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Index']['Value'] = index
                    self.Analysis['Creep Analysis']['Tertiary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

                if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Compressive Loading':
                    self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['ime']['Value'] = time
                    self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Strain']['Value'] = strain
                    self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Stress']['Value'] = stress
                    self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Index']['Value'] = index
                    self.Analysis['Creep Analysis']['Compressive Tertiary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope

                if self.Analysis['Stages']['Stage Type']['Value'][0] == 'Shear Loading':
                    self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['ime']['Value'] = time
                    self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Strain']['Value'] = strain
                    self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Stress']['Value'] = stress
                    self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Index']['Value'] = index
                    self.Analysis['Creep Analysis']['Shear Tertiary Creep-' + self.dir]['Strain Rate']['Value'] = strain_rate_info.slope
        
        # Replot the Creep Analysis
        self.clicked_creep = 0
        from GUI.CreepPropertyPlot import CreepPropertyPlot
        CreepPropertyPlot(self, window)

        # Reanalyze the stages
        self.reanalyze_stages()

        # Reload the Page
        self.create_prop_table()
        self.prop_opt.set('Creep Analysis') 

        from GUI.PropDisplay import PropDisplay
        PropDisplay(self, window)

    # -- Continue analysis or save files
    def continue_analysis(self):
        
        # Delete any existing tables
        # -- Delete the stages table
        if hasattr(self, 'stage_table'):
            self.stage_table.destroy()
        # -- Delete the stages plot, plot menus, and plot button
        if hasattr(self, 'A2_btn4'):
            self.A2_btn4.destroy()
            self.x_plot_menu.destroy()
            self.y_plot_menu.destroy()
            self.vs_label.destroy()
            self.toolbar.destroy()
            self.canvas.get_tk_widget().destroy()
        # -- Delete the properties table
        if hasattr(self, 'prop_table'):
            self.prop_table.destroy()
        # -- Delete property option menu
        if hasattr(self, 'prop_opt_menu'):
            self.prop_opt_menu.destroy()
        # -- Delete the 'Get Properties' button
        if hasattr(self, 'A2_btn3'):
            self.A2_btn3.destroy()
        # -- Delete the property plot, plot menus, and plot button
        if hasattr(self, 'A2_btn5'):
            self.A2_btn5.destroy()
            self.prop_plot_menu.destroy()
            self.toolbar.destroy()
            self.canvas.get_tk_widget().destroy()
        # -- Delete the 'Reanalyze Stages' button
        if hasattr(self, 'A2_btn6'):
            self.A2_btn6.destroy()
        if hasattr(self, 'edit_creep_menu'):
            self.edit_creep_menu.destroy()
        # -- Delete the 'Edit Creep' button
        if hasattr(self, 'edit_creep_btn'):
            self.edit_creep_btn.destroy()

        # -- Delete the Continue Button
        self.GA_cont.destroy()
        # -- Delete Stage and Properties Buttons
        self.GA_btn1.destroy() 
        self.GA_btn2.destroy() 

        # Ask user for any additional notes
        self.add_notes_end = tk.Label(window, text = "Additional Test/Analysis Notes:",font = (fontname, 12), bg = bg_color)
        self.add_notes_end.place(anchor = 'n', relx = 0.5, rely = 0.3)
        self.add_notes_entry = tk.Text(window, width = 100, height = 8, font = (fontname, 12), bg = bg_color)
        self.add_notes_entry.place(anchor = 'n', relx = 0.5, rely = 0.35)
        self.add_notes_cont = tk.Button(window, text = "Continue", command = self.run_next_or_save, 
                                    font = (fontname, fsize_s), bg = 'light green')
        self.add_notes_cont.place(anchor = 'n', relx = 0.9675, rely = 0.94)

    # Run next test or save all files to the chosen directory
    def run_next_or_save(self):
        # Set the analysis notes
        self.Analysis['General Information']['Analysis Notes']['Value'] = self.add_info[self.fcount][3] + '\n' + self.add_notes_entry.get("1.0", "end-1c")

        # Resave Analysis Neutral File
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
            
        with open(self.Analysis_file, "w") as outfile: 
            json.dump(self.Analysis, outfile, cls=NpEncoder)

        # Update the output files list
        self.outfiles.append(self.Analysis_file)

        # Delete attributes from save
        self.add_notes_cont.destroy()
        self.add_notes_end.destroy()
        self.add_notes_entry.destroy()

        # Update the file counter
        self.fcount = self.fcount + 1
        if self.fcount < len(self.raw_files):
            self.f= open(self.raw_files[self.fcount])  #Get the next file
            self.Rdict = json.load(self.f) 

            # Reset the user options
            self.user_opt['UserEdit']['Creep'] = 0
            self.user_opt['UserEdit']['Modulus'] = 0
            self.user_opt['UserEdit']['Prop'] = 0

            # Perform the analysis
            from TMAnalysis import TMAnalysisEngine
            self.Raw, self.Analysis, self.dir, err_flag, msg, self.Analysis_file = TMAnalysisEngine(self.raw_files[self.fcount], 0, self.user_opt)

            if err_flag == 0:
                from GUI.GeneralAnalysis import GeneralAnalysis
                GeneralAnalysis(self, window)

            else:
                # Raw Data incorrect - display error message and continue
                messagebox.showinfo(title='Error', message='Error in test ' + self.raw_files[self.fcount] + ':' + msg)
                self.continue_analysis()

        else:
            # Ask user where to save files
            dir = filedialog.askdirectory()

            # Move files
            for k in range(len(self.outfiles)):
                shutil.move(self.outfiles[k],os.path.join(dir,os.path.basename(self.outfiles[k])))

            # Build the Analysis Module Entry Point
            from GUI.FileSelection import FileSelection
            FileSelection(self,window)

#Call the GUI
TMAnalysis_GUI()
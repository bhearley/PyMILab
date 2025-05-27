#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   UserOptions.py
#
#   PURPOSE: Allow user to set user options. Users can add additional plotting, set custom yeild values, and define tests as tested to failure and valid (Yes/No). 
#            Users can also add notes to each test analyzed.
#
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#       frmt    format vector
#
#-----------------------------------------------------------------------------------------
def UserOptions(self,window,frmt):
    #Import Modules
    import os
    import tkinter as tk
    import tksheet

    #Unpack Formatting
    bg_color = frmt[0] 
    fontname = frmt[1]
    fsize_s = frmt[2]
    fsize_l = frmt[3]
    fsize_t = frmt[4]

    #Initialize list of attributes for each page
    self.att_list = {'UserOptions':[]}

    # Update Yield Table Function
    def update_yield_table(value):
        # Save Previous Data and Destory Table
        curr_vals = []
        if hasattr(self,'yield_table'):
            # -- Get Sheet Data
            table_data = self.yield_table.get_sheet_data(return_copy = False, get_header = False, get_index = False)
            
            # -- Save Current Values
            for k in range(len(table_data)):
                curr_vals.append(table_data[k][0])
            
            # -- Destroy Table
            self.yield_table.destroy()

        # Create Yield Table
        hdrs =  ['Offset Strain (-)']
        self.yield_table = tksheet.Sheet(window, total_rows = value, total_columns = 1, 
                                    headers = hdrs,
                                    width = 155, height = 150, show_x_scrollbar = False, show_y_scrollbar = False,
                                    font = (fontname,12,"normal"),
                                    header_font = (fontname,12,"bold"))
        self.yield_table.place(anchor = 'n', relx = 0.5, rely = 0.35)
        self.yield_table.change_theme("blue")

        # -- Enable Bindings
        self.yield_table.enable_bindings('single_select','cell_select',  'edit_cell',"copy", "paste","arrowkeys")

        # -- Add yield table to list of widgets
        if "yield_table" not in self.att_list['UserOptions']:
            self.att_list['UserOptions'].append('self.yield_table')
        
        # -- Populate table with current values
        for k in range(min([len(curr_vals),value])):
            self.yield_table.set_cell_data(k,0,curr_vals[k])

    # Create checkbutton for additional plotting
    self.UO_chkval1 = tk.IntVar()
    self.UO_chk1 = tk.Checkbutton(window, text = "Additional Plots", 
                    variable = self.UO_chkval1, 
                    onvalue = 1, 
                    offvalue = 0, 
                    height = 2, 
                    width = 15,
                    bg = bg_color,
                    font = fsize_s)
    self.UO_chk1.place(anchor = 'n', relx = 0.5, rely = 0.2)
    self.att_list['UserOptions'].append('self.UO_chk1')

    # Create table for Custom Yield
    # -- Create Text Label
    var = tk.StringVar()
    self.UO_label1 = tk.Label(window, textvariable=var, bg = bg_color, font = fsize_s)
    var.set("Number of Custom Yield Points: ")
    self.UO_label1.place(anchor = 'n', relx = 0.475, rely = 0.3)
    self.att_list['UserOptions'].append('self.UO_label1')

    #  -- Create Number Input
    yield_opts = [0,1,2,3,4,5]
    self.yield_var = tk.StringVar(window)
    self.yield_var.set(yield_opts[0]) 
    self.yield_menu = tk.OptionMenu(window, self.yield_var, *yield_opts, command = update_yield_table) 
    self.yield_menu.place(anchor = 'n', relx = 0.60, rely = 0.3)
    self.att_list['UserOptions'].append('self.yield_menu')

    # Create Options for Failure and Valid Test
    # -- Create the table
    hdrs =  ['Test','Tested to Failure?', 'Valid Test?', 'Additional Notes']
    self.test_info_extra = tksheet.Sheet(window, total_rows = len(self.raw_files), total_columns = len(hdrs), 
                                headers = hdrs,
                                width = 950, height = 500, show_x_scrollbar = False, show_y_scrollbar = True,
                                font = (fontname,12,"normal"),
                                header_font = (fontname,12,"bold"))
    self.test_info_extra.place(anchor = 'n', relx = 0.5, rely = 0.55)
    self.test_info_extra.change_theme("blue")
    self.att_list['UserOptions'].append('self.test_info_extra')

    # -- Enable General Bindings
    self.test_info_extra.enable_bindings('single_select','cell_select', 'column_select', 'edit_cell',"right_click_popup_menu","copy", "paste","arrowkeys")

    # -- Function for additional bindings
    def on_cell_select(event):
        # -- If in the test name column, disable ability to edit cell and remove popup menu functions
        if event.column == 0:
            self.test_info_extra.disable_bindings("edit_cell")
            self.test_info_extra.popup_menu_del_command(label = "Change All to Yes")
            self.test_info_extra.popup_menu_del_command(label = "Change All to No")

        # -- If in the Failure or Valid Test name columns, enable ability to edit cell and add popup menu functions
        if event.column == 1 or event.column == 2:
            self.test_info_extra.enable_bindings("edit_cell")
            self.test_info_extra.popup_menu_add_command('Change All to Yes', all_to_yes, table_menu = True, index_menu = True, header_menu = True)
            self.test_info_extra.popup_menu_add_command('Change All to No', all_to_no, table_menu = True, index_menu = True, header_menu = True)

        # -- If in the additional info column, enable ability to edit cell and remove popup menu functions
        if event.column == 3:
            self.test_info_extra.enable_bindings("edit_cell")
            self.test_info_extra.popup_menu_del_command(label = "Change All to Yes")
            self.test_info_extra.popup_menu_del_command(label = "Change All to No")

    # -- Set bindings with functions
    self.test_info_extra.extra_bindings("cell_select", on_cell_select)
    self.test_info_extra.extra_bindings("column_select", on_cell_select)

    # -- Change all to yes
    def all_to_yes():
        currently_selected = self.test_info_extra.get_currently_selected()
        if currently_selected:
            row = currently_selected.row
            column = currently_selected.column

            if column == 1 or column == 2:
                for j in range(len(self.raw_files)):
                    self.test_info_extra.set_cell_data(j,column, 'Yes')
                self.test_info_extra.redraw()

    # -- Change all to no
    def all_to_no():
        currently_selected = self.test_info_extra.get_currently_selected()
        if currently_selected:
            row = currently_selected.row
            column = currently_selected.column
            if column == 1 or column == 2:
                for j in range(len(self.raw_files)):
                    self.test_info_extra.set_cell_data(j,column, 'No')
                self.test_info_extra.redraw()

    # Set Values
    for i in range(len(self.raw_files)):
        self.test_info_extra.set_cell_data(i,0,os.path.basename(self.raw_files[i]))
        self.test_info_extra.create_dropdown(r=i, c = 1,values=['Yes','No'])
        self.test_info_extra.create_dropdown(r=i, c = 2,values=['Yes','No'])

    # Formt Columns
    self.test_info_extra.column_width(column = 0, width = 250, redraw = True)
    self.test_info_extra.column_width(column = 1, width = 120, redraw = True)
    self.test_info_extra.column_width(column = 2, width = 120, redraw = True)
    self.test_info_extra.column_width(column = 3, width = 400, redraw = True)

    # Create the continue button
    self.UO_btn1 = tk.Button(window, text = "Continue", command = self.begin_analysis, 
                                font = (fontname, fsize_s), bg = 'light green')
    self.UO_btn1.place(anchor = 'n', relx = 0.9675, rely = 0.94)
    self.att_list['UserOptions'].append('self.UO_btn1')
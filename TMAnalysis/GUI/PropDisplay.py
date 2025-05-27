#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   PropertyPlot.py
#
#   PURPOSE: Build the Full Property Plots
#    
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#       frmt    GUI formatting
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def PropDisplay(self, window, frmt):
    # Import modules
    import tkinter as tk
    import tkinter.font as tkFont
    import tksheet

    # Import Functions
    from TMAnalysis.GUI.CompressivePropertyPlot import CompressivePropertyPlot
    from TMAnalysis.GUI.CreepPropertyPlot import CreepPropertyPlot
    from TMAnalysis.GUI.RelaxationPropertyPlot import RelaxationPropertyPlot
    from TMAnalysis.GUI.ShearPropertyPlot import ShearPropertyPlot
    from TMAnalysis.GUI.TensilePropertyPlot import TensilePropertyPlot

    # Delete any existing tables
    # -- Delete Previous Proprties Table
    if hasattr(self, 'prop_table'):
        self.prop_table.destroy()
    # -- Delete the property plot, plot menus, and plot button
    if hasattr(self, 'A2_btn5'):
        self.A2_btn5.destroy()
        self.prop_plot_menu.destroy()
        self.toolbar.destroy()
        self.canvas.get_tk_widget().destroy()

    # Get selcted option
    prop = self.prop_opt.get()

    # Unpack Data
    Raw = self.Raw
    Analysis = self.Analysis
    dir = self.dir
    if dir == '11':
        diam_dir= '22'
        pr_dir = '12'
    if dir == '22':
        diam_dir= '22'
        pr_dir = '12'

    # Set Table Properties
    self.table_x = 0.175    # Property Table X Position
    self.table_y = 0.4      # Property Table Y Position
    self.table_w = 480      # Property Table Width
    self.table_h = 500      # Property Table Width

    # Set Plot Properties
    plot_menu_x = 0.75      # Plot Menu X Position
    plot_menu_y = 0.25      # Plot Menu Y Position
    plot_btn_x = 0.85       # Plot Button X Position
    plot_btn_y = 0.25       # Plot Button Y Position
    btn_width = 75          # Plot Button Width
    self.plt_x = 0.75       # Property Plot X Position
    self.plt_y = 0.275      # Property Plot Y Position
    self.tool_x = 0.845     # Property Plot Toolbar X Position
    self.tool_y = 0.975     # Property Plot Toolbar X Position

    # Set General Properties
    self.cali12= tkFont.Font(family='Calibri', # Font Name
                                size=12)          # Font Size

    # TENSILE PROPERTIES
    # Create the Tensile Properties Table
    if prop == 'Tensile Analysis':
        # Define the Properties
        prop_list_all = [
                        'Modulus-' + dir,
                        'Poissons Ratio-' + pr_dir,
                        'Proportional Limit-' + dir,
                        'Proportional Limit Strain-' + dir,
                        'Unloading Modulus-' + dir,
                        'Reversible Strain-' + dir,
                        'Irreversible Strain-' + dir,
                        'Ultimate Strength-' + dir,
                        'Strain at UTS-' + dir,
                        'Failure Strength-' + dir,
                        'Strain at Failure-' + dir,
                        'Strain Rate',
                        'Stress Rate'
                        ]
        unit_list_all = [
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        '-', 
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'],                       
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'] + '/' + Raw['Raw Data']['Units']['Time']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'] + '/' + Raw['Raw Data']['Units']['Time']['Value']
                        ]

        # Create the Prop and Unit List
        prop_list = []
        unit_list = []
        for i in range(4):
            prop_list.append(prop_list_all[i])
            unit_list.append(unit_list_all[i])

        if 'Yield Offset' in list(self.user_opt.keys()):
            for i in range(len(self.user_opt['Yield Offset'])):
                prop_list.append('Yield Offset Strain-' + dir + ' #' + str(i+1))
                prop_list.append('Yield Offset Stress-' + dir + ' #' + str(i+1))
                unit_list.append(Raw['Raw Data']['Units']['Strain']['Value'])
                unit_list.append(Raw['Raw Data']['Units']['Stress']['Value'])

        for i in range(4,len(prop_list_all)):
            prop_list.append(prop_list_all[i])
            unit_list.append(unit_list_all[i])

        # Create the Table
        self.prop_table = tksheet.Sheet(window, total_rows = len(prop_list), total_columns = 3, 
                            headers = ['Property', 'Value','Units'],
                            width = self.table_w, height = self.table_h, show_x_scrollbar = False, show_y_scrollbar = False)
        self.prop_table.place(anchor = 'n', relx = self.table_x, rely = self.table_y)

        # Add additional buttons to table menu
        self.prop_table.enable_bindings("right_click_popup_menu", 'single_select','cell_select', 'column_select','row_select')
        if Analysis['Tensile Analysis']['Proportional Limit-'+dir]['Value'] != None:
            self.prop_table.popup_menu_add_command('Edit Proportional Limit', self.edit_prop_lim, table_menu = True, index_menu = True, header_menu = True)

        if Analysis['Tensile Analysis']['Modulus-'+dir]['Value'] != None:
            self.prop_table.popup_menu_add_command('Edit Modulus', self.edit_modulus, table_menu = True, index_menu = True, header_menu = True)

        # Format Columns
        self.prop_table.column_width(column = 0, width = 280, redraw = True)
        self.prop_table.column_width(column = 1, width = 80, redraw = True)
        self.prop_table.column_width(column = 2, width = 80, redraw = True)

        # Get Plotting Option
        opt_cands = ['Stress vs Strain','Poissons Ratio','Strain Rate','Stress Rate']
        opts = []
        if Analysis['Tensile Analysis']['Modulus-' + dir]['Value'] != None:
            opts.append('Stress vs Strain')
        if Analysis['Tensile Analysis']['Poissons Ratio-' + pr_dir]['Value'] != None:
            opts.append('Poissons Ratio')
        if Analysis['Tensile Analysis']['Strain Rate']['Value'] != None:
            opts.append('Strain Rate')
        if Analysis['Tensile Analysis']['Stress Rate']['Value'] != None:
            opts.append('Stress Rate')
                
        # Create Tensile Properties Plot option menu for additional plotting
        self.prop_plot_opt = tk.StringVar(window)
        if len(opts) > 0:
            # Create the option menu
            self.prop_plot_opt.set(opts[0]) 
            self.prop_plot_menu = tk.OptionMenu(window, self.prop_plot_opt, *opts) 
            self.prop_plot_menu.place(anchor = 'e', relx = plot_menu_x, rely = plot_menu_y)
            self.prop_plot_menu.configure(font = self.cali12)
                
            # Create the button to plot
            self.A2_btn5 = tk.Button(window, text = "Plot", command = lambda: TensilePropertyPlot(self, window, frmt), 
                                    font = self.cali12, bg = 'light blue')
            self.A2_btn5.place(anchor = 'e', relx = plot_btn_x, rely = plot_btn_y, width = btn_width)

            # Plot
            TensilePropertyPlot(self, window, frmt)

    # COMPRESSIVE PROPERTIES
    # Create the Compressive Properties Table
    if prop == 'Compressive Analysis':
        # Define the Properties
        prop_list_all = [
                        'Compressive Modulus-' + dir,
                        'Compressive Poissons Ratio-' + pr_dir,
                        'Compressive Proportional Limit-' + dir,
                        'Compressive Proportional Limit Strain-' + dir,
                        'Compressive Unloading Modulus-' + dir,
                        'Compressive Reversible Strain-' + dir,
                        'Compressive Irreversible Strain-' + dir,
                        'Compressive Ultimate Strength-' + dir,
                        'Compressive Strain at UTS-' + dir,
                        'Compressive Failure Strength-' + dir,
                        'Compressive Strain at Failure-' + dir,
                        'Compressive Strain Rate',
                        'Compressive Stress Rate'
                        ]

        unit_list_all = [
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        '-', 
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'],                       
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'] + '/' + Raw['Raw Data']['Units']['Time']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'] + '/' + Raw['Raw Data']['Units']['Time']['Value']
                        ]

        # Create the Prop and Unit List
        prop_list = []
        unit_list = []
        for i in range(4):
            prop_list.append(prop_list_all[i])
            unit_list.append(unit_list_all[i])

        if 'Yield Offset' in list(self.user_opt.keys()):
            for i in range(len(self.user_opt['Yield Offset'])):
                prop_list.append('Yield Offset Strain-' + dir + ' ' + str(i+1))
                prop_list.append('Yield Offset Stress-' + dir + ' ' + str(i+1))
                unit_list.append(Raw['Raw Data']['Units']['Strain']['Value'])
                unit_list.append(Raw['Raw Data']['Units']['Stress']['Value'])

        for i in range(4,len(prop_list_all)):
            prop_list.append(prop_list_all[i])
            unit_list.append(unit_list_all[i])

        # Create the Table
        self.prop_table = tksheet.Sheet(window, total_rows = len(prop_list), total_columns = 3, 
                            headers = ['Property', 'Value','Units'],
                            width = self.table_w, height = self.table_h, show_x_scrollbar = False, show_y_scrollbar = False)
        self.prop_table.place(anchor = 'n', relx = self.table_x, rely = self.table_y)

        # Add additional buttons to table menu
        self.prop_table.enable_bindings("right_click_popup_menu", 'single_select','cell_select', 'column_select','row_select')
        if Analysis['Compressive Analysis']['Compressive Proportional Limit-'+dir]['Value'] != None:
            self.prop_table.popup_menu_add_command('Edit Proportional Limit', self.edit_prop_lim, table_menu = True, index_menu = True, header_menu = True)

        if Analysis['Compressive Analysis']['Compressive Modulus-'+dir]['Value'] != None:
            self.prop_table.popup_menu_add_command('Edit Modulus', self.edit_modulus, table_menu = True, index_menu = True, header_menu = True)

        # Format Columns
        self.prop_table.column_width(column = 0, width = 280, redraw = True)
        self.prop_table.column_width(column = 1, width = 80, redraw = True)
        self.prop_table.column_width(column = 2, width = 80, redraw = True)

        # Get Plotting Option
        opt_cands = ['Stress vs Strain','Poissons Ratio','Strain Rate','Stress Rate']
        opts = []
        if Analysis['Compressive Analysis']['Compressive Modulus-' + dir]['Value'] != None:
            opts.append('Stress vs Strain')
        if Analysis['Compressive Analysis']['Compressive Poissons Ratio-' + pr_dir]['Value'] != None:
            opts.append('Poissons Ratio')
        if Analysis['Compressive Analysis']['Compressive Strain Rate']['Value'] != None:
            opts.append('Strain Rate')
        if Analysis['Compressive Analysis']['Compressive Stress Rate']['Value'] != None:
            opts.append('Stress Rate')

        # Create Compressive Properties Plot option menu for additional ploting
        self.prop_plot_opt = tk.StringVar(window)
        if len(opts) > 0:
            # Create the option menu
            self.prop_plot_opt.set(opts[0]) 
            self.prop_plot_menu = tk.OptionMenu(window, self.prop_plot_opt, *opts) 
            self.prop_plot_menu.place(anchor = 'e', relx = plot_menu_x, rely = plot_menu_y)
            self.prop_plot_menu.configure(font = self.cali12)

            # Create the button to plot
            self.A2_btn5 = tk.Button(window, text = "Plot", command = lambda: CompressivePropertyPlot(self,window,frmt), 
                                    font = ('Calibiri', 12), bg = 'light blue')
            self.A2_btn5.place(anchor = 'e', relx = plot_btn_x, rely = plot_btn_y, width = btn_width)

            # Plot
            CompressivePropertyPlot(self,window,frmt)

    # SHEAR PROPERTIES
    # Create the Shear Properties Table
    if prop == 'Shear Analysis':
        # Define the Properties
        prop_list_all = [
                        'Shear Modulus-' + dir,
                        'Shear Proportional Limit-' + dir,
                        'Shear Proportional Limit Strain-' + dir,
                        'Shear Unloading Modulus-' + dir,
                        'Shear Reversible Strain-' + dir,
                        'Shear Irreversible Strain-' + dir,
                        'Shear Ultimate Strength-' + dir,
                        'Shear Strain at UTS-' + dir,
                        'Shear Failure Strength-' + dir,
                        'Shear Strain at Failure-' + dir,
                        'Shear Strain Rate',
                        'Shear Stress Rate'
                        ]

        unit_list_all = [
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'],                       
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'] + '/' + Raw['Raw Data']['Units']['Time']['Value'],
                        Raw['Raw Data']['Units']['Stress']['Value'] + '/' + Raw['Raw Data']['Units']['Time']['Value']
                        ]

        # Create the Prop and Unit List
        prop_list = []
        unit_list = []
        for i in range(3):
            prop_list.append(prop_list_all[i])
            unit_list.append(unit_list_all[i])

        if 'Yield Offset' in list(self.user_opt.keys()):
            for i in range(len(self.user_opt['Yield Offset'])):
                prop_list.append('Yield Offset Strain-' + dir + ' ' + str(i+1))
                prop_list.append('Yield Offset Stress-' + dir + ' ' + str(i+1))
                unit_list.append(Raw['Raw Data']['Units']['Strain']['Value'])
                unit_list.append(Raw['Raw Data']['Units']['Stress']['Value'])

        for i in range(4,len(prop_list_all)):
            prop_list.append(prop_list_all[i])
            unit_list.append(unit_list_all[i])

        # Create the Table
        self.prop_table = tksheet.Sheet(window, total_rows = len(prop_list), total_columns = 3, 
                            headers = ['Property', 'Value','Units'],
                            width = self.table_w, height = self.table_h, show_x_scrollbar = False, show_y_scrollbar = False)
        self.prop_table.place(anchor = 'n', relx = self.table_x, rely = self.table_y)

        # Add additional buttons for table menu
        self.prop_table.enable_bindings("right_click_popup_menu", 'single_select','cell_select', 'column_select','row_select')
        if Analysis['Shear Analysis']['Shear Proportional Limit-'+dir]['Value'] != None:
            self.prop_table.popup_menu_add_command('Edit Proportional Limit', self.edit_prop_lim, table_menu = True, index_menu = True, header_menu = True)

        if Analysis['Shear Analysis']['Shear Modulus-'+dir]['Value'] != None:
            self.prop_table.popup_menu_add_command('Edit Modulus', self.edit_modulus, table_menu = True, index_menu = True, header_menu = True)

        # Format Columns
        self.prop_table.column_width(column = 0, width = 280, redraw = True)
        self.prop_table.column_width(column = 1, width = 80, redraw = True)
        self.prop_table.column_width(column = 2, width = 80, redraw = True)

        # Get Plotting Option
        opt_cands = ['Stress vs Strain','Poissons Ratio','Strain Rate','Stress Rate']
        opts = []
        if Analysis['Shear Analysis']['Shear Modulus-' + dir]['Value'] != None:
            opts.append('Stress vs Strain')
        if Analysis['Shear Analysis']['Shear Strain Rate']['Value'] != None:
            opts.append('Strain Rate')
        if Analysis['Shear Analysis']['Shear Stress Rate']['Value'] != None:
            opts.append('Stress Rate')

        # Create Shear Properties Plot option menu for additional plotting
        self.prop_plot_opt = tk.StringVar(window)
        if len(opts) > 0:
            # Create the option menu
            self.prop_plot_opt.set(opts[0]) 
            self.prop_plot_menu = tk.OptionMenu(window, self.prop_plot_opt, *opts) 
            self.prop_plot_menu.place(anchor = 'e', relx = plot_menu_x, rely = plot_menu_y)
            self.prop_plot_menu.configure(font = self.cali12)

            # Creat the button to plot
            self.A2_btn5 = tk.Button(window, text = "Plot", command = lambda: ShearPropertyPlot(self,window,frmt), 
                                    font = ('Calibiri', 12), bg = 'light blue')
            self.A2_btn5.place(anchor = 'e', relx = plot_btn_x, rely = plot_btn_y, width = btn_width)

            # Plot
            ShearPropertyPlot(self,window,frmt)

    # RELAXATION PROPERTIES
    # Create the Relaxation Properties Table
    if prop == 'Relaxation Analysis':
        # Define the Properties
        prop_list = [
                        'Relaxation Hold Strain-' +dir, 
                        'Relaxation Total Time', 
                        'Relaxation Stress Drop-' + dir,
                        'Relaxation Reversible Strain-'+dir, 
                        'Relaxation Irreversible Strain-'+dir
                        ]

        unit_list = [
                        Raw['Raw Data']['Units']['Strain']['Value'], 
                        Raw['Raw Data']['Units']['Time']['Value'], 
                        Raw['Raw Data']['Units']['Stress']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value'],
                        Raw['Raw Data']['Units']['Strain']['Value']
                        ]

        # Create the Table
        self.prop_table = tksheet.Sheet(window, total_rows = len(prop_list), total_columns = 3, 
                            headers = ['Property', 'Value','Units'],
                            width = self.table_w, height = self.table_h, show_x_scrollbar = False, show_y_scrollbar = False)
        self.prop_table.place(anchor = 'n', relx = self.table_x, rely = self.table_y)

        # Format Columns
        self.prop_table.column_width(column = 0, width = 280, redraw = True)
        self.prop_table.column_width(column = 1, width = 80, redraw = True)
        self.prop_table.column_width(column = 2, width = 80, redraw = True)

        # Get Plotting Option
        opt_cands = ['Relaxation Stress vs Strain','Relaxation Strain vs Time','Relaxation Stress vs Time']
        opts = []
        if Analysis['Stages']['Stage Type']['Value'][1] == 'Relaxation':
            opts = opt_cands
           
        # Create Relaxation Properties Plot option menu for additional plotting
        self.prop_plot_opt = tk.StringVar(window)
        if len(opts) > 0:
            # Create the option menu
            self.prop_plot_opt.set(opts[2]) 
            self.prop_plot_menu = tk.OptionMenu(window, self.prop_plot_opt, *opts) 
            self.prop_plot_menu.place(anchor = 'e', relx = plot_menu_x, rely = plot_menu_y)
            self.prop_plot_menu.configure(font = self.cali12)

            # Create the button to plot
            self.A2_btn5 = tk.Button(window, text = "Plot", command = lambda:RelaxationPropertyPlot(self, window,frmt), 
                                    font = ('Calibiri', 12), bg = 'light blue')
            self.A2_btn5.place(anchor = 'e', relx = plot_btn_x, rely = plot_btn_y, width = btn_width)

            # Plot
            RelaxationPropertyPlot(self,window,frmt)

    # CREEP PROPERTIES
    # Create the Creep Properties Table
    if prop == 'Creep Analysis':
        # Define the Properties
        prop_list = [
                        'Creep Hold Stress-' + dir, 
                        'Creep Total Time-' + dir
                        ]
        unit_list = [
                        Raw['Raw Data']['Units']['Stress']['Value'], 
                        Raw['Raw Data']['Units']['Time']['Value']
                        ]
            
        # Create the Table
        self.prop_table = tksheet.Sheet(window, total_rows = len(prop_list), total_columns = 3, 
                            headers = ['Property', 'Value','Units'],
                            width = self.table_w, height = self.table_h, show_x_scrollbar = False, show_y_scrollbar = False)
        self.prop_table.place(anchor = 'n', relx = self.table_x, rely = self.table_y)

        # Format Columns
        self.prop_table.column_width(column = 0, width = 280, redraw = True)
        self.prop_table.column_width(column = 1, width = 80, redraw = True)
        self.prop_table.column_width(column = 2, width = 80, redraw = True)

        # Get Plotting Option
        opt_cands = ['Creep Stress vs Strain','Creep Strain vs Time','Creep Stress vs Time']
        opts = []
        if Analysis['Stages']['Stage Type']['Value'][1] == 'Creep':
            opts = opt_cands

        # Create Creep Properties Plot option menu
        self.prop_plot_opt = tk.StringVar(window)
        if len(opts) > 0:
            # Create the option menu
            self.prop_plot_opt.set(opts[1]) 
            self.prop_plot_menu = tk.OptionMenu(window, self.prop_plot_opt, *opts) 
            self.prop_plot_menu.place(anchor = 'e', relx = plot_menu_x, rely = plot_menu_y)
            self.prop_plot_menu.configure(font = self.cali12)

            # Create the button to plot
            self.A2_btn5 = tk.Button(window, text = "Plot", command = lambda: CreepPropertyPlot(self, window, frmt), 
                                    font = ('Calibiri', 12), bg = 'light blue')
            self.A2_btn5.place(anchor = 'e', relx = plot_btn_x, rely = plot_btn_y, width = btn_width)

            # Plot
            CreepPropertyPlot(self, window, frmt)

    # Populate the properties table             
    ct_yld = 0 # Counter for additional yeild offsets to display (Custom Analysis Values)

    # Loop through all variables in property list
    for i in range(len(prop_list)):
        self.prop_table.set_cell_data(i,0,prop_list[i])
        # Non-Custom Analysis Values
        if prop_list[i] in list(Analysis[prop].keys()):
            if Analysis[prop][prop_list[i]]['Value'] != None:
                if Analysis[prop][prop_list[i]]['Value'] > 0.01 and Analysis[prop][prop_list[i]]['Value'] < 1000:
                    self.prop_table.set_cell_data(i,1,str(round(Analysis[prop][prop_list[i]]['Value'],2)))
                else:
                    self.prop_table.set_cell_data(i,1,f'{Analysis[prop][prop_list[i]]["Value"]:.3e}')
                self.prop_table.set_cell_data(i,2,unit_list[i])

        # Custom Analysis Values
        else:
            # Custom Yield
            if 'Yield' in prop_list[i]:
                if "Shear" in prop:
                    att = "Shear Yeld-" + dir
                elif "Compressive" in prop:
                    att = "Compressive Yield-" + dir
                else:
                    att = "Yield-" + dir
                if ct_yld < len(Analysis[prop][att]["Offset Strain"]["Value"]):
                    if 'Strain' in prop_list[i]:
                        self.prop_table.set_cell_data(i,1,f'{Analysis[prop][att]["Offset Strain"]["Value"][ct_yld]:.3e}')
                    else:
                        self.prop_table.set_cell_data(i,1,str(round(Analysis[prop][att]["Yield Strength"]["Value"][ct_yld],2)))
                        ct_yld = ct_yld+1

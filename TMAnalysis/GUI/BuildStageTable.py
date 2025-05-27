#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   BuildStageTable.py
#
#   PURPOSE: Build the Stage table. 
#
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#       frmt    GUI formatting
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def Build_Stage_Table(self, window, frmt):      
    # Import Modules
    import tkinter as tk
    import tkinter.font as tkFont
    import tksheet
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

    # Unpack frmt
    bg_color = frmt[0]
    fontname = frmt[1]           
    fsize_s = frmt[2]
    fsize_l = frmt[3]
    fsize_t = frmt[4]

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
    # -- Delete the 'Edit Creep' drop down menu
    if hasattr(self, 'edit_creep_menu'):
        self.edit_creep_menu.destroy()
    # -- Delete the 'Edit Creep' button
    if hasattr(self, 'edit_creep_btn'):
        self.edit_creep_btn.destroy()

    # Unpack Data for convenienance
    Raw = self.Raw
    Analysis = self.Analysis
    dir = self.dir

    # Create the Stage Table
    hdrs =  ['Stage Name', 'Stage Type', 'Control Mode', 'Target Strain-' + dir, 'Target Stress-' + dir, 'Target Time', 'End Index']
    self.stage_table = tksheet.Sheet(window, total_rows = len(Analysis['Stages']['End Index']['Value']), total_columns = 7, 
                                headers = ['Stage Name', 'Stage Type', 'Control Mode', 'Target Strain [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']', 
                                           'Target Stress [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']', 'End Time [' + Raw['Raw Data']['Units']['Time']['Value'] + ']', 
                                           'End Index'],
                                width = 790, height = 550, show_x_scrollbar = False, show_y_scrollbar = True)
    self.stage_table.place(anchor = 'n', relx = 0.26, rely = 0.30)

    # Set the Stage Table Drop Down Lists
    for k in range(len(Analysis['Stages']['End Index']['Value'])):
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

    # Populate the Stage Table
    for i in range(len(Analysis['Stages']['End Index']['Value'])):
        for j in range(3):
            self.stage_table.set_cell_data(i,j,Analysis['Stages'][hdrs[j]]['Value'][i])
        self.stage_table.set_cell_data(i,3,round(Raw['Raw Data']['Strain-'+dir]['Value'][Analysis['Stages']['End Index']['Value'][i]],2))
        self.stage_table.set_cell_data(i,4,round(Raw['Raw Data']['Stress-'+dir]['Value'][Analysis['Stages']['End Index']['Value'][i]],2))
        self.stage_table.set_cell_data(i,5,round(Raw['Raw Data']['Time']['Value'][Analysis['Stages']['End Index']['Value'][i]],2))
        self.stage_table.set_cell_data(i,6,Analysis['Stages']['End Index']['Value'][i])

    # Format Columns
    self.stage_table.column_width(column = 0, width = 80, redraw = True)
    self.stage_table.column_width(column = 1, width = 140, redraw = True)
    self.stage_table.column_width(column = 2, width = 90, redraw = True)
    self.stage_table.column_width(column = 3, width = 120, redraw = True)
    self.stage_table.column_width(column = 4, width = 120, redraw = True)
    self.stage_table.column_width(column = 5, width = 100, redraw = True)
    self.stage_table.column_width(column = 6, width = 80, redraw = True)

    # Enable Bindings
    self.stage_table.enable_bindings('all')

    # Add Custom button for adding and removing stages
    self.stage_table.disable_bindings("rc_insert_row")
    self.stage_table.popup_menu_add_command('Insert Stage Above', self.insert_stage_above, table_menu = True, index_menu = True, header_menu = True)
    self.stage_table.popup_menu_add_command('Insert Stage Below', self.insert_stage_below, table_menu = True, index_menu = True, header_menu = True)

    # Enable Editing Rows
    self.selected_row = -1
    self.stage_table.popup_menu_add_command('Edit Stage Start Point with Plot', self.edit_stage_start, table_menu = True, index_menu = True, header_menu = True)
    self.stage_table.popup_menu_add_command('Edit Stage End Point with Plot', self.edit_stage_end, table_menu = True, index_menu = True, header_menu = True)

    # Create the Stages Plot
    def plot_stages():
        # Delete existing canvas
        if hasattr(self, 'canvas'):
            self.toolbar.destroy()
            self.canvas.get_tk_widget().destroy()

        # Get the X and Y label for the plot
        xlabel = prop = self.x_plot_opt.get()
        ylabel = prop = self.y_plot_opt.get()
        
        # Set Color Options
        color_opts = ['royalblue','darkorange','limegreen','red','orchid','maroon','deeppink','steelblue','saddlebrown']
        color_ct = 0 

        # Create Figure
        self.fig = Figure(figsize=(5,4.25), dpi = 125)
        self.plot1 = self.fig.add_subplot(111)

        # Get Load Segments
        for i in range(len(Analysis['Stages']['End Index']['Value'])):
            # -- Get Start and End Index
            if i == 0:
                start_idx = 0
                end_idx = Analysis['Stages']['End Index']['Value'][i]+1
            else:
                start_idx = Analysis['Stages']['End Index']['Value'][i-1]
                end_idx = Analysis['Stages']['End Index']['Value'][i]

            if end_idx == len(Raw['Raw Data'][xlabel]['Value']):
                end_idx = end_idx - 1

            # Set Stage Color
            clr = color_opts[color_ct]
            color_ct = color_ct+1
            if color_ct == len(color_opts):
                color_ct = 0

            # Plot
            self.plot1.plot(Raw['Raw Data'][xlabel]['Value'][start_idx:end_idx],Raw['Raw Data'][ylabel]['Value'][start_idx:end_idx],color = clr, linewidth=1)
            self.plot1.plot(Raw['Raw Data'][xlabel]['Value'][end_idx],Raw['Raw Data'][ylabel]['Value'][end_idx],color = clr, marker = 'o')

        # Set Axes Labels
        # -- X
        if 'Stress' in xlabel:
            xlab = xlabel + ' [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']'
        elif 'Strain' in xlabel:
            xlab = xlabel + ' [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']'
        elif 'Time' in xlabel:
            xlab = xlabel + ' [' + Raw['Raw Data']['Units']['Time']['Value'] + ']'
        else:
            xlab = xlabel

        # -- Y
        if 'Stress' in ylabel:
            ylab = ylabel + ' [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']'
        elif 'Strain' in ylabel:
            ylab = ylabel + ' [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']'
        elif 'Time' in ylabel:
            ylab = ylabel + ' [' + Raw['Raw Data']['Units']['Time']['Value'] + ']'
        else:
            ylab = ylabel

        self.plot1.set_xlabel(xlab)
        self.plot1.set_ylabel(ylab)

        # Create the Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master = window)
        self.canvas.draw()
        # Create the Matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, window)
        self.toolbar.update()
        # Format Toolbar
        self.toolbar.config(bg=bg_color)
        self.toolbar._message_label.config(background=bg_color)
        self.toolbar.place(anchor = 'e', relx = 0.825, rely = 0.975)
        # Add the figure to the GUI
        self.canvas.get_tk_widget().place(anchor = 'n', relx = 0.75, rely = 0.275)

    # Create X-Y Option Menus for plotting
    opts = []
    diam_dir = '33'
    if dir == '11':
        diam_dir= '22'
        pr_dir = '12'
    if dir == '22':
        diam_dir= '11'
        pr_dir = '12'
    
    opt_cad = ['Time','Strain-' + dir, 'Strain-'+diam_dir, 'Stress-'+dir, 'Index']
    for j in range(len(opt_cad)):
        if len(Raw['Raw Data'][opt_cad[j]]['Value']) > 0:
            opts.append(opt_cad[j])

    self.x_plot_opt = tk.StringVar(window) 
    self.y_plot_opt = tk.StringVar(window) 
  
    # Set the default value of the variable 
    self.x_plot_opt.set('Strain-'+dir) 
    self.y_plot_opt.set('Stress-'+dir) 
  
    # Create the option menus
    self.cali12= tkFont.Font(family='Calibri', size=12)

    # -- X
    self.x_plot_menu = tk.OptionMenu(window, self.x_plot_opt, *opts) 
    self.x_plot_menu.place(anchor = 'e', relx = 0.675, rely = 0.25)
    self.x_plot_menu.configure(font = self.cali12)

    # -- Y
    self.y_plot_menu = tk.OptionMenu(window, self.y_plot_opt, *opts) 
    self.y_plot_menu.place(anchor = 'e', relx = 0.78, rely = 0.25)
    self.y_plot_menu.configure(font = self.cali12)

    # Create the Plot Button
    self.A2_btn4 = tk.Button(window, text = "Plot", command = plot_stages, width = 10,
                            font = (fontname, 12), bg = 'light blue')
    self.A2_btn4.place(anchor = 'e', relx = 0.9, rely = 0.25)

    # Create "vs" label
    self.vs_label = tk.Label(window, text = "vs.",font = (fontname, 12), bg = bg_color)
    self.vs_label.place(anchor = 'e', relx = 0.7, rely = 0.25)

    # Initialize the plot
    plot_stages()

    # Create the ReAnalyze Button
    self.A2_btn6 = tk.Button(window, text = "Reanalyze Stages", command = self.reanalyze_stages, 
                            font = (fontname, fsize_s), bg = 'light blue')
    self.A2_btn6.place(anchor = 'n', relx = 0.265, rely = 0.225)
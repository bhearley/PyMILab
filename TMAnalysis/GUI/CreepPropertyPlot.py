#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   CreepPropertyPlot.py
#
#   PURPOSE: Build the Creep Property Additional Plotting Capability
#    
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CreepPropertyPlot(self, window):
    # Import Modules
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
    from matplotlib.backend_bases import MouseButton
    from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
    import numpy as np
    import tkinter as tk

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

    #  Delete the canvas if it exists
    if hasattr(self, 'canvas'):
        self.toolbar.destroy()
        self.canvas.get_tk_widget().destroy()

    # Create Figure
    self.fig = Figure(figsize=(self.Placement['PropTable']['Figure1'][2],self.Placement['PropTable']['Figure1'][3]), dpi = self.Placement['PropTable']['Figure1'][4])
    self.fig.subplots_adjust(left=0.1, right=0.975, top=0.95, bottom=0.15)
    self.plot1 = self.fig.add_subplot(111)

    # Get the option
    creep_opt = self.prop_plot_opt.get()

    # Get the Creep Zone Indexes
    creep_idx = []
    creep_label = []
    creep_clr = []
                
    if Analysis['Creep Analysis']['Primary Creep-'+dir]['Index']['Value'] == []:
        creep_idx = [[Analysis['Stages']['End Index']['Value'][0]],Analysis['Stages']['End Index']['Value'][1]]
        creep_label = ['']
        creep_clr = ['k']
    else:
        start_idx = Analysis['Stages']['End Index']['Value'][0] + Analysis['Creep Analysis']['Primary Creep-'+dir]['Index']['Value'][0]
        end_idx = Analysis['Stages']['End Index']['Value'][0] + Analysis['Creep Analysis']['Primary Creep-'+dir]['Index']['Value'][-1]
        creep_idx.append([start_idx,end_idx])
        creep_label.append('Primary Zone')
        creep_clr.append('r')
        if Analysis['Creep Analysis']['Secondary Creep-'+dir]['Index']['Value'] != []:
            start_idx = Analysis['Stages']['End Index']['Value'][0] + Analysis['Creep Analysis']['Secondary Creep-'+dir]['Index']['Value'][0]
            end_idx = Analysis['Stages']['End Index']['Value'][0] + Analysis['Creep Analysis']['Secondary Creep-'+dir]['Index']['Value'][-1]
            creep_idx.append([start_idx,end_idx])
            creep_label.append('Secondary Zone')
            creep_clr.append('b')
            if Analysis['Creep Analysis']['Tertiary Creep-'+dir]['Index']['Value']  != []:
                start_idx = Analysis['Stages']['End Index']['Value'][0] + Analysis['Creep Analysis']['Tertiary Creep-'+dir]['Index']['Value'][0]
                end_idx = Analysis['Stages']['End Index']['Value'][0] + Analysis['Creep Analysis']['Tertiary Creep-'+dir]['Index']['Value'][-1]
                creep_idx.append([start_idx,end_idx])
                creep_label.append('Tertiary Zone')
                creep_clr.append('g')


    # Option 1 - Relaxation Stress vs Strain
    if creep_opt == 'Creep Stress vs Strain':
        for c in range(len(creep_label)):
            # -- Unpack stress and strain
            strain = Raw['Raw Data']['Strain-'+dir]['Value'][creep_idx[c][0]:creep_idx[c][1]]
            stress = Raw['Raw Data']['Stress-'+dir]['Value'][creep_idx[c][0]:creep_idx[c][1]]
            # -- Plot
            self.plot1.plot(strain, stress,creep_clr[c],label = creep_label[c])

        if hasattr(self,'edit_creep_menu') == True:
            self.edit_creep_menu.destroy()
            self.edit_creep_btn.destroy()

        # -- Set Formatting
        xlab = 'Strain ' + ' [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']'
        ylab = 'Stress ' + ' [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']'

        xlab_frmt = ScalarFormatter() 
        ylab_frmt = FormatStrFormatter('%.1f')

    # Option 2 - Creep Strain vs Time
    elif creep_opt == 'Creep Strain vs Time':
        for c in range(len(creep_label)):
            # -- Unpack time and strain
            time = Raw['Raw Data']['Time']['Value'][creep_idx[c][0]:creep_idx[c][1]]
            strain = Raw['Raw Data']['Strain-'+dir]['Value'][creep_idx[c][0]:creep_idx[c][1]]
                        
            # -- Plot
            self.plot1.plot(time, strain, creep_clr[c],label = creep_label[c])

        if hasattr(self,'edit_creep_menu') == True:
            self.edit_creep_menu.destroy()
            self.edit_creep_btn.destroy()

        # Create the option menu to edit creep stages
        opts_creep = ['Select Zone to Edit Endpoint', 'Primary', 'Secondary']
        self.creep_edit_opt = tk.StringVar(window)
        self.creep_edit_opt.set(opts_creep[0]) 
        self.edit_creep_menu = tk.OptionMenu(window, self.creep_edit_opt, *opts_creep) 
        self.edit_creep_menu.place(anchor = 'n', relx = self.table_x, rely = self.table_y + 0.2)
        self.edit_creep_menu.configure(font = self.cali12)

        self.edit_creep_btn = tk.Button(window, text = "Edit on Plot", command = self.edit_creep, 
                                font = ('Calibiri', 12), bg = 'light goldenrod', width = 20)
        self.edit_creep_btn.place(anchor = 'n', relx = self.table_x, rely = self.table_y + 0.25)

        # -- Set Formatting
        xlab = 'Time ' + ' [' + Raw['Raw Data']['Units']['Time']['Value'] + ']'
        ylab = 'Strain ' + ' [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']'

        xlab_frmt = ScalarFormatter() 
        ylab_frmt = ScalarFormatter()

    # Option 3 - Creep Stress vs Time
    elif creep_opt == 'Creep Stress vs Time':
        for c in range(len(creep_label)):
            # -- Unpack time and stress
            time = Raw['Raw Data']['Time']['Value'][creep_idx[c][0]:creep_idx[c][1]]
            stress = Raw['Raw Data']['Stress-'+dir]['Value'][creep_idx[c][0]:creep_idx[c][1]]
                        
            # -- Plot
            self.plot1.plot(time, stress,creep_clr[c],label = creep_label[c])

        if hasattr(self,'edit_creep_menu') == True:
            self.edit_creep_menu.destroy()
            self.edit_creep_btn.destroy()

        # -- Set Formatting
        xlab = 'Time ' + ' [' + Raw['Raw Data']['Units']['Time']['Value'] + ']'
        ylab = 'Stress ' + ' [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']'

        xlab_frmt = ScalarFormatter() 
        ylab_frmt = FormatStrFormatter('%.1f')

    #--Format Plot
    self.plot1.set_xlabel(xlab)
    self.plot1.set_ylabel(ylab)
    self.plot1.xaxis.set_major_formatter(xlab_frmt)
    self.plot1.yaxis.set_major_formatter(ylab_frmt)
    if "Strain" in xlab or "Time" in xlab:
        self.plot1.ticklabel_format(style='sci',scilimits=(-6,-3),axis='x')
    if "Strain" in ylab or "Time" in ylab:
        self.plot1.ticklabel_format(style='sci',scilimits=(-6,-3),axis='y')
    self.plot1.legend()
    #--Create the Tkinter canvas
    self.canvas = FigureCanvasTkAgg(self.fig, master = window)
    self.canvas.draw()
    #--Create the Matplotlib toolbar
    self.toolbar = NavigationToolbar2Tk(self.canvas, window)
    self.toolbar.update()
    #--Format Toolbar
    self.toolbar.config(bg='white')
    self.toolbar._message_label.config(background='white')
    self.toolbar.place(
                    anchor = 'n', 
                    relx = self.Placement['PropTable']['Toolbar1'][0], 
                    rely = self.Placement['PropTable']['Toolbar1'][1]
                    )
    #--Add the figure to the GUI
    self.canvas.get_tk_widget().place(
                                    anchor = 'n', 
                                    relx = self.Placement['PropTable']['Figure1'][0], 
                                    rely = self.Placement['PropTable']['Figure1'][1]
                                    )
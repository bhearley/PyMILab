#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   ShearPropertyPlot.py
#
#   PURPOSE: Build the Shear Property Additional Plotting Capability
#    
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ShearPropertyPlot(self, window):
    # Import Modules
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
    from matplotlib.backend_bases import MouseButton
    from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
    import numpy as np

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
    shear_opt = self.prop_plot_opt.get()

    # Option 1 - Stress vs Strain
    if shear_opt == 'Stress vs Strain':
        # -- Unpack stress and strain for convenience
        strain = Raw['Raw Data']['Strain-'+dir]['Value'][0:Analysis['Stages']['End Index']['Value'][0]]
        stress = Raw['Raw Data']['Stress-'+dir]['Value'][0:Analysis['Stages']['End Index']['Value'][0]]

        # -- Plot the raw data
        self.plot1.plot(strain, stress,'k',label='Raw Data')

        # -- Plot the modulus
        strain_lin_end = (stress[-1]-stress[0])/Analysis['Shear Analysis']['Shear Modulus-'+dir]['Value']+strain[0]
        strain_lin = np.linspace(strain[0],strain_lin_end,100)
        stress_lin = stress[0]+Analysis['Shear Analysis']['Shear Modulus-'+dir]['Value']*(strain_lin-strain[0])
        self.plot1.plot(strain_lin,stress_lin,'r--',label='Modulus')

        # -- Plot Proportional Limit
        if Analysis['Shear Analysis']['Shear Proportional Limit-'+dir]['Value'] != None:
            self.plot1.plot(Analysis['Shear Analysis']['Shear Proportional Limit Strain-' + dir]['Value'],Analysis['Shear Analysis']['Shear Proportional Limit-'+dir]['Value'],'ro',label='Proportional Limit')

        # -- Plot Custom Yield Offset
        if 'Yield Offset' in list(self.user_opt.keys()):
            for i in range(len(self.user_opt['Yield Offset'])):
                strain_val = Analysis['Shear Analysis']['Shear Yield-'+dir]['Strain at Yield Strength']['Value'][i],
                stress_val = Analysis['Shear Analysis']['Shear Yield-'+dir]['Yield Strength']['Value'][i]
                self.plot1.plot(strain_val,stress_val,label=str(strain_val) + Raw['Raw Data']['Units']['Strain']['Value'] + ' Offset Yield')

        # -- Plot Ultimate Strength
        if Analysis['Shear Analysis']['Shear Ultimate Strength-' + dir]['Value'] != None:
            self.plot1.plot(Analysis['Shear Analysis']['Shear Strain at UTS-' + dir]['Value'],Analysis['Shear Analysis']['Shear Ultimate Strength-' + dir]['Value'],'mo',label='Ultimate Strength')

        # -- Plot Failure Strength
        if Analysis['Shear Analysis']['Shear Failure Strength-' + dir]['Value'] != None:
            self.plot1.plot(Analysis['Shear Analysis']['Shear Strain at Failure-' + dir]['Value'], Analysis['Shear Analysis']['Shear Failure Strength-' + dir]['Value'],'co',label='Failure Strength')

        # -- Set Formatting
        xlab = 'Strain ' + ' [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']'
        ylab = 'Stress ' + ' [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']'

        xlab_frmt = ScalarFormatter() 
        ylab_frmt = FormatStrFormatter('%.1f')

    # Option 2 - Strain Rate
    elif shear_opt == 'Strain Rate':
        # -- Unpack time and strain for convenience
        time = np.array(Raw['Raw Data']['Time']['Value'][0:Analysis['Stages']['End Index']['Value'][0]])
        strain = np.array(Raw['Raw Data']['Strain-' + dir]['Value'][0:Analysis['Stages']['End Index']['Value'][0]])

        # -- Create the linear fit
        sr_fit = Analysis['Shear Analysis']['Shear Strain Rate-'+dir]['Value']*(time-time[0])-strain[0]

        # -- Plot
        self.plot1.plot(time, strain,'k',label = 'Raw Data')
        self.plot1.plot(time, sr_fit, 'r--', label = 'Strain Rate Fit')

        # -- Set Formatting
        xlab = 'Time ' + ' [' + Raw['Raw Data']['Units']['Time']['Value'] + ']'
        ylab = 'Strain ' + ' [' + Raw['Raw Data']['Units']['Strain']['Value'] + ']'

        xlab_frmt = ScalarFormatter()
        ylab_frmt = ScalarFormatter()

    # Option 3 - Stress Rate
    elif shear_opt == 'Stress Rate':
        # -- Unpack time and strain for convenience
        time = np.array(Raw['Raw Data']['Time']['Value'][0:Analysis['Stages']['End Index']['Value'][0]])
        stress = np.array(Raw['Raw Data']['Stress-' + dir]['Value'][0:Analysis['Stages']['End Index']['Value'][0]])

        # -- Create the linear fit
        sr_fit = Analysis['Shear Analysis']['Shear Stress Rate-'+dir]['Value']*(time-time[0])-stress[0]

        # -- Plot
        self.plot1.plot(time, stress,'k',label = 'Raw Data')
        self.plot1.plot(time, sr_fit, 'r--', label = 'Stress Rate Fit')

        # -- Set Formatting
        xlab = 'Time ' + ' [' + Raw['Raw Data']['Units']['Time']['Value'] + ']'
        ylab = 'Strain ' + ' [' + Raw['Raw Data']['Units']['Stress']['Value'] + ']'

        xlab_frmt = ScalarFormatter()
        ylab_frmt = FormatStrFormatter('%.1f')

    #--Format the plot
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
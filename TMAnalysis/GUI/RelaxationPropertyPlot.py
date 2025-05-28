#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   RelaxationPropertyPlot.py
#
#   PURPOSE: Build the Relaxation Property Additional Plotting Capability
#    
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def RelaxationPropertyPlot(self, window):
    # Import Modules
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
    from matplotlib.backend_bases import MouseButton
    from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
    import numpy as np

    #  Delete the canvas if it exists
    if hasattr(self, 'canvas'):
        self.toolbar.destroy()
        self.canvas.get_tk_widget().destroy()

    # Create Figure
    self.fig = Figure(figsize=(self.Placement['PropTable']['Figure1'][2],self.Placement['PropTable']['Figure1'][3]), dpi = self.Placement['PropTable']['Figure1'][4])
    self.fig.subplots_adjust(left=0.1, right=0.975, top=0.95, bottom=0.15)
    self.plot1 = self.fig.add_subplot(111)

    # Get the option
    relax_opt = self.prop_plot_opt.get()

    # Option 1 - Relaxation Stress vs Strain
    if relax_opt == 'Relaxation Stress vs Strain':
        # -- Unpack stress and strain for convenience
        strain = self.Analysis['Relaxation Analysis']['Relaxation Strain-'+self.dir]['Value']
        stress = self.Analysis['Relaxation Analysis']['Relaxation Stress-'+self.dir]['Value']

        # -- Plot
        self.plot1.plot(strain, stress,'k',label = 'Relaxation Stress vs Strain')

        # -- Set Formatting
        xlab = 'Strain ' + ' [' + self.Raw['Raw Data']['Units']['Strain']['Value'] + ']'
        ylab = 'Stress ' + ' [' + self.Raw['Raw Data']['Units']['Stress']['Value'] + ']'

        xlab_frmt = ScalarFormatter() 
        ylab_frmt = FormatStrFormatter('%.1f')

    # Option 2 - Relaxation Strain vs Time
    elif relax_opt == 'Relaxation Strain vs Time':
        # -- Unpack time and strain for convenience
        time = self.Analysis['Relaxation Analysis']['Relaxation Time']['Value']
        strain = self.Analysis['Relaxation Analysis']['Relaxation Strain-'+self.dir]['Value']
                    
        # -- Plot
        self.plot1.plot(time, strain,'k',label = 'Relaxation Strain vs Time')

        # -- Set Formatting
        xlab = 'Time ' + ' [' + self.Raw['Raw Data']['Units']['Time']['Value']  + ']'
        ylab = 'Strain ' + ' [' + self.Raw['Raw Data']['Units']['Strain']['Value']  + ']'

        xlab_frmt = ScalarFormatter() 
        ylab_frmt = ScalarFormatter() 

    # Option 3 - Relaxation Stress vs Time
    elif relax_opt == 'Relaxation Stress vs Time':
        # -- Unpack time and stress for convenience
        time = self.Analysis['Relaxation Analysis']['Relaxation Time']['Value']
        stress = self.Analysis['Relaxation Analysis']['Relaxation Stress-'+self.dir]['Value']
                    
        # -- Plot
        self.plot1.plot(time, stress,'k',label = 'Relaxation Stress vs Time')

        # -- Set Formatting
        xlab = 'Time ' + ' [' + self.Raw['Raw Data']['Units']['Time']['Value']  + ']'
        ylab = 'Stress ' + ' [' + self.Raw['Raw Data']['Units']['Stress']['Value']  + ']'

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
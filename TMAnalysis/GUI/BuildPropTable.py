#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   BuildPropTable.py
#
#   PURPOSE: Build the Propery table and Property plots.
#    
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#       frmt    GUI formatting
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def Build_Prop_Table(self, window, frmt):  
    # Import Modules
    import tkinter as tk
    import tkinter.font as tkFont
    import tksheet

    # Unpack frmt
    bg_color = frmt[0]
    fontname = frmt[1]           
    fsize_s = frmt[2]
    fsize_l = frmt[3]
    fsize_t = frmt[4]

    # Import Functions
    from TMAnalysis.GUI.PropDisplay import PropDisplay

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
    # -- Delete the 'Get Propertise' button
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

    # Create Properties Option Menu Variable and Pptions
    options = []
    if "Tensile" in self.Analysis['Stages']['Stage Type']['Value'][0]:
        options.append('Tensile Analysis')
    if "Compressive" in self.Analysis['Stages']['Stage Type']['Value'][0]:
        options.append('Compressive Analysis')
    if "Shear" in self.Analysis['Stages']['Stage Type']['Value'][0]:
        options.append('Shear Analysis')
    if len(self.Analysis['Stages']['Stage Type']['Value']) > 1:
        if "Relaxation" in self.Analysis['Stages']['Stage Type']['Value'][1]:
            options.append('Relaxation Analysis')
        if "Creep" in self.Analysis['Stages']['Stage Type']['Value'][1]:
            options.append('Creep Analysis')

    # Set the default value of the variable 
    self.prop_opt = tk.StringVar(window) 
    self.prop_opt.set(options[0]) 
  
    # Create the option menu
    self.prop_opt_menu = tk.OptionMenu(window, self.prop_opt, *options) 
    self.prop_opt_menu.place(anchor = 'w', relx = 0.025, rely = 0.355)
    self.prop_opt_menu.config(font = self.cali12)

    # Create the button to get properties
    self.A2_btn3 = tk.Button(window, text = "Get Properties", command = lambda:PropDisplay(self, window, frmt), 
                            font = self.cali12, bg = 'light blue')
    self.A2_btn3.place(anchor = 'w', relx = 0.25, rely = 0.355)
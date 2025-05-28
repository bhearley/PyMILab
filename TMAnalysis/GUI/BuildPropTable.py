#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   BuildPropTable.py
#
#   PURPOSE: Build the Propery table and Property plots.
#    
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def Build_Prop_Table(self, window):  
    # Import Modules
    import tkinter as tk
    from tkinter import ttk

    # Import Functions
    from GUI.PropDisplay import PropDisplay

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

    # Create the option menu
    self.prop_opt_menu = ttk.Combobox(
                                    window,
                                    values=options,
                                    style="Modern.TCombobox",
                                    state="readonly",
                                    width=self.Placement['PropTable']['Combo1'][2]
                                    )
    self.prop_opt_menu.place(
                        anchor='n', 
                        relx = self.Placement['PropTable']['Combo1'][0], 
                        rely = self.Placement['PropTable']['Combo1'][1]
                        ) 
    self.prop_opt_menu.set(options[0])

    # Create the button to get properties
    self.A2_btn3 = ttk.Button(
                            window, 
                            text = "Get Properties", 
                            command = lambda:PropDisplay(self, window), 
                            style = "Modern1.TButton")
    self.A2_btn3.place(
                    anchor = 'w', 
                    relx = self.Placement['PropTable']['Button1'][0], 
                    rely = self.Placement['PropTable']['Button1'][1]
                    )
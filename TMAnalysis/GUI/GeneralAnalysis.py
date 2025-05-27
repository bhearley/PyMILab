#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   GeneralAnalyis.py
#
#   PURPOSE: Build the General Analysis Page. The General Analysis allows users to select between the stage table subpage and property table subpage. The stage
#            table page is loaded by default 
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#       frmt    format vector
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def GeneralAnalysis(self, window, frmt):
    #Import Modules
    import os
    import numpy as np
    import pandas as pd
    import tkinter as tk
    import tkinter.font as tkFont
    import tksheet

    #Unpack Formatting
    bg_color = frmt[0] 
    fontname = frmt[1]
    fsize_s = frmt[2]
    fsize_l = frmt[3]
    fsize_t = frmt[4]

    #Initialize list of attributes for each page
    self.att_list = {'GeneralAnalysis':[]}

    # Create the Stage Table Button
    self.GA_btn1 = tk.Button(window, text = "Stage Table", command = self.create_stage_table, 
                                font = (fontname, fsize_s), bg = 'light blue')
    self.GA_btn1.place(anchor = 'n', relx = 0.05, rely = 0.225)
    self.att_list['GeneralAnalysis'].append('self.GA_btn1')

    # Create the Properties Table Button
    self.GA_btn2 = tk.Button(window, text = "Test Properties", command = self.create_prop_table, 
                                font = (fontname, fsize_s), bg = 'light blue')
    self.GA_btn2.place(anchor = 'n', relx = 0.15, rely = 0.225)
    self.att_list['GeneralAnalysis'].append('self.GA_btn2')

    # Create the Continue Button
    self.GA_cont = tk.Button(window, text = "Continue", command = self.continue_analysis, 
                                font = (fontname, fsize_s), bg = 'light green')
    self.GA_cont.place(anchor = 'n', relx = 0.9675, rely = 0.94)
    self.att_list['GeneralAnalysis'].append('self.GA_cont')

    # Create the Stage Table Automatically
    self.create_stage_table()
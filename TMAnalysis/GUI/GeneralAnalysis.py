#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   GeneralAnalyis.py
#
#   PURPOSE: Build the General Analysis Page. The General Analysis allows users to select between the stage table subpage and property table subpage. The stage
#            table page is loaded by default 
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def GeneralAnalysis(self, window):
    # Import Modules
    from tkinter import ttk 

    #Initialize list of attributes for each page
    self.att_list = {'GeneralAnalysis':[]}

    # Create the Stage Table Button
    self.GA_btn1 = ttk.Button(
                            window, 
                            text = "Stage Table", 
                            command = self.create_stage_table, 
                            style = 'Modern1.TButton'
                            )
    self.GA_btn1.place(
                    anchor = 'n', 
                    relx = self.Placement['General']['Button1'][0], 
                    rely = self.Placement['General']['Button1'][1]
                    )
    self.att_list['GeneralAnalysis'].append('self.GA_btn1')

    # Create the Properties Table Button
    self.GA_btn2 = ttk.Button(
                            window, 
                            text = "Test Properties", 
                            command = self.create_prop_table, 
                            style = 'Modern1.TButton'
                            )
    self.GA_btn2.place(
                    anchor = 'n', 
                    relx = self.Placement['General']['Button2'][0], 
                    rely = self.Placement['General']['Button2'][1]
                    )
    self.att_list['GeneralAnalysis'].append('self.GA_btn2')

    # Create the Continue Button
    self.GA_cont = ttk.Button(
                            window, 
                            text = "Continue", 
                            command = self.continue_analysis, 
                            style = 'Modern1.TButton'
                            )
    self.GA_cont.place(
                    anchor = 'n', 
                    relx = self.Placement['General']['Button3'][0], 
                    rely = self.Placement['General']['Button3'][1]
                    )
    self.att_list['GeneralAnalysis'].append('self.GA_cont')

    # Create the Stage Table Automatically
    self.create_stage_table()
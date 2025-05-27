#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   FileSelection.py
#
#   PURPOSE: Allow user to select all Raw Data JSON Files to be analyzed
#
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def FileSelection(self,window):
    #Import Modules
    import tkinter as tk
    from tkinter import ttk

    #Initialize list of attributes for each page
    self.att_list = {'FileSelection':[]}

    # Create the frame for the start page
    self.FS_frame1 = tk.Frame(
                            window, 
                            bd=self.Placement['FileSelection']['Frame1'][2], 
                            relief="ridge", 
                            width = self.Placement['FileSelection']['Frame1'][3],
                            height = self.Placement['FileSelection']['Frame1'][4],
                            bg="white"
                            )
    self.FS_frame1.place(
                        anchor = 'c', 
                        relx = self.Placement['FileSelection']['Frame1'][0], 
                        rely = self.Placement['FileSelection']['Frame1'][1]
                        )
    self.att_list['FileSelection'].append('self.FS_frame1')

    # Create the label widget with all options
    self.FS_desc1 = ttk.Label(
                        self.FS_frame1, 
                        text="Select the Raw Data JSON Neutral File(s) for analysis. See the TMAnalysis User Manual for additional information.", 
                        style = "Modern1.TLabel",
                        anchor=tk.CENTER,                       
                        justify=tk.CENTER,                   
                        wraplength=self.Placement['FileSelection']['Desc1'][2]         
                        )
    self.FS_desc1.place(
                        anchor = 'n', 
                        relx = self.Placement['FileSelection']['Desc1'][0], 
                        rely = self.Placement['FileSelection']['Desc1'][1]
                        )
    self.att_list['FileSelection'].append('self.FS_desc1')

    #Create a button to upload the Raw Data JSON Files
    self.FS_btn1 = ttk.Button(
                            self.FS_frame1, 
                            text = "Select Raw Data JSON File(s)", 
                            command = self.get_raw_json,
                            style =  "Modern1.TButton",
                            )
    self.FS_btn1.place(
                        anchor = 'n', 
                        relx = self.Placement['FileSelection']['Button1'][0], 
                        rely = self.Placement['FileSelection']['Button1'][1] 
                        )
    self.att_list['FileSelection'].append('self.FS_btn1')
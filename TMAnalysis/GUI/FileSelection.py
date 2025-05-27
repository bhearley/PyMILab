#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   FileSelection.py
#
#   PURPOSE: Allow user to select all Raw Data JSON Files to be analyzed
#
#   INPUTS:
#       self    structure containing all GUI information
#       window  window
#       frmt    format vector
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def FileSelection(self,window,frmt):
    #Import Modules
    import tkinter as tk

    #Unpack Formatting
    bg_color = frmt[0] 
    fontname = frmt[1]
    fsize_s = frmt[2]

    #Initialize list of attributes for each page
    self.att_list = {'FileSelection':[]}

    # Create a StringVar to associate with the label
    text_var = tk.StringVar()
    text_var.set("Select the Raw Data JSON Neutral File(s) for analysis. See the TMAnalysis User Manual for additional information.")

    # Create the label widget with all options
    self.FS_desc1 = tk.Label(window, 
                     textvariable=text_var, 
                     anchor=tk.CENTER,       
                     bg=bg_color,                  
                     bd=3,              
                     height = 3,
                     font=(fontname, fsize_s),              
                     padx=25,               
                     pady=25,                
                     justify=tk.CENTER,    
                     relief=tk.RAISED,                
                     wraplength=800         
                    )
    self.FS_desc1.place(anchor = 'n', relx = 0.5, rely = 0.25)
    self.att_list['FileSelection'].append('self.FS_desc1')

    #Create a button to upload the Raw Data JSON Files
    self.FS_btn1 = tk.Button(window, text = "Select Raw Data JSON File(s)", command = self.get_raw_json, 
                                font = (fontname, fsize_s), bg = 'light blue')
    self.FS_btn1.place(anchor = 'n', relx = 0.5, rely = 0.5)
    self.att_list['FileSelection'].append('self.FS_btn1')
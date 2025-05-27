#-----------------------------------------------------------------------------------------
#
#   GetStyles.py
#
#   PURPOSE: Set the self.btn_style1s for the GUI
#
#   INPUTS:
#       self    structure containing all GUI information
#-----------------------------------------------------------------------------------------
def GetStyles(self):
    # Import modules
    from tkinter import ttk

    # Initialize Syles
    self.style = ttk.Style()
    self.style.theme_use("alt") 
    self.style_man = {}

    # Buttons
    # -- Blue Large Text
    self.style.configure(
                        "Modern1.TButton",
                        background='#0b3d91',
                        foreground="white",
                        font=("Segoe UI", 18),
                        borderwidth=2,
                        padding=10,
                        focuscolor='',
                        highlightthickness=0
                        )
    self.style.map(
                        "Modern1.TButton",
                        background=[("active", "#428bca")]
                )
    
    # Text
    # -- Label 1
    self.style.configure(
                        "Modern1.TLabel",
                        foreground="black",
                        background="white",
                        font=("Segoe UI", 14),
                        padding=0
                        )
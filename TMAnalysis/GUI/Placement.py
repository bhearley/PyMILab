#-----------------------------------------------------------------------------------------
#
#   Placements.py
#
#   PURPOSE: Get the coordinates and size of each widget based on screen size
#
#   INPUTS:
#       self    structure containing all GUI information
#-----------------------------------------------------------------------------------------
def Placements(self, res):
    # Initialize
    Placement = {'HomePage':{},
                 'FileSelection' :{},
                 }
    
    # 2560 x 1440
    if res == "2560x1440":
        # -- Home Page
        Placement['HomePage']['Title'] = [0.5 ,0.025]
        Placement['HomePage']['Logo'] = [0.999 ,0.06]

        # -- File Selection
        Placement['FileSelection']['Frame1'] = [0.5, 0.5, 3, 600, 400]
        Placement['FileSelection']['Desc1'] = [0.5, 0.25, 500]
        Placement['FileSelection']['Button1'] = [0.5, 0.6]
        
    # 1536 x 960
    if res == "1536x960":
        # -- Home Page
        Placement['HomePage']['Title'] = [0.5 ,0]
        Placement['HomePage']['Logo'] = [0.999 ,0.06]

        # -- FileSelection
        Placement['FileSelection']['Frame1'] = [0.5, 0.5, 3, 500, 300]
        Placement['FileSelection']['Desc1'] = [0.5, 0.25, 400]
        Placement['FileSelection']['Button1'] = [0.5, 0.6]

    else:
        Placements(self, "1536x960")


    # Set to self
    self.Placement = Placement

    return
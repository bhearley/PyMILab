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
                 'UserOptions':{},
                 'General':{},
                 'StageTable':{},
                 'PropTable':{},
                 'Notes':{}
                 }
    
    # 2560 x 1440
    if res == "2560x1440":
        # -- Home Page
        Placement['HomePage']['Title'] = [0.5 ,0.03]
        Placement['HomePage']['Logo'] = [0.999 ,0.06]

        # -- File Selection
        Placement['FileSelection']['Frame1'] = [0.5, 0.5, 3, 600, 400]
        Placement['FileSelection']['Desc1'] = [0.5, 0.25, 500]
        Placement['FileSelection']['Button1'] = [0.5, 0.6]

        # -- User Options
        Placement['UserOptions']['Sheet1'] = [0.5, 0.325, 180, 200, 12]
        Placement['UserOptions']['Check1'] = [0.5, 0.2, 15]
        Placement['UserOptions']['Label1'] = [0.475, 0.275]
        Placement['UserOptions']['Combo1'] = [0.575, 0.275]
        Placement['UserOptions']['Sheet2'] = [0.5, 0.5, 950, 500, 12, 250, 150, 120, 400]
        Placement['UserOptions']['Button1'] = [0.965, 0.955]

        # -- General Analysis
        Placement['General']['Button1'] = [0.055, 0.175]
        Placement['General']['Button2'] = [0.125, 0.175]
        Placement['General']['Button3'] = [0.965, 0.955]

        # -- Stage Table
        Placement['StageTable']['Sheet1'] = [0.175, 0.225, 790, 550, 80, 140, 90, 120, 120, 100, 80]
        Placement['StageTable']['Figure1'] = [0.775, 0.26, 8, 7.2, 125]
        Placement['StageTable']['Toolbar1'] = [0.795, 0.9]
        Placement['StageTable']['Combo1'] = [0.71, 0.191, 10]
        Placement['StageTable']['Combo2'] = [0.8, 0.191, 10]
        Placement['StageTable']['Button1'] = [0.875, 0.175, 6]
        Placement['StageTable']['Label1'] = [0.755, 0.191]
        Placement['StageTable']['Button2'] = [0.20325, 0.175]

        # -- Prop Table
        Placement['PropTable']['Combo1'] = [0.0625, 0.3125, 20]
        Placement['PropTable']['Button1'] = [0.135, 0.325]
        Placement['PropTable']['Sheet1'] = [0.118, 0.4, 480, 500, 280, 80, 80]
        Placement['PropTable']['Combo2'] = [0.725, 0.191]
        Placement['PropTable']['Button2'] = [0.875, 0.175, 10]
        Placement['PropTable']['Figure1'] = [0.75, 0.26, 9, 7.5, 125]
        Placement['PropTable']['Toolbar1'] = [0.775, 0.9]

        # -- Notes
        Placement['Notes']['Label1'] = [0.5, 0.3]
        Placement['Notes']['Text1'] = [0.5, 0.35, 100, 8, 12]
        Placement['Notes']['Button1'] = [0.965, 0.955]
        Placement['Notes']['Button2'] = [0.0325, 0.955]

        
    # 1536 x 960
    if res == "1536x960":
        # -- Home Page
        Placement['HomePage']['Title'] = [0.5 ,0.025]
        Placement['HomePage']['Logo'] = [0.999 ,0.06]

        # -- FileSelection
        Placement['FileSelection']['Frame1'] = [0.5, 0.5, 3, 500, 300]
        Placement['FileSelection']['Desc1'] = [0.5, 0.25, 400]
        Placement['FileSelection']['Button1'] = [0.5, 0.6]

        # -- UserOptions
        Placement['UserOptions']['Sheet1'] = [0.5, 0.325, 155, 175, 12]
        Placement['UserOptions']['Check1'] = [0.5, 0.2, 15]
        Placement['UserOptions']['Label1'] = [0.475, 0.275]
        Placement['UserOptions']['Combo1'] = [0.625, 0.275]
        Placement['UserOptions']['Sheet2'] = [0.5, 0.55, 950, 500, 12, 250, 150, 120, 400]
        Placement['UserOptions']['Button1'] = [0.94375, 0.9325]

        # -- General Analysis
        Placement['General']['Button1'] = [0.058, 0.175]
        Placement['General']['Button2'] = [0.1745, 0.175]
        Placement['General']['Button3'] = [0.94375, 0.9325]

        # -- Stage Table
        Placement['StageTable']['Sheet1'] = [0.26, 0.25, 790, 550, 80, 140, 90, 120, 120, 100, 80]
        Placement['StageTable']['Figure1'] = [0.775, 0.26, 5, 4.25, 125]
        Placement['StageTable']['Toolbar1'] = [0.795, 0.875]
        Placement['StageTable']['Combo1'] = [0.6875, 0.191, 10]
        Placement['StageTable']['Combo2'] = [0.81, 0.191, 10]
        Placement['StageTable']['Button1'] = [0.9, 0.175, 6]
        Placement['StageTable']['Label1'] = [0.75, 0.191]
        Placement['StageTable']['Button2'] = [0.305, 0.175]

        # -- Prop Table
        Placement['PropTable']['Combo1'] = [0.0825, 0.3125, 20]
        Placement['PropTable']['Button1'] = [0.2, 0.325]
        Placement['PropTable']['Sheet1'] = [0.175, 0.4, 480, 500, 280, 80, 80]
        Placement['PropTable']['Combo2'] = [0.725, 0.191]
        Placement['PropTable']['Button2'] = [0.875, 0.175, 6]
        Placement['PropTable']['Figure1'] = [0.75, 0.26, 6, 4.25, 125]
        Placement['PropTable']['Toolbar1'] = [0.775, 0.875]

        # -- Notes
        Placement['Notes']['Label1'] = [0.5, 0.3]
        Placement['Notes']['Text1'] = [0.5, 0.35, 100, 8, 12]
        Placement['Notes']['Button1'] = [0.94375, 0.9325]
        Placement['Notes']['Button2'] = [0.05625, 0.9325]

    else:
        Placements(self, "1536x960")


    # Set to self
    self.Placement = Placement

    return
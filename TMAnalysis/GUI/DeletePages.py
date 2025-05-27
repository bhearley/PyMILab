#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   DeletePages.py
#
#   PURPOSE: Delete a page
#
#   INPUTS:
#       self    structure containing all GUI information
#       page    name of the page td destory
#
#-----------------------------------------------------------------------------------------
def DeletePages(self,page):
    for widget in self.att_list[page]:
        eval(widget).destroy()
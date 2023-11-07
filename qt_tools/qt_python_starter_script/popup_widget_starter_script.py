##########################################################################
#
#               COPY THIS LINE OF CODE BELOW INTO YOUR SCRIPT
#
# This is meant to server as a kicking off point to load up the ui very quickly
# Change certain names in the script to suit your needs:
#     - CLASS_NAME:                       Give it any class name you want
#     - THE_FUNCTION:                     Give a name for the function
#     - PATH TO UI FOLDER:                The full path the leads to the folder that holds the .ui file
#     - NAME OF UI FILE:                  The name of the ui file as it appears
#
#   This will server as a popup window
##########################################################################




import sys
import os

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtUiTools as Ui_Tools

## Path to the ui folder
absolute_path = os.path.dirname(__file__)

class CHANGE_THE_CLASS_NAME(QtWidgets.QWidget):
    def __init__(self,  project=None, parent=None, ):
        super(CHANGE_THE_CLASS_NAME, self).__init__()

        ## Loading the .ui file
        toolset_path = os.path.join("\\PATH TO UI FOLDER")
        ui_path = os.path.join(toolset_path + "\\NAME OF UI FILE.ui")
        self.ui = Ui_Tools.QUiLoader().load(ui_path, parentWidget=self)



def run_popup():
    global app
    app = CHANGE_THE_CLASS_NAME()
    app.show()
 






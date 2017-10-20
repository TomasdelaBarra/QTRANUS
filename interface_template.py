import os
import sys
from PyQt4.Qt import QMessageBox
from PyQt4 import QtGui, uic,QtCore,Qt


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'launch_template.ui'))



class InterfaceTemplateDialog(QtGui.QDialog,FORM_CLASS):

    def __init__(self,parent=None):
        """Constructor."""
        super(InterfaceTemplateDialog, self).__init__(parent)
    
        self.setupUi(self)
        
       
       
        
        self.run_tranus_btn = self.findChild(QtGui.QPushButton,'run_tranus_btn')
        self.spin_box = self.findChild(QtGui.QSpinBox,'spinBox')
        
        #imploc checkboxes 
        self.imploc_1 = self.findChild(QtGui.QCheckBox,'imploc_1') # All information by sector and zone
        self.imploc_2 = self.findChild(QtGui.QCheckBox,'imploc_2') # Total production by sector and zone
        self.imploc_3 = self.findChild(QtGui.QCheckBox,'imploc_3') # Total production by year/policy
        self.imploc_4 = self.findChild(QtGui.QCheckBox,'imploc_4') # Internal information by sector and zone
        self.imploc_5 = self.findChild(QtGui.QCheckBox,'imploc_5') # Consumption coefficients by sector
        self.imploc_6 = self.findChild(QtGui.QCheckBox,'imploc_6') # Total consumption by sector and zone 
        self.imploc_7 = self.findChild(QtGui.QCheckBox,'imploc_7') # all information, comma delimited
        
        #Imptra checkboxes 
        self.imptra_1 = self.findChild(QtGui.QCheckBox,'imptra_1') # Report all links
        self.imptra_2 = self.findChild(QtGui.QCheckBox,'imptra_2') # Report specified link types
        self.imptra_3 = self.findChild(QtGui.QCheckBox,'imptra_3') # Filter links by demand/capacity range
        self.imptra_4 = self.findChild(QtGui.QCheckBox,'imptra_4') # Report specified links
        self.imptra_5 = self.findChild(QtGui.QCheckBox,'imptra_5') # Table of indicators
        self.imptra_6 = self.findChild(QtGui.QCheckBox,'imptra_6') # Cordons (only with IMPTRA.DAT)
        self.imptra_7 = self.findChild(QtGui.QCheckBox,'imptra_7') # Transit Routes profile
        self.imptra_9 = self.findChild(QtGui.QCheckBox,'imptra_9') # Link route and category profile
        self.imptra_10 = self.findChild(QtGui.QCheckBox,'imptra_10') # Route profile in comma delimited format
        self.imptra_11 = self.findChild(QtGui.QCheckBox,'imptra_11') # indicators, comma delimited
        
        
        #Mats checkboxes
        self.mats_1 = self.findChild(QtGui.QCheckBox,'mats_1') # Disut by transport category
        self.mats_2 = self.findChild(QtGui.QCheckBox,'mats_2') # Disut by mode and transport category
        self.mats_3 = self.findChild(QtGui.QCheckBox,'mats_3') # Disut by socio economic sector
        self.mats_4 = self.findChild(QtGui.QCheckBox,'mats_4') # Trips by mode
        self.mats_5 = self.findChild(QtGui.QCheckBox,'mats_5') # Trips by transport category
        self.mats_6 = self.findChild(QtGui.QCheckBox,'mats_6') # Trips by mode and transport category
        self.mats_7 = self.findChild(QtGui.QCheckBox,'mats_7') # Total trips (sum of categories)
        self.mats_8 = self.findChild(QtGui.QCheckBox,'mats_8') # Frequency distribution of trips by mode
        self.mats_9 = self.findChild(QtGui.QCheckBox,'mats_9') # Flows by socio-economic sector
        self.mats_10 = self.findChild(QtGui.QCheckBox,'mats_10') # Flows by transport category
        self.mats_11 = self.findChild(QtGui.QCheckBox,'mats_11') # Costs by transport category
        self.mats_12 = self.findChild(QtGui.QCheckBox,'mats_12') # Costs by socio-economic sector
        self.mats_13 = self.findChild(QtGui.QCheckBox,'mats_13') # Exogenous trips by transport category
        self.mats_14 = self.findChild(QtGui.QCheckBox,'mats_14') # Exogenous trips by category and mode
        
        #Matesp checkboxes
        self.matesp_1 = self.findChild(QtGui.QCheckBox,'matesp_1') # Trips by operator
        self.matesp_3 = self.findChild(QtGui.QCheckBox,'matesp_3') # Matrix of transfers
        self.matesp_4 = self.findChild(QtGui.QCheckBox,'matesp_4') # Matrix of distance
        self.matesp_5 = self.findChild(QtGui.QCheckBox,'matesp_5') # Matrix of time
        self.matesp_6 = self.findChild(QtGui.QCheckBox,'matesp_6') # Matrix of costs
        self.matesp_7 = self.findChild(QtGui.QCheckBox,'matesp_7') # Matrix of transfers between operators
        self.matesp_8 = self.findChild(QtGui.QCheckBox,'matesp_8') # Flows through nodes
        
        #extensions 
        self.imploc_extension = self.findChild(QtGui.QListWidget,'imploc_extension')
        self.imptra_extension = self.findChild(QtGui.QListWidget,'imptra_extension')
        self.mats_extension = self.findChild(QtGui.QListWidget,'mats_extension')
        self.matesp_extension = self.findChild(QtGui.QListWidget,'matesp_extension')
        
            
        self.generate_btn = self.findChild(QtGui.QPushButton,'generate_btn')
        self.check_all_btn = self.findChild(QtGui.QPushButton,'check_all_btn')
        self.console = self.findChild(QtGui.QTextBrowser,'console')
        self.clear_console = self.findChild(QtGui.QPushButton,'clear_console') 
        self.close_btn = self.findChild(QtGui.QDialogButtonBox, 'close_btn')
        
        
    
        
        
       
   
    
       
 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
        
     
        
   
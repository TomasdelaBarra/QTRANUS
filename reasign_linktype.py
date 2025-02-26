# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .classes.data.DataBase import DataBase
#from .classes.libraries.pandas import pandas
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.Helpers import Helpers
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_sector_dialog import AddSectorDialog
#import pandas
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'reasign_linktype.ui'))

class ReasignLintype(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, id_scenario,  parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ReasignLintype, self).__init__(parent)
        self.setupUi(self)
        # Resize Dialog for high resolution monitor
        self.tranus_folder = tranus_folder
        self.id_scenario = id_scenario
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.response_buttons = None
        # Linking objects with controls
        self.cb_linktype = self.findChild(QtWidgets.QComboBox, 'cb_linktype')
        
        #self.scenario_tree.customContextMenuRequested.connect(self.open_menu)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.ok_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close_event)
        
        self.load_data()
        

    def load_data(self):
        link_types = self.dataBaseSqlite.selectAll(' link_type ', where=f" where id_scenario = {self.id_scenario}")
        self.cb_linktype.clear()
        for value in link_types:
            self.cb_linktype.addItem(f"{value[0]} {value[2]}", value[0])


    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def ok_event(self, event):
        self.response_buttons = 1
        self.close()
    
    def close_event(self, event):
        self.response_buttons = 0
        self.close()
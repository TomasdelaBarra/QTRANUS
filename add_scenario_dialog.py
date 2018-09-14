# -*- coding: utf-8 -*-
import os, re, webbrowser
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from .classes.general.QTranusMessageBox import QTranusMessageBox
from string import *
from .classes.data.DataBase import DataBase
from PyQt5.Qt import QDialogButtonBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_scenario.ui'))

class AddScenarioDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddScenarioDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.dataBase = DataBase()
        
        # Linking objects with controls
        self.code = self.findChild(QtWidgets.QLineEdit, 'code')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.previous = self.findChild(QtWidgets.QComboBox, 'cb_previous')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_scenario)
        
        #Loads
        self.__load_scenarios_combobox()
        
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)

    def save_new_scenario(self):
        if(self.code is None or self.code.text().strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's code.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's code.")
            return False
        
        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's name.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's name.")
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's description.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's description.")
            return False
    
        previousCode = ''
        if len(self.previous) > 0:
            if self.previous.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select a previous scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select a previous scenario code.")    
                return False
            else:
                previousCode = (self.previous.currentText().split('-'))[0].strip()               
        
        
        newMatrix = self.dataBase.add_new_scenario(self.parent().parent().scenariosMatrix, self.code.text(), self.name.text(), self.description.text(), previousCode)
        if newMatrix is not None:
            self.parent().parent().scenariosMatrix = newMatrix
            self.parent().load_scenarios()
            self.accept()
        else:
            return False
        
        return True
    
    def __load_scenarios_combobox(self):            
        scenarios_dic = self.dataBase.get_scenarios_list(self.parent().parent().scenariosMatrix)
        if scenarios_dic is not None:
            if len(scenarios_dic) > 0:
                for scenario in scenarios_dic:
                    self.previous.addItem(scenario[0])

            
            
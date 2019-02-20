# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_scenario.ui'))

class AddScenarioDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent = None, codeScenario=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddScenarioDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeScenario = codeScenario
        self.tranus_folder = tranus_folder
        self.dataBase = DataBase()
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder )
        
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
        if self.codeScenario:
            self.__load_default_data()

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)

    def save_new_scenario(self):
        if(self.code is None or self.code.text().strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's code.")
            return False
        
        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's name.")
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's description.")
            return False
    
        previousCode = ''
        if len(self.previous) > 0:
            if self.previous.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select a previous scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select a previous scenario code.")    
                return False
            else:
                previousCode = (self.previous.currentText().split('-'))[0].strip()
                if self.code.text() == previousCode:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select other previous scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    print("Please select other previous scenario code.")    
                    return False
        
        if self.codeScenario is None:
            newMatrix = self.dataBaseSqlite.addScenario(self.code.text(), self.name.text(), self.description.text(), previousCode)
            if not newMatrix:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select other previous scenario code.")    
                return False
        else:
            newMatrix = self.dataBaseSqlite.updateScenario(self.code.text(), self.name.text(), self.description.text(), previousCode)
        #BEFORE FROM FILE  newMatrix = self.dataBase.add_new_scenario(self.parent().parent().scenariosMatrix, self.code.text(), self.name.text(), self.description.text(), previousCode)
        if newMatrix is not None:
        #BEFORE FROM FILE    self.parent().parent().scenariosMatrix = newMatrix
            self.parent().load_scenarios()
            self.accept()
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's description.")
            return False
        return True
    
    """ BEFORE LOAD DATA FROM DATABASE FILE (CSV)
    def __load_scenarios_combobox(self):            
        scenarios_dic = self.dataBase.get_scenarios_list(self.parent().parent().scenariosMatrix)
        if scenarios_dic is not None:
            if len(scenarios_dic) > 0:
                for scenario in scenarios_dic:
                    self.previous.addItem(scenario[0])"""

    def __load_scenarios_combobox(self):            
        scenarios = self.dataBaseSqlite.selectAll('scenario')
        if scenarios is not None:
            if len(scenarios) > 0:
                for scenario in scenarios:
                    self.previous.addItem(scenario[1])

    def __load_default_data(self):
        data = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.codeScenario))     
        self.code.setText(data[0][1])
        self.name.setText(data[0][2])
        self.description.setText(data[0][3])
        indexPrevious = self.previous.findText(data[0][4], Qt.MatchFixedString)
        self.previous.setCurrentIndex(indexPrevious)
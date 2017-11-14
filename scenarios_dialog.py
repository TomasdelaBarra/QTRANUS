# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from PyQt4 import QtGui, uic
from classes.data.DataBase import DataBase
from classes.data.Scenarios import Scenarios
from classes.data.ScenariosModel import ScenariosModel
from classes.general.QTranusMessageBox import QTranusMessageBox
from string import *
from .add_scenario_dialog import AddScenarioDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenarios.ui'))

class ScenariosDialog(QtGui.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ScenariosDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.dataBase = DataBase()
        #self.scenariosMatrix = None
        
        # Linking objects with controls
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtGui.QTreeView, 'scenarios_tree')
        self.scenarioCode = self.findChild(QtGui.QLineEdit, 'code')
        self.scenarioName = self.findChild(QtGui.QLineEdit, 'name')
        self.scenarioDescription = self.findChild(QtGui.QLineEdit, 'description')
        self.previousScenarios = self.findChild(QtGui.QComboBox, 'cb_previous')
        self.remove_btn = self.findChild(QtGui.QPushButton, 'remove')
        self.add_btn = self.findChild(QtGui.QPushButton, 'add')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.remove_btn.clicked.connect(self.remove_scenario)
        self.add_btn.clicked.connect(self.open_add_scenario_window)
        self.scenario_tree.clicked.connect(self.__tree_element_selected)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.ok_button)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.cancel_button)
        
        #Loads
        self.__load_scenarios_from_db_file()
        
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)
    
    def open_add_scenario_window(self):
        """
            @summary: Opens add scenario window
        """
        dialog = AddScenarioDialog(parent = self)
        dialog.show()
        result = dialog.exec_()
        
    def remove_scenario(self):
        if self.scenarioCode.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios", "Please select a scenario to remove.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Please select a scenario to remove.")
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Question, "Remove scenario", "Are you sure you want to remove scenario " + self.scenarioCode.text().strip(), ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            result = messagebox.exec_()
            if result == QtGui.QMessageBox.Yes:
                removeResult, matrixResult = self.dataBase.remove_scenario_from_file(self.parent().scenariosMatrix, self.scenarioCode.text().strip())
                if(removeResult):
                    self.parent().scenariosMatrix = matrixResult 
                    self.__get_scenarios_data()
                    self.scenarioCode.setText('')
                    self.scenarioName.setText('')
                    self.scenarioDescription.setText('')
            
        
    def __load_scenarios_from_db_file(self):
        if(self.project.db_path is None or self.project.db_path.strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios", "DB File was not found.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("DB File was not found.")
        else:
            if(self.dataBase.extract_scenarios_file_from_zip(self.project.db_path, self.project['tranus_folder'])):
                self.__get_scenarios_data()
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios", "Scenarios file could not be extracted.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                messagebox.exec_()
                print("Scenarios file could not be extracted.")
                
    def __get_scenarios_data(self):
        if self.parent().scenariosMatrix is not None:
            if self.parent().scenariosMatrix.size > 0:
                #self.scenariosMatrix = self.dataBase.get_scenarios_array(self.project['tranus_folder']) 
                self.scenarios = Scenarios()
                self.scenarios.load_data(self.parent().scenariosMatrix)
                
                self.__load_previous_scenarios_combobox()
                
                scenariosModel = ScenariosModel(self)
                self.scenario_tree.setModel(scenariosModel)
                self.scenario_tree.setExpanded(scenariosModel.indexFromItem(scenariosModel.root_item), True)
    
    def load_scenarios(self):
        self.__get_scenarios_data()
    
    def __load_previous_scenarios_combobox(self):
        if self.parent().scenariosMatrix is not None:
            if self.parent().scenariosMatrix.size > 0:
                previousScenariosMatrix = np.unique(self.parent().scenariosMatrix[['PreviousScenarioCode']])
                previousScenariosMatrix.sort(order='PreviousScenarioCode')
                self.previousScenarios.clear()
                for item in np.nditer(previousScenariosMatrix):
                    self.previousScenarios.addItem(item.item(0)[0])
        

    def __tree_element_selected(self, index):
        selectedItemText = index.model().itemFromIndex(index).text()
        if selectedItemText.strip() != '':
            scenarioData = self.parent().scenariosMatrix[(self.parent().scenariosMatrix['ScenarioCode'] == selectedItemText.split()[0])]
            if scenarioData is not None:
                if scenarioData.size > 0:
                    self.scenarioCode.setText(scenarioData.item(0)[0])
                    self.scenarioName.setText(scenarioData.item(0)[2])
                    self.scenarioDescription.setText(scenarioData.item(0)[3])
                    self.previousScenarios.setCurrentIndex(self.previousScenarios.findText(scenarioData.item(0)[1]))
                print(scenarioData)
            
    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def closeEvent(self, event):
        self.__rollback_changes()
        print('Closed')
        
    def __rollback_changes(self):
        self.parent().scenariosMatrix = self.parent().scenariosMatrixBackUp
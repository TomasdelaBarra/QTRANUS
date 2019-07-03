# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from string import *
from .add_scenario_dialog import AddScenarioDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenarios.ui'))

class ScenariosDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ScenariosDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBase = DataBase()
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenarioCode = self.findChild(QtWidgets.QLineEdit, 'code')
        self.scenarioName = self.findChild(QtWidgets.QLineEdit, 'name')
        self.scenarioDescription = self.findChild(QtWidgets.QLineEdit, 'description')
        self.previousScenarios = self.findChild(QtWidgets.QComboBox, 'cb_previous')
        self.add_btn = self.findChild(QtWidgets.QPushButton, 'add')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_btn.clicked.connect(self.open_add_scenario_window)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.customContextMenuRequested.connect(self.open_menu)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)

        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()

        #Add Icons
        self.add_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def open_menu(self, position):
        menu = QMenu()

        indexes = self.scenario_tree.selectedIndexes()
        codeScenarioSelected = indexes[0].model().itemFromIndex(indexes[0]).text().split(" - ")[0]

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Scenario')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Scenario')
        copy = menu.addAction(QIcon(self.plugin_dir+"/icons/copy-scenario.svg"),'Copy Scenario Changes')
        paste = menu.addAction(QIcon(self.plugin_dir+"/icons/paste-scenario.svg"),'Paste Scenario Changes')
        if self.copyScenarioSelected:
            paste.setEnabled(True)
        else:
            paste.setEnabled(False)

        opt = menu.exec_(self.scenario_tree.viewport().mapToGlobal(position))

        if opt == edit:
            dialog = AddScenarioDialog(self.tranus_folder, parent = self, codeScenario=codeScenarioSelected)
            dialog.show()
            result = dialog.exec_()
        if opt == copy:
            paste.setEnabled(True)
            self.copy_scenario(codeScenario=codeScenarioSelected)
        if opt == paste:
            paste.setEnabled(True)
            self.paste_scenario(codeScenario=codeScenarioSelected)
            self.__get_scenarios_data()
        if opt == remove:
            self.remove_scenario(codeScenario=codeScenarioSelected)
            self.__get_scenarios_data()


    def open_add_scenario_window(self):
        """
            @summary: Opens add scenario window
        """
        dialog = AddScenarioDialog(self.tranus_folder,  parent = self)
        dialog.show()
        result = dialog.exec_()
        

    def remove_scenario(self, codeScenario=None):
        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Question, "Remove scenario", "Are you sure you want to remove scenario {}?".format(codeScenario), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        result = messagebox.exec_()
        if result == QtWidgets.QMessageBox.Yes:
            removeResult = self.dataBaseSqlite.removeScenario(codeScenario)
            if removeResult:
                return True
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios", "Error while trying to eliminate scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
    
    def copy_scenario(self, codeScenario=None):
        self.copyScenarioSelected = codeScenario

    def paste_scenario(self, codeScenario=None):
        self.copyScenarioSelected
        data = self.dataBaseSqlite.selectAll('scenario', "where code = '{}'".format(self.copyScenarioSelected))
        
        #result = DataBaseSqlite().addScenario(data[0][1], data[0][2], data[0][3], codeScenario)
        #if result:
        return True
    
    def __load_scenarios_from_db_file(self):
        if(self.project.db_path is None or self.project.db_path.strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios", "DB File was not found.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("DB File was not found.")
        else:
            if(self.dataBase.extract_scenarios_file_from_zip(self.project.db_path, self.project['tranus_folder'])):
                self.__get_scenarios_data()
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios", "Scenarios file could not be extracted.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Scenarios file could not be extracted.")
                
    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
    
    def load_scenarios(self):
        self.__get_scenarios_data()
    
    def __load_previous_scenarios_combobox(self):
        if self.parent().scenariosMatrix is not None:
            if self.parent().scenariosMatrix.size > 0:
                previousScenariosMatrix = np.unique(self.parent().scenariosMatrix[['ScenarioCode']])
                previousScenariosMatrix.sort(order='ScenarioCode')
                self.previousScenarios.clear()
                for item in np.nditer(previousScenariosMatrix):
                    self.previousScenarios.addItem(item.item(0)[0])
        
            
    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def close_event(self, event):
        self.parent().load_scenarios()
        self.__rollback_changes()
        
    def __rollback_changes(self):
        self.parent().scenariosMatrix = self.parent().scenariosMatrixBackUp
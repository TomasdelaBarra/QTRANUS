# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *
from .classes.libraries.tabulate import tabulate

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_mode_dialog import AddModeDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'modes.ui'))

class ModesDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ModesDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioCode = scenarioCode
        self.idScenario = None
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.modes_tree = self.findChild(QtWidgets.QTreeView, 'modes_tree')
        self.lb_total_items_modes = self.findChild(QtWidgets.QLabel, 'total_items_modes')
        self.modes_tree.setRootIsDecorated(False)
        self.add_mode_btn = self.findChild(QtWidgets.QPushButton, 'add_mode_btn')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_mode_btn.clicked.connect(self.open_add_mode_window)
        self.modes_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.modes_tree.customContextMenuRequested.connect(self.open_menu_modes)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        
        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__get_modes_data()

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_mode_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)



    def open_menu_modes(self, position):
        menu = QMenu()

        indexes = self.modes_tree.selectedIndexes()
        modeSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Mode')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Mode')

        opt = menu.exec_(self.modes_tree.viewport().mapToGlobal(position))

        if opt == edit:
            dialog = AddModeDialog(self.tranus_folder, parent = self, codeMode=modeSelected)
            dialog.show()
            result = dialog.exec_()
            self.__get_modes_data()
        if opt == remove:
            validation, categories, operators, exogenous_trips = self.dataBaseSqlite.validateRemoveMode(modeSelected)
            
            if validation == False:
                categories = tabulate(categories, headers=["Scenario Code", "Category"]) if categories else ''
                operators = tabulate(operators, headers=["Scenario Code", "Operator"])  if operators else ''
                exogenous_trips = tabulate(exogenous_trips, headers=["Scenario Code", "Zone Origin", "Zone Dest.", "Trip"])  if exogenous_trips else ''
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Modes", "Cannot delete Element? \n Please check details.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok, detailedText=f"Dependents Elements \n {categories} \n {operators} \n {exogenous_trips}")
                messagebox.exec_()

            else:
                self.dataBaseSqlite.removeMode(modeSelected)
                self.__get_modes_data()
            


    def open_add_mode_window(self):
        """
            @summary: Opens add scenario window
        """    
        dialog = AddModeDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__get_modes_data()
        

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
              

    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()


    def __get_modes_data(self):
        result = self.dataBaseSqlite.selectAll('mode', columns=' id, name, description', orderby=' order by 1 ')

        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Description'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,3):
                model.setData(model.index(x, y), result[x][z])
                z+=1

        self.modes_tree.setModel(model)
        self.modes_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)

        self.lb_total_items_modes.setText("%s Items" % len(result))


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
# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .classes.libraries.tabulate import tabulate
from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_operator_dialog import AddOperatorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'operators.ui'))

class OperatorsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(OperatorsDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.idScenario = None
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
        self.lb_total_items_operators = self.findChild(QtWidgets.QLabel, 'total_items_operators')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.operators_tree = self.findChild(QtWidgets.QTreeView, 'operators_tree')
        self.operators_tree.setRootIsDecorated(False)
        self.add_operator_btn = self.findChild(QtWidgets.QPushButton, 'add_operator_btn')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_operator_btn.clicked.connect(self.open_add_operator_window)
        self.operators_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.operators_tree.customContextMenuRequested.connect(self.open_menu_modes)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        
        #Loads
        self.__get_scenarios_data()
        self.__get_operators_data()

        if self.scenarioCode:
            self.__find_scenario_data(self.scenarioCode)

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_operator_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        

    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__get_operators_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)



    def open_menu_modes(self, position):
        menu = QMenu()

        indexes = self.operators_tree.selectedIndexes()
        operatorSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Operator')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Operator')

        opt = menu.exec_(self.operators_tree.viewport().mapToGlobal(position))

        if opt == edit:
            if not self.idScenario:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            else:
                dialog = AddOperatorDialog(self.tranus_folder, parent = self, idScenario=self.idScenario, codeOperator=operatorSelected)
                dialog.show()
                result = dialog.exec_()
                self.__get_operators_data()
        if opt == remove:
            scenarios = [str(value[0]) for value in scenarios]
            scenarios = ','.join(scenarios)
            validation, transfers, routes, link_types = self.dataBaseSqlite.validateRemoveOperator(operatorSelected, scenarios)
             
            if validation == False:
                routes = tabulate(routes, headers=["Scenario Code", "Route"]) if routes else ''
                transfers = tabulate(transfers, headers=["Scenario Code", "Origin Operator", "Destination Operator","Cost"])  if transfers else ''
                link_types = tabulate(link_types, headers=["Scenario Code", "Link Type"])  if link_types else ''
                
                buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel
                message_txt = "Do you really want to delete the items?"
                if routes:
                    buttons = QtWidgets.QMessageBox.Cancel
                    message_txt = "There are dependent routes, you can't delete operator"
                
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Modes", f"{message_txt} \n Please check details.", ":/plugins/QTranus/icon.png", self, buttons = buttons, detailedText=f"Dependents Elements \n {routes} \n\n {transfers} \n\n {link_types}")

                result = messagebox.exec_()
                if result == QtWidgets.QMessageBox.Yes:
                    self.dataBaseSqlite.removeOperator(operatorSelected)
                    self.__get_operators_data()
            else:
                self.dataBaseSqlite.removeOperator(operatorSelected)
                self.__get_operators_data()
            


    def open_add_operator_window(self):
        """
            @summary: Opens add scenario window
        """
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            dialog = AddOperatorDialog(self.tranus_folder,  idScenario=self.idScenario, parent = self)
            dialog.show()
            result = dialog.exec_()
            self.__get_operators_data()
        

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
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        itemsList = self.scenarios_model.findItems(self.scenarioCode, Qt.MatchContains | Qt.MatchRecursive, 0)
        indexSelected = self.scenarios_model.indexFromItem(itemsList[0])
        modelSelection.setCurrentIndex(indexSelected, QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)
        
        self.select_scenario(self.scenario_tree.selectedIndexes()[0])


    def __get_operators_data(self):
        
        qry = """select a.id, a.name, a.description 
                 from operator a
                 where a.id_scenario = %s""" % (self.idScenario)
        result = self.dataBaseSqlite.executeSql(qry)
        
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Description'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,3):
                model.setData(model.index(x, y), result[x][z])
                z+=1
        self.operators_tree.setModel(model)
        self.operators_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)

        self.lb_total_items_operators.setText(" %s Items" % len(result))


    def load_scenarios(self):
        self.__get_scenarios_data()


    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]

    
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
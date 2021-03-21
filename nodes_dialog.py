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
from .add_node_dialog import AddNodeDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'nodes.ui'))

class NodesDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode, scenarioSelectedIndex=None, parent = None, nodeShapeFields=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(NodesDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.copyAdministratorSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioSelectedIndex = scenarioSelectedIndex
        self.node_shape_fields = nodeShapeFields if nodeShapeFields else None
        self.scenarioCode = scenarioCode
        self.idScenario = None
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], resolution_dict['height'])
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.nodes_tree = self.findChild(QtWidgets.QTreeView, 'node_tree')
        self.nodes_tree.setRootIsDecorated(False)
        self.lb_total_items_nodes = self.findChild(QtWidgets.QLabel, 'total_items_nodes')
        self.add_node_btn = self.findChild(QtWidgets.QPushButton, 'add_node_btn')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_node_btn.clicked.connect(self.open_add_node_window)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.nodes_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.nodes_tree.customContextMenuRequested.connect(self.open_menu_nodes)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        
        
        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__get_nodes_data()

        # Set scenarioIndex
        if self.scenarioCode:
            self.__find_scenario_data(self.scenarioCode)

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_node_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))

        
    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__get_nodes_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)



    def open_menu_nodes(self, position):
        menu = QMenu()

        indexes = self.nodes_tree.selectedIndexes()
        nodeSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Node')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Node')

        opt = menu.exec_(self.nodes_tree.viewport().mapToGlobal(position))

        if opt == edit:
            if not self.idScenario:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            else:
                dialog = AddNodeDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeNode=nodeSelected, nodeShapeFields=self.node_shape_fields)
                dialog.show()
                result = dialog.exec_()
                self.__get_nodes_data()
        if opt == remove:
            scenarios = [str(value[0]) for value in scenarios]
            scenarios = ','.join(scenarios)
            validation, links = self.dataBaseSqlite.validateRemoveNodes(nodeSelected, scenarios)
             
            if validation == False:
                links = tabulate(links, headers=["Scenario Code", "Link"])  if links else ''
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Modes", "Can not remove elements? \n Please check details.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok, detailedText=f"Dependents Elements \n {links}")
                messagebox.exec_()
            else:
                scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
                self.dataBaseSqlite.removeNode(scenarios, nodeSelected)
                self.__get_nodes_data()
            


    def open_add_node_window(self):
        """
            @summary: Opens add scenario window
        """
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            dialog = AddNodeDialog(self.tranus_folder, idScenario=self.idScenario,  parent = self, nodeShapeFields=self.node_shape_fields)
            dialog.show()
            result = dialog.exec_()
            self.__get_nodes_data()
        

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
               

    def __get_nodes_data(self):
        
        qry = """select id, name, 
                 case WHEN id_type = 1 then 'Internal' 
                      WHEN id_type = 2 then 'External'
                      WHEN id_type = 3 or  id_type = 0 then 'Node'  end type    
                 from node  
                 where id_scenario = %s
                 order by 1 asc """ % (self.idScenario)
        result = self.dataBaseSqlite.executeSql(qry)
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Type'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,3):
                model.setData(model.index(x, y), result[x][z])
                z+=1
        self.nodes_tree.setModel(model)
        self.nodes_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)

        self.lb_total_items_nodes.setText(" %s Items" % len(result))


    def load_scenarios(self):
        self.__get_scenarios_data()
    

    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]
        
            
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
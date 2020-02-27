# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser, numpy as np

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
from .add_category_dialog import AddCategoryDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'categories.ui'))

class CategoriesDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(CategoriesDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], resolution_dict['height'])
        self.scenarioCode = scenarioCode
        self.idScenario = None

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.categories_tree = self.findChild(QtWidgets.QTreeView, 'categories_tree')
        self.lb_total_items_categories = self.findChild(QtWidgets.QLabel, 'total_items_categories')
        self.categories_tree.setRootIsDecorated(False)
        self.add_category_btn = self.findChild(QtWidgets.QPushButton, 'add_category')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_category_btn.clicked.connect(self.open_add_category_window)
        self.categories_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.categories_tree.customContextMenuRequested.connect(self.open_menu_categories)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        
        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__get_categories_data()

        if self.scenarioCode:
            self.__find_scenario_data(self.scenarioCode)

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_category_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
    
    

    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__get_categories_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def open_menu_categories(self, position):
        menu = QMenu()
        
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        indexes = self.categories_tree.selectedIndexes()
        categorySelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Category')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Category')
        
        opt = menu.exec_(self.categories_tree.viewport().mapToGlobal(position))
    
        if opt == edit:
            dialog = AddCategoryDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeCategory=categorySelected)
            dialog.show()
            result = dialog.exec_()
            self.__get_categories_data()
        if opt == remove:
            scenarios = [str(value[0]) for value in scenarios]
            scenarios = ','.join(scenarios)
            validation, operators, exogenous_trips = self.dataBaseSqlite.validateRemoveCategory(categorySelected, scenarios)
             
            if validation == False:
                operators = tabulate(operators, headers=["Scenario Code", "Operator"]) if operators else ''
                exogenous_trips = tabulate(exogenous_trips, headers=["Scenario Code", "Origin", "Destination","Trip"])  if exogenous_trips else ''
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Modes", "Can not remove elements? \n Please check details.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok, detailedText=f"Dependents Elements \n {operators} \n {exogenous_trips}")   
                messagebox.exec_()
            else:
                self.dataBaseSqlite.removeCategory(scenarios, categorySelected)
                self.__get_categories_data()
            


    def open_add_category_window(self):
        """
            @summary: Opens add scenario window
        """
        dialog = AddCategoryDialog(self.tranus_folder, self.idScenario,  parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__get_categories_data()
              

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


    def __get_categories_data(self):

        sql = f"""select a.id, a.name, a.description
                from category a 
                where id_scenario = {self.idScenario}"""
                
        result = self.dataBaseSqlite.executeSql(sql)

        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Description'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,3):
                model.setData(model.index(x, y), result[x][z])
                z+=1
        self.categories_tree.setModel(model)
        self.categories_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)

        self.lb_total_items_categories.setText("%s Items " % len(result))


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
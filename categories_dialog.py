# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

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
    
    def __init__(self, tranus_folder, parent = None):
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

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.categories_tree = self.findChild(QtWidgets.QTreeView, 'categories_tree')
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

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_category_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def open_menu_categories(self, position):
        menu = QMenu()

        indexes = self.categories_tree.selectedIndexes()
        categorySelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Category')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Category')
        
        opt = menu.exec_(self.categories_tree.viewport().mapToGlobal(position))
    
        if opt == edit:
            dialog = AddCategoryDialog(self.tranus_folder, parent = self, codeCategory=categorySelected)
            dialog.show()
            result = dialog.exec_()
            self.__get_categories_data()
        if opt == remove:
            self.dataBaseSqlite.removeCategory(categorySelected)
            self.__get_categories_data()
            


    def open_add_category_window(self):
        """
            @summary: Opens add scenario window
        """
        dialog = AddCategoryDialog(self.tranus_folder,  parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__get_categories_data()
              

    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()


    def __get_categories_data(self):
        sql = """select a.id, a.name, a.description, a.volumen_travel_time, 
                a.value_of_waiting_time, a.min_trip_gener, a.max_trip_gener, a.elasticity_trip_gener, a.choice_elasticity, b.name
                from category a
                join mode b on (a.id_mode = b.id)"""
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
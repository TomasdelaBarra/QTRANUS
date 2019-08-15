# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

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

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_routes_links.ui'))

class AddRoutesLinksDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, id_operators_arr, idScenario=None, scenarioSelectedIndex=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddRoutesLinksDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.id_operators_arr = id_operators_arr
        self.copyAdministratorSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioSelectedIndex = scenarioSelectedIndex
        self.idScenario = idScenario
        resolution_dict = Helpers.screenResolution(30)
        self.resize(resolution_dict['width'], resolution_dict['height'])
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.routes_tree = self.findChild(QtWidgets.QTreeView, 'routes_tree')
        self.routes_tree.setRootIsDecorated(False)
        self.routes_tree.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.lb_total_items_routes = self.findChild(QtWidgets.QLabel, 'total_items_routes')
        self.ic_bus_stop = QIcon(self.plugin_dir+"/icons/bus-stop.png")
        self.ic_bus = QIcon(self.plugin_dir+"/icons/bus-icon.png")

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.routes_tree.clicked.connect(self.select_routes)
       
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)
        #self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.save_event)

        self.__get_routes_data()

        
    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__get_links_data()


    def select_routes(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        route = selectedIndex.model().itemFromIndex(selectedIndex).text()
        


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)
    

    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]

    def __get_routes_data(self):
        """
            @summary: Find and Set data of the scenario Selected
        """
        ids_operators = ','.join(self.id_operators_arr)
        ids_routes_selected = ''
        criteria = ''
        if self.parent().id_routes_arr_selected:
            ids_routes_selected = ','.join(self.parent().id_routes_arr_selected)
            criteria = """ and a.id not in (%s)""" % ids_routes_selected

        qry = """select a.id||' '||a.name route
                from 
                route a
                join operator b 
                on (a.id_operator = b.id)
                where id_operator in (%s) %s order by 1""" % (ids_operators, criteria)

        result = self.dataBaseSqlite.executeSql(qry)
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Routes'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,1):
                model.setData(model.index(x, y), result[x][z])
                z+=1
        self.routes_tree.setModel(model)
        self.routes_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)
        self.lb_total_items_routes.setText("%s Items" % len(result))

            
    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def close_event(self, event):
        self.close()


    def save_event(self, event):
        routes_selected = self.routes_tree.selectedIndexes()
        for values in routes_selected:
            self.parent().id_routes_arr_selected.append(values.model().itemFromIndex(values).text().split(" ")[0])
            
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Routes'])
        x=0
        for values in routes_selected:
            item = QtGui.QStandardItem()
            item.setIcon(self.ic_bus_stop)
            item.setText(values.model().itemFromIndex(values).text())
            item.setData('passes_stops',Qt.UserRole)
            #model.setData(model.index(x,0), 'Tipo')
            model.setItem(x,item)
            #model.appendRow(item)
            x+=1

        self.parent().tree_routes.setModel(model)
        self.parent().tree_routes.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)
        self.close()
        
        
    def __rollback_changes(self):
        self.parent().scenariosMatrix = self.parent().scenariosMatrixBackUp
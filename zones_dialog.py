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
from .add_zone_dialog import AddZoneDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zones.ui'))

class ZonesDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ZonesDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.zones_tree = self.findChild(QtWidgets.QTreeView, 'zones_tree')
        self.zones_tree.setRootIsDecorated(False)
        self.add_zone_btn = self.findChild(QtWidgets.QPushButton, 'add_zone_btn')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_zone_btn.clicked.connect(self.open_add_zone_window)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.zones_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.zones_tree.customContextMenuRequested.connect(self.open_menu_zones)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        
        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__get_zones_data()

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_zone_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)



    def open_menu_zones(self, position):
        menu = QMenu()

        indexes = self.zones_tree.selectedIndexes()
        zoneSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Zones')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Zones')

        opt = menu.exec_(self.zones_tree.viewport().mapToGlobal(position))

        if opt == edit:
            dialog = AddZoneDialog(self.tranus_folder, parent = self, codeZone=zoneSelected)
            dialog.show()
            result = dialog.exec_()
            self.__get_zones_data()
        if opt == remove:
            self.dataBaseSqlite.removeZone(zoneSelected)
            self.__get_zones_data()
            


    def open_add_zone_window(self):
        """
            @summary: Opens add scenario window
        """
        dialog = AddZoneDialog(self.tranus_folder,  parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__get_zones_data()
        

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


    def __get_zones_data(self):
        result = self.dataBaseSqlite.selectAll(' zone ', where=" where id != 0 ", orderby=" order by id asc")
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,2):
                model.setData(model.index(x, y), result[x][z])
                z+=1
        self.zones_tree.setModel(model)
        self.zones_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)


    def load_scenarios(self):
        self.__get_scenarios_data()
        
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
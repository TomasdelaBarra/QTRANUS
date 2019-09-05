# -*- coding: utf-8 -*-
import os, re, webbrowser, csv, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from qgis.gui import *


from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'imports_network.ui'))

class ImportsNetworkDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode, scenarioSelectedIndex=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ImportsNetworkDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.copyAdministratorSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioSelectedIndex = scenarioSelectedIndex
        self.scenarioCode = scenarioCode
        self.idScenario = None
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], 350)
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.btn_nodes = self.findChild(QtWidgets.QRadioButton, 'btn_nodes')
        self.btn_links = self.findChild(QtWidgets.QRadioButton, 'btn_links')
        self.btn_routes = self.findChild(QtWidgets.QRadioButton, 'btn_routes')
        self.btn_opers = self.findChild(QtWidgets.QRadioButton, 'btn_opers')
        self.btn_turns = self.findChild(QtWidgets.QRadioButton, 'btn_turns')
        self.import_file_obj = self.findChild(QgsFileWidget, 'import_file_obj')
        self.import_file_obj.setFilter(("*.csv;*.nodes;*.links;*.opers;*.turns"))
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.progress_bar = self.findChild(QtWidgets.QProgressBar, 'pg_progress')
        self.lbl_progress = self.findChild(QtWidgets.QLabel, 'lbl_progresbar')

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)
        self.progress_bar.setVisible(False)
        self.lbl_progress.setVisible(False)
                
        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        #self.__get_administrators_data()

        
    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        #self.__get_administrators_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def __get_scenarios_data(self):

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)
        
        self.select_scenario(self.scenario_tree.selectedIndexes()[0])
               
    

    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]
        
        
    def save_event(self, event):
        if self.btn_nodes.isChecked():
            self.__load_csv_nodes(self.import_file_obj.filePath())
        elif self.btn_links.isChecked():
            self.__load_csv_links(self.import_file_obj.filePath())
        elif self.btn_routes.isChecked():
            self.__load_csv_routes(self.import_file_obj.filePath())
        elif self.btn_opers.isChecked():
            self.__load_csv_opers(self.import_file_obj.filePath())
        elif self.btn_turns.isChecked():
            self.__load_csv_turns(self.import_file_obj.filePath())
        #self.close()

    def close_event(self, event):
        # wprint("dentro close")
        self.dataBaseSqlite.insertLoteTest()

        self.close()

    def __load_csv_routes(self, path):
        return True

    def __load_csv_opers(self, path):
        scenario_code = self.scenarioCode
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            data_list = []
            try:
                for index, row in enumerate(csv_reader):
                    if index > 1:
                        _id = row[0].strip()
                        name = row[1].strip() 
                        description = row[2].strip() 
                        id_operator = row[3].strip()
                        frequency_from = row[4].strip()
                        frequency_to = row[5].strip()
                        target_occ = row[6].strip()
                        max_fleet = row[7].strip()
                        follows_schedule = row[8].strip()
                        data_list.append((_id, name, description, id_operator, frequency_from, frequency_to, target_occ, max_fleet, follows_schedule))   
                self.dataBaseSqlite.addFFileRoute(scenarios, data_list)
            except:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            finally:
                self.close() 
                return True
                

    def __load_csv_turns(self, path):
        return True

    def __load_csv_nodes(self, path):
        scenario_code = self.scenarioCode
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            data_list = []
            try:
                for index, row in enumerate(csv_reader):
                    if index > 1:
                        _id = row[0].strip()
                        x = float(row[1].strip())
                        y = float(row[2].strip())
                        id_type = int(row[3].strip()) if int(row[3].strip()) == 1 or int(row[3].strip()) == 2 else 0
                        name = row[4].strip() if row[4].strip() else None
                        description = row[5].strip() if row[5].strip() else None
                        data_list.append((_id, x, y, id_type, name, description))
                self.dataBaseSqlite.addFFileNode(scenarios, data_list)
            except:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            finally:
                self.close()   
                return True

    def __load_csv_links(self, path):
        scenario_code = self.scenarioCode
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
        if len(scenarios) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return True
            self.close() 
        with open(path) as csv_file_read:
            rows_file_read = csv.reader(csv_file_read, delimiter=',')
            tot_rows = len(list(rows_file_read))

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            step = 100/tot_rows
            counter = 0
            data_list = []
            try:
                for index, row in enumerate(csv_reader):
                    if index > 0 and int(row[4].strip()) != 0:
                        linkid = f"{row[1].strip()}-{row[2].strip()}"
                        node_from = row[1].strip() 
                        node_to = row[2].strip() 
                        id_linktype = row[4].strip() 
                        length = row[5].strip() if row[5].strip() else None
                        capacity = row[6].strip() if row[6].strip() else None
                        name = row[7].strip() if row[7].strip() else None 
                        description = row[8].strip() if row[8].strip() else None
                        data_list.append((linkid, node_from, node_to, id_linktype, length, capacity, name, description))
                self.dataBaseSqlite.addFFileLink(scenarios, data_list)
            except:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            finally:
                self.close()
                return True                 
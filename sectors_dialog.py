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
from .add_sector_dialog import AddSectorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sectors.ui'))

class SectorsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(SectorsDialog, self).__init__(parent)
        self.setupUi(self)
        resolution_dict = Helpers.screenResolution(60)
        self.resize(int(resolution_dict['width']), int(resolution_dict['height']))

        self.project = parent.project
        #self.scenarioSelectedIndex = scenarioSelectedIndex
        self.scenarioCode = scenarioCode
        self.idScenario = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)


        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.sectors_tree = self.findChild(QtWidgets.QTreeView, 'sectors_tree')
        self.sectors_tree.setRootIsDecorated(False)
        self.add_sector_btn = self.findChild(QtWidgets.QPushButton, 'add_sector')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        self.lb_total_items = self.findChild(QtWidgets.QLabel, 'total_items')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_sector_btn.clicked.connect(self.open_add_sector_window)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.sectors_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sectors_tree.customContextMenuRequested.connect(self.open_menu_sectors)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)

        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__get_sectors_data()

        #Add Iconss
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_sector_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def open_menu_sectors(self, position):
        menu = QMenu()

        indexes = self.sectors_tree.selectedIndexes()
        sectorSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Sector')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Sector')
        """copy = menu.addAction(QIcon(self.plugin_dir+"/icons/copy-scenario.svg"),'Copy Sector')
        paste = menu.addAction(QIcon(self.plugin_dir+"/icons/paste-scenario.svg"),'Paste Sector')"""

        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        opt = menu.exec_(self.sectors_tree.viewport().mapToGlobal(position))

        if opt == edit:
            dialog = AddSectorDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeSector=sectorSelected)
            dialog.show()
            result = dialog.exec_()
        if opt == remove:
            scenarios = [str(value[0]) for value in scenarios]
            scenarios = ','.join(scenarios)
            validation, sectors, zonal_data = self.dataBaseSqlite.validateRemoveSector(sectorSelected, scenarios)
             
            if validation == False:
                sectors = tabulate(sectors, headers=["Scenario Code", "Sector"])  if sectors else ''
                zonal_data = tabulate(zonal_data, headers=["Scenario Code", "Sector"])  if zonal_data else ''
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Modes", "Can not remove elements? \n Please check details.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok, detailedText=f"Dependents Elements \n Sectors \n {sectors} \n Zonal Data \n {zonal_data}")
                messagebox.exec_()
            else:
                self.dataBaseSqlite.removeSector(sectorSelected)
                self.__get_sectors_data()
            


    def open_add_sector_window(self):
        """
            @summary: Opens add scenario window
        """
        dialog = AddSectorDialog(self.tranus_folder,  idScenario=self.idScenario, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__get_sectors_data()
        

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
    

    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__get_sectors_data()


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
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        itemsList = self.scenarios_model.findItems(self.scenarioCode, Qt.MatchContains | Qt.MatchRecursive, 0)
        indexSelected = self.scenarios_model.indexFromItem(itemsList[0])
        modelSelection.setCurrentIndex(indexSelected, QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)
        
        self.select_scenario(self.scenario_tree.selectedIndexes()[0])
        


    def __get_sectors_data(self):
        result = self.dataBaseSqlite.selectAll('sector', where=f" where id_scenario = {self.idScenario} ",columns=' id, name, description ', orderby='order by 1 asc')
        
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Description'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z=0
            for y in range(0,3):
                model.setData(model.index(x, y), result[x][z])
                z+=1
        self.sectors_tree.setModel(model)
        self.sectors_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)
        self.lb_total_items.setText("%s Items" % len(result))

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
# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .classes.data.DataBase import DataBase
#from .classes.libraries.pandas import pandas
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.Helpers import Helpers
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_sector_dialog import AddSectorDialog
#import pandas
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'transfers.ui'))

class TransfersDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(TransfersDialog, self).__init__(parent)
        self.setupUi(self)
        # Resize Dialog for high resolution monitor
        resolution_dict = Helpers.screenResolution(70)
        self.resize(resolution_dict['width'], resolution_dict['height'])


        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioCode = scenarioCode
        self.idScenario = None
        self.operators = []
        self.header = ['Origin Operator','Destination Operator', 'Tariff']

        self.doubleValidator = self.validateDouble()

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.add_tariff = self.findChild(QtWidgets.QPushButton, 'add_tariff')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.transfers_table = self.findChild(QtWidgets.QTableWidget, 'transfers_table')
        self.cb_operator_origin = self.findChild(QtWidgets.QComboBox, 'cb_operator_origin')
        self.cb_operator_destination = self.findChild(QtWidgets.QComboBox, 'cb_operator_destination')
        self.tariff = self.findChild(QtWidgets.QLineEdit, 'tariff')
        

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_tariff.clicked.connect(self.save_tariff)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)
        self.add_tariff.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        # Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__load_operators_cb_data()
        self.__load_operators_tb_data()

        # Set scenarioIndex
        if self.scenarioCode:
            self.__find_scenario_data(self.scenarioCode)

        self.tariff.setValidator(self.doubleValidator)
        #self.transfers_table.itemChanged.connect(self.__update_operators)
        
    
    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__load_operators_tb_data()
        

    def validateDouble(self):

        objValidatorRange = QtGui.QDoubleValidator(self)
        objValidatorRange.setRange(-10.0, 100.0, 5)
        return objValidatorRange

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)   


    def save_event(self):
        rowsCount = self.transfers_table.rowCount()
        id_scenario = self.idScenario

        for index in range(0, rowsCount):
            id_origin = self.transfers_table.item(index, 0).text().split(" ")[0]
            id_destination = self.transfers_table.item(index, 1).text().split(" ")[0]
            cost = self.transfers_table.item(index, 2).text()
            self.dataBaseSqlite.updateTransferOperator(id_scenario, id_origin, id_destination, cost)
        
        self.close()

    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()


    def __load_operators_cb_data(self):        
        result = self.dataBaseSqlite.selectAll( ' operator ', columns='id, name', orderby=' order by 1 asc')

        for value in result:
            self.cb_operator_origin.addItem(str(value[0])+" "+str(value[1]), value[0])
            self.cb_operator_destination.addItem(str(value[0])+" "+str(value[1]), value[0]) 

    
    def __load_operators_tb_data(self):

        if self.idScenario:
            qry = """
                select 
                b.id||' '||b.name operator_from, c.id||' '||c.name operator_to, a.cost
                from 
                transfer_operator_cost a
                join operator b on a.id_operator_from = b.id
                join operator c on a.id_operator_to = c.id
                where id_scenario = %s order by 1,2 asc""" % self.idScenario

            result = self.dataBaseSqlite.executeSql(qry)
            self.transfers_table.setRowCount(len(result))
            self.transfers_table.setColumnCount(3)
            self.transfers_table.setHorizontalHeaderLabels(self.header)
            self.transfers_table.horizontalHeader().setStretchLastSection(True)

            header = self.transfers_table.horizontalHeader()       
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

            for indice,valor in enumerate(result):
                x = 0
                for z in range(0,len(valor)):
                    data = result[indice][z] if result[indice][z] is not None else ''
                    self.transfers_table.setItem(indice, x, QTableWidgetItem(str(data)))
                    x+=1


    def save_tariff(self):
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            if self.tariff.text() != None and self.tariff.text() != '':
                id_scenario = self.idScenario
                scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
                scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

                id_from = self.cb_operator_origin.itemData(self.cb_operator_origin.currentIndex())
                id_to = self.cb_operator_destination.itemData(self.cb_operator_destination.currentIndex())
                tariff = self.tariff.text()
                

                qry = """select * from transfer_operator_cost
                where id_operator_from={} and id_operator_to={}""".format(id_from, id_to)
                
                result = self.dataBaseSqlite.executeSql(qry)
                if result:
                    self.tariff.setText('')
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add", "Duplicate values ​​are not allowed.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                else:
                    self.dataBaseSqlite.addTransferOperator(scenarios, id_from, id_to, tariff)
                    self.__load_operators_tb_data()
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Transfers", "Please Select one value", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()


    def load_scenarios(self):
        self.__get_scenarios_data()

    
    def __find_scenario_data(self, scenarioSelectedIndex):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]


    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def close_event(self, event):
        self.close()
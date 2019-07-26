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
from .add_mode_dialog import AddModeDialog
from .add_category_dialog import AddCategoryDialog
from .classes.general.Validators import validatorRegex

#import pandas
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'exogenous_trips.ui'))

class ExogeousTripsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """

        super(ExogeousTripsDialog, self).__init__(parent)
        self.setupUi(self)
        # Resize Dialog for high resolution monitor
        resolution_dict = Helpers.screenResolution(80)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioCode = scenarioCode
        self.idScenario = None

        doubleValidator = self.validateDouble()

        self.zones = []
        self.header_trips = ['Origin Zone','Destination Zone', 'Trips']
        self.header_factor = ['Origin Zone','Destination Zone', 'Factor']
        

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.add_trip = self.findChild(QtWidgets.QPushButton, 'add_trip')
        self.add_factor = self.findChild(QtWidgets.QPushButton, 'add_factor')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.lb_total_items_exotrips = self.findChild(QtWidgets.QLabel, 'total_items_exotrips')
        self.trips_tbl = self.findChild(QtWidgets.QTableWidget, 'trips_tbl')
        self.factor_tbl = self.findChild(QtWidgets.QTableWidget, 'factor_tbl')
        self.cb_category = self.findChild(QtWidgets.QComboBox, 'cb_category')
        self.cb_mode = self.findChild(QtWidgets.QComboBox, 'cb_mode')
        self.cb_tr_zone_origin = self.findChild(QtWidgets.QComboBox, 'cb_tr_zone_origin')
        self.cb_tr_zone_destination = self.findChild(QtWidgets.QComboBox, 'cb_tr_zone_destination')
        self.cb_fc_zone_origin = self.findChild(QtWidgets.QComboBox, 'cb_fc_zone_origin')
        self.cb_fc_zone_destination = self.findChild(QtWidgets.QComboBox, 'cb_fc_zone_destination')
        self.le_trip = self.findChild(QtWidgets.QLineEdit, 'le_trip')
        self.le_factor = self.findChild(QtWidgets.QLineEdit, 'le_factor')
        self.btn_category = self.findChild(QtWidgets.QPushButton, 'btn_category')
        self.btn_mode = self.findChild(QtWidgets.QPushButton, 'btn_mode')

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_trip.clicked.connect(self.save_trip)
        self.add_factor.clicked.connect(self.save_factor)
        self.btn_category.clicked.connect(self.open_category)
        self.btn_mode.clicked.connect(self.open_mode)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)
        
        self.le_trip.setValidator(doubleValidator)
        self.le_factor.setValidator(doubleValidator)

        self.add_trip.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        self.add_factor.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        self.btn_category.setIcon(QIcon(self.plugin_dir+"/icons/category.jpg"))
        self.btn_mode.setIcon(QIcon(self.plugin_dir+"/icons/bus-icon.png"))
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        
        # Set scenarioIndex
        if self.scenarioCode:
            self.__find_scenario_data(self.scenarioCode)
        
        self.__load_zones_cb_data()
        self.__load_category_data()
        self.__load_mode_data()
        self.__get_scenarios_data()
        self.__load_zones_tb_data()

        self.cb_category.currentIndexChanged[int].connect(self.category_changed)
        self.cb_mode.currentIndexChanged[int].connect(self.mode_changed)
        self.trips_tbl.itemChanged.connect(self.__validate_trips)
        self.factor_tbl.itemChanged.connect(self.__validate_factor)
    

    def __validate_trips(self, item):
        if item.text()!=None and item.text()!='' and item.column() > 1:
            column = item.column()
            item_value = item.text()
            row = item.row()
            result = validatorRegex(item_value, 'real')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.trips_tbl.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))


    def __validate_factor(self, item):
        if item.text()!=None and item.text()!='' and item.column() > 1:
            column = item.column()
            item_value = item.text()
            row = item.row()
            result = validatorRegex(item_value, 'real')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.factor_tbl.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__load_zones_tb_data()


    def validateDouble(self):

        objValidatorRange = QtGui.QDoubleValidator(self)
        objValidatorRange.setRange(-10.0, 100.0, 5)
        return objValidatorRange

    def category_changed(self):
        self.__load_zones_tb_data()

    def mode_changed(self):
        self.__load_zones_tb_data()


    def save_event(self):
        id_category = self.cb_category.itemData(self.cb_category.currentIndex())
        id_mode = self.cb_mode.itemData(self.cb_mode.currentIndex())
        id_scenario = self.idScenario
        rowsTrips = self.trips_tbl.rowCount()
        rowsfactor = self.factor_tbl.rowCount()

        for index in range(0,rowsTrips):
            id_origin = self.trips_tbl.item(index, 0).text().split(" ")[0]
            id_destination = self.trips_tbl.item(index, 1).text().split(" ")[0]
            tariff = self.trips_tbl.item(index, 2).text()
            self.dataBaseSqlite.updateExogenousData(id_scenario, id_origin, id_destination, id_mode, id_category,  'trip', tariff)
        
        for index in range(0,rowsfactor):
            id_origin = self.factor_tbl.item(index, 0).text().split(" ")[0]
            id_destination = self.factor_tbl.item(index, 1).text().split(" ")[0]
            factor = self.factor_tbl.item(index, 2).text()
            self.dataBaseSqlite.updateExogenousData(id_scenario, id_origin, id_destination, id_mode, id_category,  'factor', factor)

        self.close()
  

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)  


    def open_category(self):
        """
            @summary: Opens QTranus users help
        """
        categorySelected = self.cb_category.itemData(self.cb_category.currentIndex())
        dialog = AddCategoryDialog(self.tranus_folder, parent = self, codeCategory=categorySelected)
        dialog.show()
        result = dialog.exec_()

    def open_mode(self):
        """
            @summary: Opens QTranus users help
        """
        modeSelected = self.cb_mode.itemData(self.cb_mode.currentIndex())
        dialog = AddModeDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeMode=modeSelected)
        dialog.show()
        result = dialog.exec_() 

    def __get_scenarios_data(self):
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)
        
        self.select_scenario(self.scenario_tree.selectedIndexes()[0])

        """self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()"""


    def __load_zones_tb_data(self):
        id_category = self.cb_category.itemData(self.cb_category.currentIndex())
        id_mode = self.cb_mode.itemData(self.cb_mode.currentIndex())
        id_scenario = self.idScenario
        if id_scenario:
            qry = """
                select b.id||' '||b.name zone_from, 
                c.id|| ' ' ||c.name zone_to, trip
                from exogenous_trips a
                join zone b on a.id_zone_from = b.id
                join zone c on a.id_zone_to = c.id
                where a.id_scenario = {} and a.id_mode = {} and a.id_category = {} and trip is not null""".format(id_scenario, id_mode, id_category)

            qry_b = """
                select b.id||' '||b.name zone_from, 
                c.id|| ' ' ||c.name zone_to, factor
                from exogenous_trips a
                join zone b on a.id_zone_from = b.id
                join zone c on a.id_zone_to = c.id
                where  a.id_scenario = {} and a.id_mode = {} and a.id_category = {} and factor is not null""".format(id_scenario, id_mode, id_category)

            result = self.dataBaseSqlite.executeSql(qry)
            result_b = self.dataBaseSqlite.executeSql(qry_b)
            self.trips_tbl.setRowCount(len(result))
            self.trips_tbl.setColumnCount(3)
            self.trips_tbl.setHorizontalHeaderLabels(self.header_trips)
            self.trips_tbl.horizontalHeader().setStretchLastSection(True)

            self.factor_tbl.setRowCount(len(result_b))
            self.factor_tbl.setColumnCount(3)
            self.factor_tbl.setHorizontalHeaderLabels(self.header_factor)
            self.factor_tbl.horizontalHeader().setStretchLastSection(True)
            #self.trips_tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            for indice,valor in enumerate(result):
                x = 0
                for z in range(0,len(valor)):
                    data = result[indice][z] if result[indice][z] is not None else ''
                    self.trips_tbl.setItem(indice, x, QTableWidgetItem(str(data)))
                    x+=1

            for indice,valor in enumerate(result_b):
                x = 0
                for z in range(0,len(valor)):
                    data = result_b[indice][z] if result_b[indice][z] is not None else ''
                    self.factor_tbl.setItem(indice, x, QTableWidgetItem(str(data)))
                    x+=1

            self.lb_total_items_exotrips.setText(" %s Items " % len(result))

        

    def save_trip(self):
        id_from = self.cb_tr_zone_origin.itemData(self.cb_tr_zone_origin.currentIndex())
        id_to = self.cb_tr_zone_destination.itemData(self.cb_tr_zone_destination.currentIndex())
        id_category = self.cb_category.itemData(self.cb_category.currentIndex())
        id_mode = self.cb_mode.itemData(self.cb_mode.currentIndex())
        trips = self.le_trip.text()
        id_scenario = self.idScenario

        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

            qry = """select * from exogenous_trips
            where id_scenario ={} and id_zone_from={} and id_zone_to={} 
            and id_mode={} and id_category={}  and trip is not null""".format(id_scenario, id_from, id_to, id_mode, id_category)
            
            qry_b = """select * from exogenous_trips
            where id_scenario ={} and id_zone_from={} and id_zone_to={} 
            and id_mode={} and id_category={} """.format(id_scenario, id_from, id_to, id_mode, id_category)
            
            result = self.dataBaseSqlite.executeSql(qry)
            result_b = self.dataBaseSqlite.executeSql(qry_b)
            if result:
                self.le_trip.setText('')
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add", "Duplicate values ​​are not allowed.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            else:
                if result_b:
                    self.dataBaseSqlite.updateExogenousData(scenarios, id_from, id_to, id_mode, id_category, 'trip', trips)
                else:
                    self.dataBaseSqlite.addExogenousData(scenarios, id_from, id_to, id_mode, id_category, 'trip', trips)
                self.__load_zones_tb_data()
    

    def save_factor(self):
        id_from = self.cb_fc_zone_origin.itemData(self.cb_fc_zone_origin.currentIndex())
        id_to = self.cb_fc_zone_destination.itemData(self.cb_fc_zone_destination.currentIndex())
        id_category = self.cb_category.itemData(self.cb_category.currentIndex())
        id_mode = self.cb_mode.itemData(self.cb_mode.currentIndex())
        factor = self.le_factor.text()
        id_scenario = self.idScenario

        if not self.idScenario:
            messagebox.exec_()
        else:
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

            qry = """select * from exogenous_trips
            where id_scenario ={} and id_zone_from={} and id_zone_to={} 
            and id_mode={} and id_category={}  and factor is not null""".format(id_scenario, id_from, id_to, id_category, id_mode)
            
            qry_b = """select * from exogenous_trips
            where id_scenario ={} and id_zone_from={} and id_zone_to={} 
            and id_mode={} and id_category={} """.format(id_scenario, id_from, id_to, id_category, id_mode)
            
            result = self.dataBaseSqlite.executeSql(qry)
            result_b = self.dataBaseSqlite.executeSql(qry_b)
            if result:
                self.le_trip.setText('')
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add", "Duplicate values ​​are not allowed.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            else:
                if result_b:
                    self.dataBaseSqlite.updateExogenousData(id_scenario, id_from, id_to, id_category, id_mode, 'factor', factor)
                else:
                    self.dataBaseSqlite.addExogenousData(scenarios, id_from, id_to, id_category, id_mode, 'factor', factor)
                self.__load_zones_tb_data()
        
    
    def __load_category_data(self):
        
        result = self.dataBaseSqlite.selectAll( ' category ', orderby=' order by 1 asc')
        for value in result:
            self.cb_category.addItem("%s %s" % (value[0],value[2]),str(value[0]))


    def __load_mode_data(self):
        result = self.dataBaseSqlite.selectAll( ' mode ', orderby=' order by 1 asc')
        for value in result:
            self.cb_mode.addItem("%s %s" % (value[0],value[1]),str(value[0]))


    def __load_zones_cb_data(self):
        result = self.dataBaseSqlite.selectAll( 'zone ', ' where id > 0 ',orderby=' order by 1 asc')

        for value in result:
            self.cb_tr_zone_origin.addItem(str(value[0])+" "+str(value[1]), value[0])
            self.cb_tr_zone_destination.addItem(str(value[0])+" "+str(value[1]), value[0])
            self.cb_fc_zone_origin.addItem(str(value[0])+" "+str(value[1]), value[0])
            self.cb_fc_zone_destination.addItem(str(value[0])+" "+str(value[1]), value[0])


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
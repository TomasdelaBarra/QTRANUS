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
from .classes.general.Helpers import Helpers
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_sector_dialog import AddSectorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'intersectors.ui'))

class IntersectorsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder,  scenarioCode=None, parent=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(IntersectorsDialog, self).__init__(parent)
        self.setupUi(self)
        self.model = QtGui.QStandardItemModel()
        self.modelTrans = QtGui.QStandardItemModel()
        self.header = ['Input Sector','Min. Demand','Max. Demand', 'Elasticity','Substitutes', 'Exog. Prod. Attractors', 'Ind. Prod. Attractors']
        self.columnIntersectorsDb = ["id_input_sector","min_demand","max_demand","elasticity","substitute","exog_prod_attractors","ind_prod_attractors"]
        self.headerTrans = ['Category','Type','Time Factor', 'Volume Factor','Flow to Product', 'Flow to Consumer']
        self.columnIntersectorsTransDb = ["id_category","type","time_factor","volume_factor","flow_to_product","flow_to_consumer"]
        self.scenarioCode = scenarioCode
        self.idScenario = None

        # Resize Dialog for high resolution monitor
        resolution_dict = Helpers.screenResolution(70)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.intersectors_table = self.findChild(QtWidgets.QTableWidget, 'intersectors_table')
        self.intersectors_table_trans = self.findChild(QtWidgets.QTableWidget, 'intersectors_table_trans')
        self.cb_sector = self.findChild(QtWidgets.QComboBox, 'cb_sector')
        self.sustitute = self.findChild(QtWidgets.QLabel, 'sustitute')
        self.btn_sector_detail = self.findChild(QtWidgets.QPushButton, 'btn_sector_detail')

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.btn_sector_detail.clicked.connect(self.open_sector_detail)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)

        # Set scenarioIndex
        #if self.scenarioSelectedIndex:
        #    self.__find_scenario_data(self.scenarioSelectedIndex)

        
        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__load_sector_cb_data()
        self.__load_intersector_data()

        #Conections to signals
        self.cb_sector.currentIndexChanged[int].connect(self.sector_changed)
        #self.model.itemChanged.connect(self.__update_intersectors_sector_input)
        #self.modelTrans.itemChanged.connect(self.__update_intersectors_trans)
        
    


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__load_intersector_data()
        

    def save_event(self):
        
        id_scenario = self.idScenario
        rowsInputs = self.intersectors_table.rowCount()
        rowsTrans = self.intersectors_table_trans.rowCount()
        
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            id_sector = self.cb_sector.itemData(self.cb_sector.currentIndex()) 
            
            for index in range(0,rowsInputs):
                id_input_sector = self.intersectors_table.item(index, 0).text().split(" ")[0]
                min_demand = self.intersectors_table.item(index, 1).text()
                max_demand = self.intersectors_table.item(index, 2).text()
                elasticity = self.intersectors_table.item(index, 3).text()
                substitute = self.intersectors_table.item(index, 4).text()
                exog_prod_attractors = self.intersectors_table.item(index, 5).text()
                ind_prod_attractors = self.intersectors_table.item(index, 6).text()
                self.dataBaseSqlite.addIntersectorSectorInput(scenarios, id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors )
            
            for index in range(0,rowsTrans):
                id_category = self.intersectors_table_trans.item(index, 0).text().split(" ")[0]
                _type = self.intersectors_table_trans.item(index, 1).text()
                time_factor = self.intersectors_table_trans.item(index, 2).text()
                volume_factor = self.intersectors_table_trans.item(index, 3).text()
                flow_to_product = self.intersectors_table_trans.item(index, 4).text()
                flow_to_consumer = self.intersectors_table_trans.item(index, 5).text()
                self.dataBaseSqlite.addIntersectorTrans(scenarios, id_sector, id_category, _type, time_factor, volume_factor, flow_to_product, flow_to_consumer)
            

        self.close()


    def __find_scenario_data(self, scenarioSelectedIndex):
        """
            @summary: Find and Set data of the scenario Selected
        """
        codeScenario = self.scenarioSelectedIndex.data().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(codeScenario))
        self.idScenario = scenarioData[0][0]
        

    def sector_changed(self):
        sector = self.cb_sector.currentText()
        results = self.dataBaseSqlite.selectAll('sector', " where name = '{}'".format(sector))
        self.sustitute.setText(str(results[0][7]))
        self.__load_intersector_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)  


    def open_sector_detail(self):
        """
            @summary: Open sector detail Dialog
        """
        sectorSelected = self.cb_sector.currentText()
        result = self.dataBaseSqlite.selectAll('sector', " where name = '{}'".format(sectorSelected))
        dialog = AddSectorDialog(self.tranus_folder, parent=self, codeSector=result[0][0])
        dialog.show()
        result = dialog.exec_()  


    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()


    def __load_sector_cb_data(self):
        sectors = self.dataBaseSqlite.selectAll('sector')
        for value in sectors:
            self.cb_sector.addItem(value[1], value[0])

    def __load_intersector_data(self):
        sectorId = self.cb_sector.itemData(self.cb_sector.currentIndex())
        
        print("sectorId", sectorId)
        results = self.dataBaseSqlite.selectAll(' sector ', " where id = %s" % sectorId)
        self.sustitute.setText(str(results[0][7]))
        
        if self.idScenario:
            # Default data of the table
            sql = """select a.id||" "||a.name sector, b.min_demand, max_demand, elasticity, b.substitute, exog_prod_attractors, ind_prod_attractors 
                  from sector a left join inter_sector_inputs b on (a.id = b.id_input_sector) where id_scenario = %s and id_sector = %s""" % (self.idScenario, sectorId)

            sqlB = """select a.id||" "||a.name category, b.type, time_factor, volume_factor, flow_to_product, b.flow_to_consumer 
                    from category a left join inter_sector_transport_cat b on (a.id = b.id_category) where id_scenario = %s and id_sector = %s""" % (self.idScenario, sectorId)

            resultA = self.dataBaseSqlite.executeSql(sql)
            resultB = self.dataBaseSqlite.executeSql(sqlB)
            
            if len(resultA)==0:
                sql = """select a.id||" "||a.name sector, '' min_demand, '' max_demand, '' elasticity, '' substitute, '' exog_prod_attractors, '' ind_prod_attractors 
                  from sector a"""
                resultA = self.dataBaseSqlite.executeSql(sql)

            if len(resultB)==0:
                sql = """select a.id||" "||a.name category, '' type, '' time_factor, '' volume_factor, '' flow_to_product, '' flow_to_consumer 
                    from category a """ 
                resultB = self.dataBaseSqlite.executeSql(sql)

            self.intersectors_table.setRowCount(len(resultA))
            self.intersectors_table.setColumnCount(7)
            self.intersectors_table.setHorizontalHeaderLabels(self.header)
            self.intersectors_table.horizontalHeader().setStretchLastSection(True)
            
            self.intersectors_table_trans.setRowCount(len(resultB))
            self.intersectors_table_trans.setColumnCount(6)
            self.intersectors_table_trans.setHorizontalHeaderLabels(self.headerTrans)
            self.intersectors_table_trans.horizontalHeader().setStretchLastSection(True)

            for indice,valor in enumerate(resultA):
                x = 0
                for z in range(0,7):
                    data = resultA[indice][z] if resultA[indice][z] is not None else ''
                    self.intersectors_table.setItem(indice, x, QTableWidgetItem(str(data)))
                    x+=1

            for indice,valor in enumerate(resultB):
                x = 0
                for z in range(0,6):
                    data = resultB[indice][z] if resultB[indice][z] is not None else ''
                    self.intersectors_table_trans.setItem(indice, x, QTableWidgetItem(str(data)))
                    x+=1

            header_a = self.intersectors_table.horizontalHeader()       
            header_a.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            header_a.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            header_a.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
            #header_a.setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)

            header_b = self.intersectors_table_trans.horizontalHeader()       
            header_b.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            header_b.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            header_b.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            

    def load_scenarios(self):
        self.__get_scenarios_data()


    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def close_event(self, event):
        self.close()
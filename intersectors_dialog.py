# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

from PyQt5.QtGui import *
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import QApplication, QClipboard
from PyQt5 import QtCore, QtGui


from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.Helpers import Helpers
from .classes.general.Validators import validatorRegex
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
        # Resize Dialog for high resolution monitor
        resolution_dict = Helpers.screenResolution(85)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        self.model = QtGui.QStandardItemModel()
        self.modelTrans = QtGui.QStandardItemModel()
        self.shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.header = ['Min. Demand','Max. Demand', 'Elasticity','Substitutes', 'Exog. Prod. Attractors', 'Ind. Prod. Attractors']
        self.columnIntersectorsDb = ["id_input_sector","min_demand","max_demand","elasticity","substitute","exog_prod_attractors","ind_prod_attractors"]
        self.headerTrans = ['Type','Time Factor', 'Volume Factor','Flow to Product', 'Flow to Consumer']
        self.columnIntersectorsTransDb = ["id_category","type","time_factor","volume_factor","flow_to_product","flow_to_consumer"]
        self.scenarioCode = scenarioCode
        self.idScenario = None
        self.table_type = None

        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.lb_total_items_input = self.findChild(QtWidgets.QLabel, 'total_items_input')
        self.lb_total_items_trans = self.findChild(QtWidgets.QLabel, 'total_items_trans')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.intersectors_table = self.findChild(QtWidgets.QTableWidget, 'intersectors_table')
        self.intersectors_table_trans = self.findChild(QtWidgets.QTableWidget, 'intersectors_table_trans')
        self.cb_sector = self.findChild(QtWidgets.QComboBox, 'cb_sector')
        self.sustitute = self.findChild(QtWidgets.QLabel, 'sustitute')
        self.btn_sector_detail = self.findChild(QtWidgets.QPushButton, 'btn_sector_detail')
        
        # Control Actions
        self.shortcut.activated.connect(self.paste_event)
        self.help.clicked.connect(self.open_help)
        self.btn_sector_detail.clicked.connect(self.open_sector_detail)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)
        self.intersectors_table.cellClicked.connect(self.set_row_colum_inputs)
        self.intersectors_table_trans.cellClicked.connect(self.set_row_colum_trans)

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
        self.intersectors_table.itemChanged.connect(self.__validate_intersectors_sector_input)
        self.intersectors_table_trans.itemChanged.connect(self.__validate_update_intersectors_trans)
        self.scenario_tree.clicked.connect(self.select_scenario)
        

    def __validate_intersectors_sector_input(self, item):
        
        if item.text()!=None and item.text()!='':
            column = item.column()
            item_value = item.text()
            row = item.row()

            result = validatorRegex(item_value, 'real')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Intersectors", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.intersectors_table.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))


    def __validate_update_intersectors_trans(self, item):
        
        if item.text()!=None and item.text()!='':
            column = item.column()
            item_value = item.text()
            row = item.row()

            result = validatorRegex(item_value, 'real')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.intersectors_table_trans.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))


            

    def set_row_colum_inputs(self, row, column):
        self._row = row
        self._column = column
        self.table_type = 'inputs'


    def set_row_colum_trans(self, row, column):
        self._row = row
        self._column = column
        self.table_type = 'trans'


    # For Paste Text to Table
    def paste_event(self):
        text = QApplication.clipboard().text()
        rows = text.split('\n')
        row = self._row
        column = self._column
        for rowIndex, cells in enumerate(rows):
            cells = cells.split('\t')
            for cellIndex, cell in enumerate(cells):
                if self.table_type == 'inputs':
                    self.intersectors_table.setItem(rowIndex+row, cellIndex+column, QTableWidgetItem(str(cell)))
                if self.table_type == 'trans':
                    self.intersectors_table_trans.setItem(rowIndex+row, cellIndex+column, QTableWidgetItem(str(cell)))
                

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
            
            inputs_arr = []
            for index in range(0,rowsInputs):
                id_input_sector = self.intersectors_table.verticalHeaderItem(index).text().split(" ")[0]
                min_demand = self.intersectors_table.item(index, 0).text()
                max_demand = self.intersectors_table.item(index, 1).text()
                elasticity = self.intersectors_table.item(index, 2).text()
                substitute = self.intersectors_table.item(index, 3).text()
                exog_prod_attractors = self.intersectors_table.item(index, 4).text()
                ind_prod_attractors = self.intersectors_table.item(index, 5).text()
                inputs_arr.append((id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors ))
            #self.dataBaseSqlite.addIntersectorSectorInput(scenarios, id_sector, id_input_sector, min_demand, max_demand, elasticity, substitute, exog_prod_attractors, ind_prod_attractors )
            self.dataBaseSqlite.addIntersectorSectorInputTestInsertUpdate(scenarios, inputs_arr)
            
            trans_arr = []
            for index in range(0,rowsTrans):
                #print("asd")
                id_category = self.intersectors_table_trans.verticalHeaderItem(index).text().split(" ")[0]
                _type = self.intersectors_table_trans.item(index, 0).text()
                time_factor = self.intersectors_table_trans.item(index, 1).text()
                volume_factor = self.intersectors_table_trans.item(index, 2).text()
                flow_to_product = self.intersectors_table_trans.item(index, 3).text()
                flow_to_consumer = self.intersectors_table_trans.item(index, 4).text()
                trans_arr.append((id_sector, id_category, _type, time_factor, volume_factor, flow_to_product, flow_to_consumer))
            #self.dataBaseSqlite.addIntersectorTrans(scenarios, id_sector, id_category, _type, time_factor, volume_factor, flow_to_product, flow_to_consumer)
            self.dataBaseSqlite.addIntersectorTransInsertUpdate(scenarios, trans_arr)
            
        self.close()


    def __find_scenario_data(self, scenarioSelectedIndex):
        """
            @summary: Find and Set data of the scenario Selected
        """
        codeScenario = self.scenarioSelectedIndex.data().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(codeScenario))
        self.idScenario = scenarioData[0][0]
        

    def sector_changed(self):
        sector = self.cb_sector.itemData(self.cb_sector.currentIndex())
        results = self.dataBaseSqlite.selectAll('sector', " where id = {} and id_scenario = {} ".format(sector, self.idScenario))
        self.sustitute.setText(str(results[0][8]))
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
        sectorSelected = sectorSelected.split(" ")
        dialog = AddSectorDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeSector=sectorSelected[0])
        #dialog = AddSectorDialog(self.tranus_folder, parent=self, codeSector=sectorSelected[0])
        dialog.show()
        result = dialog.exec_()


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


    def __load_sector_cb_data(self):
        id_scenario = self.idScenario
        sectors = self.dataBaseSqlite.selectAll(' sector ', where=f" where id_scenario = {id_scenario}", orderby=" order by id asc")
        for value in sectors:
            self.cb_sector.addItem(f"{value[0]} {value[2]}", value[0])


    def __load_intersector_data(self):
        sectorId = self.cb_sector.itemData(self.cb_sector.currentIndex())
        results = self.dataBaseSqlite.selectAll(' sector ', f" where id = {sectorId} and id_scenario = {self.idScenario}")
        id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)
        
        if self.idScenario and sectorId and results:
            self.sustitute.setText(str(results[0][7]))
            # Default data of the table
            sql = f"""
                with sectors as (
                        select * 
                        from sector),
                intersectors as (
                    select  a.id, a.id||" "||a.name sector, b.min_demand, max_demand, case when elasticity > 0 and elasticity != '' then printf("%f",elasticity) else null end as elasticity, b.substitute, exog_prod_attractors, ind_prod_attractors 
                    from sector a 
                    left join inter_sector_inputs b 
                    on (a.id = b.id_input_sector and a.id_scenario = b.id_scenario) 
                    where a.id_scenario = {self.idScenario} and id_sector = {sectorId} order by a.id asc)
                select distinct a.id||" "||a.name sector, b.min_demand, max_demand, case when elasticity > 0 and elasticity != '' then printf("%f",elasticity) else null end as elasticity, b.substitute, exog_prod_attractors, ind_prod_attractors
                from sectors a
                left join intersectors b on a.id = b.id order by a.id asc
                """

            resultA_prev = None

            sqlB = """with categories as (
                        select * from category
                    ), 
                    intersector_transport as (
                        select a.id, a.id||" "||a.name category, b.type, time_factor, volume_factor, flow_to_product, b.flow_to_consumer 
                        from category a 
                        left join inter_sector_transport_cat b on (a.id = b.id_category) and a.id_scenario = b.id_scenario 
                        where a.id_scenario = %s and id_sector = %s order by a.id asc)
                    select distinct a.id||" "||a.name category, b.type, time_factor, volume_factor, flow_to_product, b.flow_to_consumer 
                    from categories a 
                    left join intersector_transport b on (a.id = b.id) order by a.id asc""" % (self.idScenario, sectorId)

            resultA_prev = None
            resultB_prev = None
            if id_prevScenario:
                sql_prev = f"""
                with sectors as (
                        select * 
                        from sector),
                intersectors as (
                    select  a.id, a.id||" "||a.name sector, b.min_demand, max_demand, case when elasticity > 0 and elasticity != '' then printf("%f",elasticity) else null end as elasticity, b.substitute, exog_prod_attractors, ind_prod_attractors 
                    from sector a 
                    left join inter_sector_inputs b 
                    on (a.id = b.id_input_sector and a.id_scenario = b.id_scenario) 
                    where a.id_scenario = {id_prevScenario[0][0]} and id_sector = {sectorId} order by a.id asc)
                select distinct a.id||" "||a.name sector, b.min_demand, max_demand, case when elasticity > 0 and elasticity != '' then printf("%f",elasticity) else null end as elasticity, b.substitute, exog_prod_attractors, ind_prod_attractors
                from sectors a
                left join intersectors b on a.id = b.id order by a.id asc
                """

                resultA_prev = self.dataBaseSqlite.executeSql(sql_prev)

                sqlB_prev = f"""with categories as (
                        select * from category
                    ), 
                    intersector_transport as (
                        select a.id, a.id||" "||a.name category, b.type, time_factor, volume_factor, flow_to_product, b.flow_to_consumer 
                        from category a 
                        left join inter_sector_transport_cat b on (a.id = b.id_category) and a.id_scenario = b.id_scenario 
                        where a.id_scenario = {id_prevScenario[0][0]} and id_sector = {sectorId} order by a.id asc)
                    select distinct a.id||" "||a.name category, b.type, time_factor, volume_factor, flow_to_product, b.flow_to_consumer 
                    from categories a 
                    left join intersector_transport b on (a.id = b.id) order by a.id asc"""

                resultB_prev = self.dataBaseSqlite.executeSql(sqlB_prev)

            resultA = self.dataBaseSqlite.executeSql(sql)
            
            resultB = self.dataBaseSqlite.executeSql(sqlB)
            
            if len(resultA)==0:
                sql = """select a.id||" "||a.name sector, '' min_demand, '' max_demand, '' elasticity, '' substitute, '' exog_prod_attractors, '' ind_prod_attractors 
                  from sector a 
                  where id_scenario = {} order by a.id asc """.format(self.idScenario)
                resultA = self.dataBaseSqlite.executeSql(sql)

            if len(resultB)==0:
                sql = """select a.id||" "||a.name category, '' type, '' time_factor, '' volume_factor, '' flow_to_product, '' flow_to_consumer 
                    from category a
                    where id_scenario = {} order by a.id asc """.format(self.idScenario)
                resultB = self.dataBaseSqlite.executeSql(sql)

            self.intersectors_table.setRowCount(len(resultA))
            self.intersectors_table.setColumnCount(6)
            self.intersectors_table.setHorizontalHeaderLabels(self.header)
            self.intersectors_table.horizontalHeader().setStretchLastSection(True)
            self.intersectors_table.setColumnWidth(5, 120)

            self.intersectors_table_trans.setRowCount(len(resultB))
            self.intersectors_table_trans.setColumnCount(5)
            self.intersectors_table_trans.setHorizontalHeaderLabels(self.headerTrans)
            self.intersectors_table_trans.horizontalHeader().setStretchLastSection(True)
            

            font = QFont()

            for indice,valor in enumerate(resultA):
                x = 0
                self.intersectors_table.setVerticalHeaderItem(indice, QTableWidgetItem(str(resultA[indice][0])))
                
                for z in range(1,7):
                    data = resultA[indice][z] if resultA[indice][z] is not None else ''
                    itemText = QTableWidgetItem()
                    itemText.setText(Helpers.decimalFormat(str(data)))

                    if resultA_prev:
                        if resultA[indice][z] != resultA_prev[indice][z]:
                            itemText.setForeground(QColor("green"))
                            font.setBold(True)
                            itemText.setFont(font)  
                        else:
                            font.setBold(False)
                            itemText.setFont(font)   
                            itemText.setForeground(QColor("black"))
                    self.intersectors_table.setItem(indice, x, itemText)
                    x+=1

            for indice,valor in enumerate(resultB):
                x = 0
                self.intersectors_table_trans.setVerticalHeaderItem(indice, QTableWidgetItem(str(resultB[indice][0])))
                for z in range(1,6):
                    data = resultB[indice][z] if resultB[indice][z] is not None else ''
                    itemText = QTableWidgetItem()
                    itemText.setText(Helpers.decimalFormat(str(data)))

                    if resultB_prev:
                        # print(resultB[indice], resultB_prev[indice])
                        if resultB[indice][z] != resultB_prev[indice][z]:
                            itemText.setForeground(QColor("green"))
                            font.setBold(True)
                            itemText.setFont(font)  
                        else:
                            font.setBold(False)
                            itemText.setFont(font)   
                            itemText.setForeground(QColor("black"))
                    self.intersectors_table_trans.setItem(indice, x, itemText)
                    x+=1

            header_a = self.intersectors_table.horizontalHeader()       
            header_a.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            header_a.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

            header_b = self.intersectors_table_trans.horizontalHeader()       
            header_b.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            
            self.lb_total_items_input.setText("%s Items " % len(resultA))
            self.lb_total_items_trans.setText("%s Items " % len(resultB))
            

    def load_scenarios(self):
        self.__get_scenarios_data()


    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def close_event(self, event):
        self.close()
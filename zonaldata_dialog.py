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
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import validatorRegex
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_sector_dialog import AddSectorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zonaldata.ui'))

class ZonalDataDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ZonalDataDialog, self).__init__(parent)
        self.setupUi(self)

        # Resize Dialog for high resolution monitor
        resolution_dict = Helpers.screenResolution(70)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        self.zonaldata_model = QtGui.QStandardItemModel()
        self.modelTrans = QtGui.QStandardItemModel()
        self.shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.vertical_header = []
        self.vertical_header_imp = []
        self.vertical_header_exp = []
        self._row = 0
        self._column = 0
        self.table_type = None
        self.header = ['Exog. Production','Induced Production', 'Min. Prod','Max. Prod', 'Exog. Demand','Base Price', 'Value Added', 'Attractor']
        self.header_import = ['Min Imp', 'Max. Imp.', 'Base Price','Attractor']
        self.header_export = ['Exports']
        self.columnZonalDataDb = ["exogenous_production","induced_production","min_production","max_production","exogenous_demand","base_price","value_added","attractor"]
        self.columnZonalDataDbImp = ["max_imports","min_imports","base_price","attractor"]
        self.columnZonalDataDbExp = ["exports"]
        self.scenarioCode = scenarioCode
        self.idScenario = None

        self.project = parent.project
        self.copyScenarioSelected = None
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.lb_total_items_internal = self.findChild(QtWidgets.QLabel, 'total_items_internal')
        self.lb_total_items_imports = self.findChild(QtWidgets.QLabel, 'total_items_imports')
        self.lb_total_items_exports = self.findChild(QtWidgets.QLabel, 'total_items_exports')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.internal_data_table = self.findChild(QtWidgets.QTableWidget, 'internal_data_table')
        self.imports_data_table = self.findChild(QtWidgets.QTableWidget, 'imports_data_table')
        self.exports_data_table = self.findChild(QtWidgets.QTableWidget, 'exports_data_table')
        self.cb_sector = self.findChild(QtWidgets.QComboBox, 'cb_sector')
        self.sustitute = self.findChild(QtWidgets.QLabel, 'sustitute')
        self.btn_sector_detail = self.findChild(QtWidgets.QPushButton, 'btn_sector_detail')

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.btn_sector_detail.clicked.connect(self.open_sector_detail)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_event)
        self.shortcut.activated.connect(self.paste_event)
        self.internal_data_table.cellClicked.connect(self.set_row_colum_internal)
        self.imports_data_table.cellClicked.connect(self.set_row_colum_imports)
        self.exports_data_table.cellClicked.connect(self.set_row_colum_exports)

        self.internal_data_table.itemChanged.connect(self.__validate_internal)
        self.imports_data_table.itemChanged.connect(self.__validate_imports)
        self.exports_data_table.itemChanged.connect(self.__validate_exports)
        
        #self.zonaldata_table.cellClicked.connect(updateCell)

        #Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        
        self.__load_zonal_data()
        self.__get_scenarios_data()

        #Conections to signals
        self.cb_sector.currentIndexChanged[int].connect(self.sector_changed)
        
        

    def __validate_internal(self, item):

        if item.text()!=None and item.text()!='':
            column = item.column()
            item_value = item.text()
            row = item.row()

            result = validatorRegex(item_value, 'real-negative')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.internal_data_table.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))


    def __validate_imports(self, item):

        if item.text()!=None and item.text()!='':
            column = item.column()
            item_value = item.text()
            row = item.row()

            result = validatorRegex(item_value, 'real-negative')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.imports_data_table.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))



    def __validate_exports(self, item):

        if item.text()!=None and item.text()!='':
            column = item.column()
            item_value = item.text()
            row = item.row()

            result = validatorRegex(item_value, 'real-negative')
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.exports_data_table.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))





    def set_row_colum_internal(self, row, column):
        self._row = row
        self._column = column
        self.table_type = 'internal'

    def set_row_colum_imports(self, row, column):
        self._row = row
        self._column = column
        self.table_type = 'imports'

    def set_row_colum_exports(self, row, column):
        self._row = row
        self._column = column
        self.table_type = 'exports'


    # For Paste Text to Table
    def paste_event(self):
        text = QApplication.clipboard().text()
        rows = text.split('\n')
        row = self._row
        column = self._column
        for rowIndex, cells in enumerate(rows):
            cells = cells.split('\t')
            for cellIndex, cell in enumerate(cells):
                if self.table_type == 'internal':
                    self.internal_data_table.setItem(rowIndex+row, cellIndex+column, QTableWidgetItem(str(cell)))
                if self.table_type == 'imports':
                    self.imports_data_table.setItem(rowIndex+row, cellIndex+column, QTableWidgetItem(str(cell)))
                if self.table_type == 'exports':
                    self.exports_data_table.setItem(rowIndex+row, cellIndex+column, QTableWidgetItem(str(cell)))
                

    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__load_sector_data()
        self.__load_zonal_data()


    def save_event(self):
        id_scenario = self.idScenario
        rowsInternal = self.internal_data_table.rowCount()
        rowsImports = self.imports_data_table.rowCount()
        rowsExports = self.exports_data_table.rowCount()
        
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            id_sector = self.cb_sector.itemData(self.cb_sector.currentIndex()) 
            
            zonal_data_arr = []
            for index in range(0,rowsInternal):
                id_zone = self.internal_data_table.verticalHeaderItem(index).text().split(" ")[0] 
                id_zone = id_zone if id_zone != 'Global' else 0
                exogenous_production = self.internal_data_table.item(index, 0).text()
                induced_production = self.internal_data_table.item(index, 1).text()
                min_production = self.internal_data_table.item(index, 2).text()
                max_production = self.internal_data_table.item(index, 3).text()
                exogenous_demand = self.internal_data_table.item(index, 4).text()
                base_price = self.internal_data_table.item(index, 5).text()
                value_added = self.internal_data_table.item(index, 6).text()
                attractor = self.internal_data_table.item(index, 7).text()
                zonal_data_arr.append((id_sector, id_zone, exogenous_production, induced_production, min_production, max_production, exogenous_demand, base_price, value_added, attractor))
            self.dataBaseSqlite.addZonalDataInsertUpdate(scenarios, zonal_data_arr)

            zonal_data_import = []
            for index in range(0,rowsImports):
                id_zone = self.imports_data_table.verticalHeaderItem(index).text().split(" ")[0] 
                id_zone = id_zone if id_zone != 'Global' else 0
                min_imports = self.imports_data_table.item(index, 0).text()
                max_imports = self.imports_data_table.item(index, 1).text()
                base_price = self.imports_data_table.item(index, 2).text()
                attractor = self.imports_data_table.item(index, 3).text()
                zonal_data_import.append((id_sector, id_zone,  min_imports, max_imports, base_price, attractor))
            self.dataBaseSqlite.addZonalDataImportInsertUpdate(scenarios, zonal_data_import) 
            
            zonal_data_exports = []
            for index in range(0,rowsExports):
                id_zone = self.imports_data_table.verticalHeaderItem(index).text().split(" ")[0] 
                id_zone = id_zone if id_zone != 'Global' else 0
                exports = self.exports_data_table.item(index, 0).text()
                zonal_data_exports.append((id_sector, id_zone, exports))
            self.dataBaseSqlite.addZonalDataExportsInsertUpdate(scenarios, zonal_data_exports)
            
        self.close()


    def __find_scenario_data(self, scenarioSelectedIndex):
        """
            @summary: Find and Set data of the scenario Selected
        """
        codeScenario = self.scenarioSelectedIndex.data().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(codeScenario))
        self.idScenario = scenarioData[0][0]


    def sector_changed(self):
        self.__load_zonal_data()


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
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        itemsList = self.scenarios_model.findItems(self.scenarioCode, Qt.MatchContains | Qt.MatchRecursive, 0)
        indexSelected = self.scenarios_model.indexFromItem(itemsList[0])
        modelSelection.setCurrentIndex(indexSelected, QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)
        
        self.select_scenario(self.scenario_tree.selectedIndexes()[0])

    def __load_sector_data(self):
        
        sectors = self.dataBaseSqlite.selectAll(' sector ', where = f" where id_scenario = {self.idScenario}")
        
        if self.cb_sector.count() == 0:
            for value in sectors:
                self.cb_sector.addItem( f"{value[0]} {value[2]}", value[0])
        

    def __load_zonal_data(self):
        id_sector = self.cb_sector.itemData(self.cb_sector.currentIndex())
        
        if self.idScenario:
            # Internal Zonal Data
            id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)

            sql = """select 
                        zone.id||" "||zone.name zone, zone.external, exogenous_production, 
                        induced_production, min_production, max_production,   
                        exogenous_demand, base_price, value_added, attractor
                    from 
                    (select * from zone) zone
                    left join 
                    (select a.id_zone, exogenous_production, induced_production, min_production, 
                    max_production, exogenous_demand, base_price, value_added, attractor 
                    from zonal_data a
                    where a.id_sector = {} and a.id_scenario = {}) zonal_data
                    on zone.id = zonal_data.id_zone
                    where (external is null or external = 0)
                    order by zone.id""".format(id_sector, self.idScenario)

            # Imports Zonal Data
            sql_import = """select 
                        zone.id||" "||zone.name zone,  zone.external, min_imports,  
                        max_imports, base_price, attractor_import
                    from 
                    (select * from zone where external = 1) zone
                    left join 
                    (select a.id_zone,  min_imports, max_imports, base_price,
                    attractor_import
                    from zonal_data a
                    where a.id_sector = {} and a.id_scenario = {}) zonal_data
                    on zone.id = zonal_data.id_zone
                    order by zone.id""".format(id_sector, self.idScenario)

            # Exports Zonal Data
            sql_exp = """select 
                        zone.id||" "||zone.name zone,  zone.external, exports
                    from 
                    (select * from zone where external = 1) zone
                    left join 
                    (select a.id_zone, exports
                    from zonal_data a
                    where a.id_sector = {} and a.id_scenario = {}) zonal_data
                    on zone.id = zonal_data.id_zone
                    order by zone.id""".format(id_sector, self.idScenario)


            result = self.dataBaseSqlite.executeSql(sql)
            result_imp = self.dataBaseSqlite.executeSql(sql_import)
            result_exp = self.dataBaseSqlite.executeSql(sql_exp)

            result_prev = None
            result_imp_prev = None
            result_exp_prev = None

            if id_prevScenario:
                # Internal Zonal Data Prevous Scenario
                sql_prev = """select 
                            zone.id||" "||zone.name zone, zone.external, exogenous_production, 
                            induced_production, min_production, max_production,   
                            exogenous_demand, base_price, value_added, attractor
                        from 
                        (select * from zone) zone
                        left join 
                        (select a.id_zone, exogenous_production, induced_production, 
                        min_production, max_production, exogenous_demand, base_price, value_added, attractor 
                        from zonal_data a
                        where a.id_sector = {} and a.id_scenario = {}) zonal_data
                        on zone.id = zonal_data.id_zone
                        where (external is null or external = 0)
                        order by zone.id""".format(id_sector, id_prevScenario[0][0])
                
                # Imports Zonal Data
                sql_import_prev = """select 
                            zone.id||" "||zone.name zone,  zone.external, min_imports,
                            max_imports, base_price, attractor_import
                        from 
                        (select * from zone where external = 1) zone
                        left join 
                        (select a.id_zone, max_imports, min_imports, base_price,
                        attractor_import
                        from zonal_data a
                        where a.id_sector = {} and a.id_scenario = {}) zonal_data
                        on zone.id = zonal_data.id_zone
                        order by zone.id""".format(id_sector, id_prevScenario[0][0])

                # Exports Zonal Data
                sql_exp_prev = """select 
                    zone.id||" "||zone.name zone,  zone.external, exports
                    from 
                    (select * from zone where external = 1) zone
                    left join 
                    (select a.id_zone, exports
                    from zonal_data a
                    where a.id_sector = {} and a.id_scenario = {}) zonal_data
                    on zone.id = zonal_data.id_zone
                    order by zone.id""".format(id_sector, id_prevScenario[0][0])
                
                result_prev = self.dataBaseSqlite.executeSql(sql_prev)
                result_imp_prev = self.dataBaseSqlite.executeSql(sql_import_prev)
                result_exp_prev = self.dataBaseSqlite.executeSql(sql_exp_prev)
            
            if len(result)==0:
                    sql = """select 
                            a.id||" "||a.name zone, a.external, '' exogenous_production, 
                            '' induced_production, '' min_production, '' max_production,  
                            '' exogenous_demand, '' base_price, '' value_added, '' attractor
                        from zone a  
                        order by a.id"""
                    result = self.dataBaseSqlite.executeSql(sql) 

            if len(result_imp)==0:
                    sql_import = """select 
                        zone.id||" "||zone.name zone,  zone.external,  '' min_imports, '' max_imports, 
                        '' base_price, '' attractor_import
                    from 
                    (select * from zone where external = 1) zone
                    order by zone.id"""
                    result_imp = self.dataBaseSqlite.executeSql(sql_import)

            if len(result_exp)==0:
                    sql_exp = """select 
                        zone.id||" "||zone.name zone,  zone.external, '' exports
                    from 
                    (select * from zone where external = 1) zone
                    order by zone.id"""
                    result_exp = self.dataBaseSqlite.executeSql(sql_exp)

            #Internal Zonal Data
            columsCount = len(self.header)
            rowsCount = len(result)
            self.internal_data_table.setRowCount(rowsCount)
            self.internal_data_table.setColumnCount(columsCount)
            self.internal_data_table.setHorizontalHeaderLabels(self.header) # Headers of columns table
            
            #Import Zonal Data
            columsCount = len(self.header_import)
            rowsCount = len(result_imp)
            self.imports_data_table.setRowCount(rowsCount)
            self.imports_data_table.setColumnCount(columsCount)
            self.imports_data_table.setHorizontalHeaderLabels(self.header_import) # Headers of columns table
            self.imports_data_table.horizontalHeader().setStretchLastSection(True)

            #Export Zonal Data
            columsCount = len(self.header_export)
            rowsCount = len(result_exp)
            self.exports_data_table.setRowCount(rowsCount)
            self.exports_data_table.setColumnCount(columsCount)
            self.exports_data_table.setHorizontalHeaderLabels(self.header_export) # Headers of columns table
            self.exports_data_table.horizontalHeader().setStretchLastSection(True)

            font = QFont()

            #Internal Header
            for index, valor in enumerate(result):
                self.vertical_header.append(valor[0])
                if valor[0] == '0 Global Increments':
                    headerItem = QTableWidgetItem('Global Increments')
                else:
                    headerItem = QTableWidgetItem(valor[0])
                if valor[0] != '0 Global Increments':
                    if valor[1]==1:
                        headerItem.setIcon(QIcon(self.plugin_dir+"/icons/mini-square-red.jpg"))
                    else:
                        headerItem.setIcon(QIcon(self.plugin_dir+"/icons/mini-square-gray.jpg"))
                self.internal_data_table.setVerticalHeaderItem(index,headerItem)
            
            header = self.internal_data_table.horizontalHeader()       
            for x in range(0,columsCount):
                header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)
            
            #Internal Data
            for indice, valor in enumerate(result):
                x = 0
                for z in range(2,len(valor)):
                    data = result[indice][z] if result[indice][z] is not None else ''
                    itemText = QTableWidgetItem()
                    itemText.setText(Helpers.decimalFormat(str(data)))
                    if indice == 0 and len(id_prevScenario) == 0:
                        itemText.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled  )
                    
                    if result_prev:
                        if result[indice][z] != result_prev[indice][z]:
                            itemText.setForeground(QColor("green"))
                            font.setBold(True)
                            itemText.setFont(font)  
                        else:
                            font.setBold(False)
                            itemText.setFont(font)   
                            itemText.setForeground(QColor("black"))
                    self.internal_data_table.setItem(indice, x, itemText)
                    x+=1
                    
            #Imports Zonal Data
            for index, valor in enumerate(result_imp):
                self.vertical_header_imp.append(valor[0])
                headerItem = QTableWidgetItem(valor[0])
                if valor[1]==1:
                    headerItem.setIcon(QIcon(self.plugin_dir+"/icons/mini-square-red.jpg"))
                else:
                    headerItem.setIcon(QIcon(self.plugin_dir+"/icons/mini-square-gray.jpg"))
                self.imports_data_table.setVerticalHeaderItem(index,headerItem)
            
            header = self.imports_data_table.horizontalHeader()       
            for x in range(0,columsCount):
                header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)
            for indice,valor in enumerate(result_imp):
                x = 0
                for z in range(2,len(valor)):
                    data = result_imp[indice][z] if result_imp[indice][z] is not None else ''
                    itemText = QTableWidgetItem()
                    itemText.setText(Helpers.decimalFormat(str(data)))

                    if result_imp_prev:
                        if result_imp[indice][z] != result_imp_prev[indice][z]:
                            itemText.setForeground(QColor("green"))
                            font.setBold(True)
                            itemText.setFont(font)  
                        else:
                            font.setBold(False)
                            itemText.setFont(font)   
                            itemText.setForeground(QColor("black"))

                    self.imports_data_table.setItem(indice, x, itemText)
                    x+=1

            # Export Zonal Data
            for index, valor in enumerate(result_exp):
                self.vertical_header_exp.append(valor[0])
                headerItem = QTableWidgetItem(valor[0])
                if valor[1]==1:
                    headerItem.setIcon(QIcon(self.plugin_dir+"/icons/mini-square-red.jpg"))
                else:
                    headerItem.setIcon(QIcon(self.plugin_dir+"/icons/mini-square-gray.jpg"))
                self.exports_data_table.setVerticalHeaderItem(index,headerItem)
            
            header = self.exports_data_table.horizontalHeader()       
            for x in range(0,columsCount):
                header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)

            for indice,valor in enumerate(result_exp):
                x = 0
                for z in range(2,len(valor)):
                    data = result_exp[indice][z] if result_exp[indice][z] is not None else ''
                    itemText = QTableWidgetItem()
                    itemText.setText(Helpers.decimalFormat(str(data)))

                    if result_imp_prev:
                        if result_exp[indice][z] != result_exp_prev[indice][z]:
                            itemText.setForeground(QColor("green"))
                            font.setBold(True)
                            itemText.setFont(font)  
                        else:
                            font.setBold(False)
                            itemText.setFont(font)   
                            itemText.setForeground(QColor("black"))

                    self.exports_data_table.setItem(indice, x, itemText)
                    x+=1

            header_a = self.internal_data_table.horizontalHeader()       
            header_a.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            header_a.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

            self.lb_total_items_internal.setText("%s Items " % len(result))
            self.lb_total_items_imports.setText("%s Items " % len(result_imp))
            self.lb_total_items_exports.setText("%s Items " % len(result_exp))


    def load_scenarios(self):
        self.__get_scenarios_data()

    def ok_button(self):
        self.parent().load_scenarios()
        self.accept()
    
    def cancel_button(self):
        self.__rollback_changes()
        
    def close_event(self, event):
        self.parent().load_scenarios()
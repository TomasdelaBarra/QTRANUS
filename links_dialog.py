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
from .add_link_dialog import AddLinkDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'links.ui'))

class LinksDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, scenarioCode, scenarioSelectedIndex=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(LinksDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioSelectedIndex = scenarioSelectedIndex
        self.scenarioCode = scenarioCode
        self.idScenario = None
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], resolution_dict['height'])
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.links_tree = self.findChild(QtWidgets.QTreeView, 'links_tree')
        self.links_tree.setRootIsDecorated(False)
        self.lb_total_items_links = self.findChild(QtWidgets.QLabel, 'total_items_links')
        self.add_link_btn = self.findChild(QtWidgets.QPushButton, 'add_link_btn')
        self.show_used_btn = self.findChild(QtWidgets.QPushButton, 'show_used')
        self.show_changed_btn = self.findChild(QtWidgets.QPushButton, 'show_changed')
        self.le_search = self.findChild(QtWidgets.QLineEdit, 'le_search')
        self.btn_search = self.findChild(QtWidgets.QPushButton, 'btn_search')
        self.le_search.setPlaceholderText("Link ID")

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.add_link_btn.clicked.connect(self.open_add_link_window)
        self.btn_search.clicked.connect(self.__search_link)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.links_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.links_tree.customContextMenuRequested.connect(self.open_menu_links)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)
        
        # Loads
        # LOAD SCENARIO FROM FILE self.__load_scenarios_from_db_file()
        self.__get_scenarios_data()
        self.__get_links_data()

        # Set scenarioIndex
        if self.scenarioCode:
            self.__find_scenario_data(self.scenarioCode)

        #Add Icons
        self.ic_one_way = QIcon(self.plugin_dir+"/icons/one-way-road.png")
        self.ic_two_way_road = QIcon(self.plugin_dir+"/icons/two-way-road.png")
        self.show_used_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        self.show_used_btn.setToolTip("Show Used Only")
        self.show_changed_btn.setIcon(QIcon(self.plugin_dir+"/icons/square-green.png"))
        self.show_changed_btn.setToolTip("Show Changed Only")
        self.add_link_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        self.btn_search.setIcon(QIcon(self.plugin_dir+"/icons/search.svg"))
        self.btn_search.setToolTip("Search Link ID")

    def __search_link(self):
        le_searchTxt = self.le_search.text()
        if not le_searchTxt:
            #messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Search", "Please enter value.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            #messagebox.exec_()
            self.__get_links_data()
            return False
        self.__get_links_data(linkid=le_searchTxt)


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.__get_links_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)



    def open_menu_links(self, position):
        menu = QMenu()

        indexes = self.links_tree.selectedIndexes()
        linkSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

        edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Link')
        remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Remove Link')

        opt = menu.exec_(self.links_tree.viewport().mapToGlobal(position))

        if opt == edit:
            if not self.idScenario:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            else:
                dialog = AddLinkDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeLink=linkSelected)
                dialog.show()
                result = dialog.exec_()
                self.__get_links_data()
        if opt == remove:
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            
            self.dataBaseSqlite.removeLink(scenarios, linkSelected)
            self.__get_links_data()
            


    def open_add_link_window(self):
        """
            @summary: Opens add scenario window
        """
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            dialog = AddLinkDialog(self.tranus_folder, idScenario=self.idScenario,  parent = self)
            dialog.show()
            result = dialog.exec_()
            self.__get_links_data()
        

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
        
        return True

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
               

    def __get_links_data(self, linkid=None): 
        linkid = f" and linkid like '%{linkid}%' " if linkid else ''
        qry = """with base as (
                    select distinct case when (a.two_way is null or a.two_way == '') 
                                    then '0' else a.two_way end ||' '||linkid linkid, a.name,  b.id||' '||b.name linktype, 
                                    node_from, node_to
                    from link a
                    left join link_type b on (a.id_linktype = b.id) and (a.id_scenario = b.id_scenario)
                    WHERE a.id_scenario = {0} and (two_way is null or two_way == '' or two_way == 0) {1}
                    group  by 1,2,3,4,5
                ), two_way as (
                select  
                        case when 
                            cast(substr(linkid, 0, instr(linkid, '-')) as integer) < cast(substr(linkid, instr(linkid, '-')+1) as INTEGER) 
                            then '1'||' '||substr(linkid, 0, instr(linkid, '-'))||'-'||substr(linkid, instr(linkid, '-')+1)
                            else '1'||' '||substr(linkid, instr(linkid, '-')+1)||'-'||substr(linkid, 0, instr(linkid, '-')) 
                            end linkid,
                        a.name,
                        b.id||' '||b.name linktype,
                        a.node_from,
                        a.node_to
                    from link a
                    left join link_type b on (a.id_linktype = b.id) and (a.id_scenario = b.id_scenario)
                    where two_way = 1 and a.id_scenario = {0} {1}
                    group by 1)
                select linkid, name, linktype, cast(substr(substr(linkid,3), 0, instr(substr(linkid,3), '-')) as INTEGER)  node_from, cast(substr(substr(linkid,3), instr(substr(linkid,3), '-')+1) as INTEGER) node_to
                from (
                    select linkid, name, linktype, node_from, node_to
                    from base
                    UNION
                    select linkid, name, linktype, node_from, node_to
                    from two_way 
                ) order by node_from, node_to asc""".format(self.idScenario, linkid)
                
        result = self.dataBaseSqlite.executeSql(qry)
        
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Link Type'])
        for x in range(0, len(result)):
            model.insertRow(x)
            z = 0
            for y in range(0,3):
                item = QtGui.QStandardItem()
                item.setText(result[x][z])
                if z == 0:
                    if result[x][z].split(" ")[0] != '0' and result[x][z].split(" ")[0] != '':
                        item.setIcon(QIcon(self.plugin_dir+"/icons/two-way-road.png"))
                    else:
                        item.setIcon(QIcon(self.plugin_dir+"/icons/one-way-road.png"))
                    item.setText(result[x][z].split(" ")[1])
                
                
                model.setItem( x, z, item)
                z+=1
        self.links_tree.setModel(model)
        self.links_tree.setColumnWidth(0, 100)
        self.lb_total_items_links.setText(" %s Items" % len(result))
        


    def load_scenarios(self):
        self.__get_scenarios_data()
    

    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]
        
            
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
# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser, numpy as np

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
from .add_category_dialog import AddCategoryDialog
from .link_type_dialog import LinkTypeDialog
from .add_link_dialog import AddLinkDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'database_error.ui'))

class DatabaseErrorsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, linktypesList, scenarioCode, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(DatabaseErrorsDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.idScenario = None
        self.copyScenarioSelected = None
        self.linktypesList = linktypesList
        self.scenarioCode = scenarioCode
        self.tranus_folder = tranus_folder
        self.result_adm = []
        self.result_oper = []
        self.result_linkType = []
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.plugin_dir = os.path.dirname(__file__)
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], 400)

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.links_tree = self.findChild(QtWidgets.QTreeView, 'links_tree')
        self.links_tree.setRootIsDecorated(False)
        self.links_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.links_tree.customContextMenuRequested.connect(self.open_menu_links)
        self.le_linktype = self.findChild(QtWidgets.QLineEdit, 'le_linktype')
        self.lb_total_items_links = self.findChild(QtWidgets.QLabel, 'lbl_total_items_links')
        self.btn_linktype = self.findChild(QtWidgets.QPushButton, 'btn_linktype')
        self.statusbar_container = self.findChild(QtWidgets.QVBoxLayout, 'statusbar_container')
        self.btn_linktype.setIcon(QIcon(self.plugin_dir+"/icons/link-type.png"))
        self.btn_linktype.setToolTip("Link Type")

        self.btn_linktype.clicked.connect(self.open_linktype_window)

        

        self.load_data()
        self.__get_scenarios_data()
        self.__get_links_data()
        self.__validate_buttons()


    def open_menu_links(self, position):
        menu = QMenu()

        indexes = self.links_tree.selectedIndexes()
        linkSelected = indexes[0].model().itemFromIndex(indexes[0]).text()
        editAction = QAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Link', )
        self.result_linkType = self.dataBaseSqlite.selectAll(" link_type ")

        if len(self.result_linkType) == 0:
            editAction.setEnabled(False)
        else:
            editAction.setEnabled(True)

        edit = menu.addAction(editAction)
        opt = menu.exec_(self.links_tree.viewport().mapToGlobal(position))
        if isinstance(opt, QtWidgets.QAction):
            if opt.text() == editAction.text():
                if not self.idScenario:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                else:
                    dialog = AddLinkDialog(self.tranus_folder, idScenario=self.idScenario, parent = self, codeLink=linkSelected)
                    dialog.show()
                    result = dialog.exec_()
                    self.__get_links_data()


    def __validate_buttons(self):
        self.result_adm = self.dataBaseSqlite.selectAll(" administrator ", where=" where id_scenario = %s" % self.idScenario)
        self.result_oper = self.dataBaseSqlite.selectAll(" operator ", where=" where id_scenario = %s" % self.idScenario)

        errorMsgTxt = '<b>Info:</b> Please Create'
        errorMsgTxt += ', Administrator' if len(self.result_adm) == 0 else ''
        errorMsgTxt += ', Operator' if len(self.result_oper) == 0 else ''

        if len(self.result_adm) == 0 or len(self.result_oper) == 0:
            self.btn_linktype.setEnabled(False)
            statusBar = QtWidgets.QStatusBar()
            mensaje = QtWidgets.QLabel()
            mensaje.setText(errorMsgTxt)
            mensaje.setStyleSheet( "color : #2E86C1;" )
            statusBar.addWidget(mensaje)
            self.statusbar_container.addWidget(statusBar)
        else:
            self.btn_linktype.setEnabled(True)
        
       

    def open_linktype_window(self):
        """
            @summary: Opens administrators window
        """
        dialog = LinkTypeDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.finished.connect(self.close_linktype_window)
        dialog.show()
        

    def close_linktype_window(self):
        self.linktypeWithoutDefinitions()
        self.load_data()
        self.__get_links_data()


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


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        
        self.linktypeWithoutDefinitions()
        self.__get_links_data()


    def __get_links_data(self, linkid=None): 
        linkid = f" and linkid like '%{linkid}%' " if linkid else ''
        qry = """with base as (
                    select distinct case when (a.two_way is null or a.two_way == '') 
                                    then '0' else a.two_way end ||' '||linkid linkid, a.name,  a.id_linktype linktype, 
                                    node_from, node_to
                    from link a
                    left join link_type b on (a.id_linktype = b.id) and (a.id_scenario = b.id_scenario)
                    WHERE a.id_scenario = {0} and (two_way is null or two_way == '' or two_way == 0) {1}
                    and (b.id is null)
                    group  by 1,2,3,4,5
                ), two_way as (
                select  
                        case when 
                            cast(substr(linkid, 0, instr(linkid, '-')) as integer) < cast(substr(linkid, instr(linkid, '-')+1) as INTEGER) 
                            then '1'||' '||substr(linkid, 0, instr(linkid, '-'))||'-'||substr(linkid, instr(linkid, '-')+1)
                            else '1'||' '||substr(linkid, instr(linkid, '-')+1)||'-'||substr(linkid, 0, instr(linkid, '-')) 
                            end linkid,
                        a.name,
                        a.id_linktype linktype,
                        a.node_from,
                        a.node_to
                    from link a
                    left join link_type b on (a.id_linktype = b.id) and (a.id_scenario = b.id_scenario)
                    where two_way = 1 and a.id_scenario = {0} {1} and (b.id is null)
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
                item.setText(str(result[x][z] if result[x][z] != None else '-'))
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


    def load_data(self):
        if self.linktypesList:
            idLinktype =  ", ".join(self.linktypesList)
            self.le_linktype.setText(idLinktype)


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def __load_scenarios(self):
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenario_tree.setSelectionModel(modelSelection)

    def load_scenarios(self):
        self.__load_scenarios()

    def linktypeWithoutDefinitions(self):

        sql = """
            select distinct a.id_linktype
            from link a
            left join link_type  b on (a.id_linktype = b.id)
            where b.id is null or b.id = '' and a.id_scenario = %s
            order by 1 
            """ % (self.idScenario)
        result = self.dataBaseSqlite.executeSql(sql)
        
        self.linktypesList = []
        for value in result:
            self.linktypesList.append(str(value[0]))

        return result
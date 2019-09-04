# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *

from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import * # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .add_routes_links_dialog import AddRoutesLinksDialog
from .add_linktype_dialog import AddLinkTypeDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_link.ui'))

class AddLinkDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, idScenario = None, parent = None, codeLink=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddLinkDialog, self).__init__(parent)
        self.setupUi(self)
        self.dialogAddRoutesLink = None
        self.turns_delays_arr = []
        self.id_operators_arr = []
        self.id_routes_arr_selected = []
        self.project = parent.project
        self.codeLink = codeLink
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder )
        self.idScenario = idScenario
        resolution_dict = Helpers.screenResolution(70)
        self.resize(resolution_dict['width'], resolution_dict['height'])
        self.plugin_dir = os.path.dirname(__file__)
        self.modelRoutes = QtGui.QStandardItemModel()

        # Linking objects with controls
        # Principal Section
        self.cb_origin = self.findChild(QtWidgets.QComboBox, 'cb_origin')
        self.cb_destination = self.findChild(QtWidgets.QComboBox, 'cb_destination')
        self.cb_type = self.findChild(QtWidgets.QComboBox, 'cb_type')
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')

        # Data Section
        self.two_way = self.findChild(QtWidgets.QCheckBox, 'two_way')
        self.used_in_scenario = self.findChild(QtWidgets.QCheckBox, 'used_in_scenario')
        self.length = self.findChild(QtWidgets.QLineEdit, 'length')
        self.capacity = self.findChild(QtWidgets.QLineEdit, 'capacity')
        self.delay = self.findChild(QtWidgets.QLineEdit, 'delay')

        # Aviable Operators Section
        self.tbl_operators = self.findChild(QtWidgets.QTableWidget, 'tbl_operators')

        # Routes Section
        self.tree_routes = self.findChild(QtWidgets.QTreeView, 'tree_routes')
        self.tree_routes.setRootIsDecorated(False)
        self.btn_pass_and_stop = self.findChild(QtWidgets.QPushButton, 'btn_pass_and_stop')
        self.btn_pass_only = self.findChild(QtWidgets.QPushButton, 'btn_pass_only')
        self.btn_no_pass = self.findChild(QtWidgets.QPushButton, 'btn_no_pass')
        self.btn_add_route = self.findChild(QtWidgets.QPushButton, 'btn_add_route')
        self.btn_remove_route = self.findChild(QtWidgets.QPushButton, 'btn_remove_route')
        self.btn_reverse = self.findChild(QtWidgets.QPushButton, 'btn_reverse')
        self.btn_linktype = self.findChild(QtWidgets.QPushButton, 'btn_linktype')
        self.btn_cannot_turn = self.findChild(QtWidgets.QPushButton, 'btn_cannot_turn')
        

        # Turns Section
        self.tbl_turns = self.findChild(QtWidgets.QTableWidget, 'tbl_turns')

        # Scenarios Tree
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenario_tree')
        
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')

        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_link)

        # Validations
        self.name.setMaxLength(10)
        self.description.setMaxLength(55)
        self.length.setValidator(validatorExpr('decimal'))
        self.length.textChanged.connect(self.check_state)
        #self.capacity.setValidator(validatorExpr('decimal'))
        #self.capacity.textChanged.connect(self.check_state)
        self.delay.setValidator(validatorExpr('decimal'))
        self.delay.textChanged.connect(self.check_state)
        
        self.cb_type.currentTextChanged.connect(self.__load_tb_operator_aviable)
        self.cb_destination.currentTextChanged.connect(self.__load_tb_turns_delay)
        
        
        self.__load_cb_type()
        self.__load_cb_ori_dest()
        self.__load_tb_operator_aviable()

        self.btn_pass_and_stop.setIcon(QIcon(self.plugin_dir+"/icons/bus-stop.png"))
        self.btn_pass_and_stop.setToolTip("Passes and Stops")
        self.btn_pass_only.setIcon(QIcon(self.plugin_dir+"/icons/green-light.png"))
        self.btn_pass_only.setToolTip("Passes only")
        self.btn_no_pass.setIcon(QIcon(self.plugin_dir+"/icons/red-light.png"))
        self.btn_no_pass.setToolTip("Cannot pass")
        self.btn_add_route.setIcon(QIcon(self.plugin_dir+"/icons/bus-icon.png"))
        self.btn_add_route.setToolTip("Add Routes")
        self.btn_remove_route.setIcon(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"))
        self.btn_remove_route.setToolTip("Remove Route")
        self.btn_reverse.setIcon(QIcon(self.plugin_dir+"/icons/reverse.png"))
        self.btn_reverse.setToolTip("Reverse Link")
        self.btn_linktype.setIcon(QIcon(self.plugin_dir+"/icons/link-type.png"))
        self.btn_linktype.setToolTip("Link Type")

        self.btn_turn_ok.setIcon(QIcon(self.plugin_dir+"/icons/green-light.png"))
        self.btn_turn_ok.setToolTip("Turn Ok")   
        self.btn_cannot_turn.setIcon(QIcon(self.plugin_dir+"/icons/no-turn-right.png"))
        self.btn_cannot_turn.setToolTip("Cannot Turn")        

        self.ic_bus_stop = QIcon(self.plugin_dir+"/icons/bus-stop.png")
        self.ic_bus = QIcon(self.plugin_dir+"/icons/bus-icon.png")
        self.ic_greenlight = QIcon(self.plugin_dir+"/icons/green-light.png")
        self.ic_redlight = QIcon(self.plugin_dir+"/icons/red-light.png")
        self.ic_no_turn = QIcon(self.plugin_dir+"/icons/no-turn-right.png")
        self.ic_link_type = QIcon(self.plugin_dir+"/icons/link-type.png")

        self.btn_add_route.clicked.connect(self.open_add_route_link_window)
        self.btn_remove_route.clicked.connect(self.remove_route)
        self.btn_pass_only.clicked.connect(self.set_pass_only)
        self.btn_no_pass.clicked.connect(self.set_cannot_pass)
        self.btn_pass_and_stop.clicked.connect(self.set_pass_stop)
        self.btn_reverse.clicked.connect(self.load_reverse)
        self.btn_linktype.clicked.connect(self.load_linktype)
        self.btn_turn_ok.clicked.connect(self.set_turn_ok)
        self.btn_cannot_turn.clicked.connect(self.set_connot_turn)

        self.__validateReverse()
        self.__load_tb_turns_delay()
        #Loads
        self.__get_scenarios_data()
        if self.codeLink is not None:
            self.setWindowTitle("Edit Link")
            self.load_default_data()
            

    def __validateReverse(self):
        self.btn_reverse.setEnabled(False)

        if self.codeLink:
            linkid = self.codeLink.split("-")
            linkid = f"{linkid[1]}-{linkid[0]}"
            result = self.dataBaseSqlite.selectAll(" link ", where=f" where linkid = '{linkid}'")
            if result:
                self.btn_reverse.setEnabled(True)


    def load_reverse(self):
        linkid = self.codeLink.split("-")
        linkid = f"{linkid[1]}-{linkid[0]}"
        self.codeLink = linkid
        self.load_default_data()


    def load_linktype(self):
        linkTypeSelected = self.cb_type.itemData(self.cb_type.currentIndex())
        dialog = AddLinkTypeDialog(self.tranus_folder, parent = self,  linkTypeSelected=linkTypeSelected, idScenario=self.idScenario)
        dialog.show()
        result = dialog.exec_()
        self.__load_tb_operator_aviable()


    def remove_route(self):
        """
            @summary: Opens add scenario window
        """
        currentIndex = self.tree_routes.currentIndex()
        route = currentIndex.model().itemFromIndex(currentIndex).text().split(" ")[0]

        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, " Remove Route ", "Are you sure?", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        result = messagebox.exec_()

        if QtWidgets.QMessageBox.Ok == result:
            if currentIndex.isValid():
                model = self.tree_routes.model()
                model.removeRow(currentIndex.row(), currentIndex.parent())
                if self.codeLink:
                    id_scenario = self.idScenario
                    id_origin = self.cb_origin.itemData(self.cb_origin.currentIndex())
                    id_destination = self.cb_destination.itemData(self.cb_destination.currentIndex())
                    id_link = f"{id_origin}-{id_destination}"
                    scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
                    scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

                    self.dataBaseSqlite.deleteRouteFLink(scenarios, id_link, route) 

    def set_connot_turn(self):
        """
            @summary: Opens add scenario window
        """
        selectedItems = self.tbl_turns.selectedItems()
        for item in selectedItems:
            headerItem = QTableWidgetItem()
            headerItem.setIcon(QIcon(self.plugin_dir+"/icons/no-turn-right.png"))
            headerItem.setText(self.tbl_turns.verticalHeaderItem(item.row()).text())
            self.tbl_turns.setVerticalHeaderItem(item.row(),headerItem)
            self.tbl_turns.setItem(item.row(), 0, QTableWidgetItem("Inf"))


    def set_turn_ok(self):
        """
            @summary: Opens add scenario window
        """
        selectedItems = self.tbl_turns.selectedItems()
        for item in selectedItems:
            headerItem = QTableWidgetItem()
            headerItem.setIcon(QIcon(self.plugin_dir+"/icons/green-light.png"))
            headerItem.setText(self.tbl_turns.verticalHeaderItem(item.row()).text())
            self.tbl_turns.setVerticalHeaderItem(item.row(),headerItem)
            self.tbl_turns.setItem(item.row(), 0, QTableWidgetItem(""))


    def set_pass_stop(self):
        """
            @summary: Opens add scenario window
        """
        currentIndex = self.tree_routes.currentIndex()
        if currentIndex.isValid():
            model = currentIndex.model()
            itemSelected = model.itemFromIndex(currentIndex)
            itemSelected.setData('passes_stops',Qt.UserRole)
            itemSelected.setIcon(self.ic_bus_stop)
            model.takeRow(currentIndex.row())
            model.insertRow(currentIndex.row(),itemSelected)


    def set_pass_only(self):
        """
            @summary: Opens add scenario window
        """
        currentIndex = self.tree_routes.currentIndex()
        if currentIndex.isValid():
            model = currentIndex.model()
            itemSelected = model.itemFromIndex(currentIndex)            
            itemSelected.setData('passes_only',Qt.UserRole)
            itemSelected.setIcon(self.ic_greenlight)
            model.takeRow(currentIndex.row())
            model.insertRow(currentIndex.row(),itemSelected)


    def set_cannot_pass(self):
        """
            @summary: Opens add scenario window
        """
        currentIndex = self.tree_routes.currentIndex()
        if currentIndex.isValid():
            model = currentIndex.model()
            itemSelected = model.itemFromIndex(currentIndex)
            itemSelected.setData('cannot_pass',Qt.UserRole)
            itemSelected.setIcon(self.ic_redlight)
            model.takeRow(currentIndex.row())
            model.insertRow(currentIndex.row(),itemSelected)
        

    def open_add_route_link_window(self):
        """
            @summary: Opens add scenario window
        """
        if not self.idScenario:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Please Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            self.dialogAddRoutesLink = AddRoutesLinksDialog(self.tranus_folder, id_operators_arr=self.id_operators_arr, idScenario=self.idScenario,  parent = self)
            self.dialogAddRoutesLink.show()
            result = self.dialogAddRoutesLink.exec_()
        return


    def __load_tb_operator_aviable(self):
        id_linktype = self.cb_type.itemData(self.cb_type.currentIndex())
       
        header = ['Name', 'Description']
        qry = """select b.id||' '||b.name name, b.description
                from link_type_operator a
                join operator b 
                on (a.id_operator = b.id)
                where a.id_linktype = %s and speed is not null """ % (id_linktype)
        
        result = self.dataBaseSqlite.executeSql(qry)
        self.id_operators_arr = []
        for value in result:
            self.id_operators_arr.append(value[0].split(" ")[0])

        if result:
            rowsCount = len(result)
            columsCount = len(result[0])
            self.tbl_operators.setRowCount(rowsCount)
            self.tbl_operators.setColumnCount(columsCount)
            self.tbl_operators.setHorizontalHeaderLabels(header) # Headers of columns table
            self.tbl_operators.horizontalHeader().setStretchLastSection(True)

            # Set columns size
            for index,value in enumerate(result):
                x = 0
                for z in range(0,len(value)):
                    data = result[index][z] if result[index][z] is not None else ''
                    item = QTableWidgetItem(str(data))
                    item.setFlags(Qt.NoItemFlags)
                    self.tbl_operators.setItem(index, x, item)
                    x+=1
        else:
            self.tbl_operators.clear()
            self.tbl_operators.setRowCount(0)
            self.tbl_operators.setColumnCount(0)
        return 


    def __load_tb_turns_delay(self):
        id_origin = self.cb_origin.itemData(self.cb_origin.currentIndex())
        id_destination = self.cb_destination.itemData(self.cb_destination.currentIndex())
        header = [ 'Delay']
        #header = ['Turn To','Delay']

        if self.codeLink:
            qry = f"""select id_node node_to, delay
            from intersection_delay 
            where id_link = '{id_origin}-{id_destination}'
            and id_scenario = {self.idScenario}""" 
            result_a = self.dataBaseSqlite.executeSql(qry)
            if not result_a:
                qry = f"""select node_to, delay 
                    from link
                    where node_from = {id_destination} 
                    and id_scenario = {self.idScenario}
                    order by 1"""
        else:
            qry = f"""select node_to, delay 
                    from link
                    where node_from = {id_destination} 
                    and id_scenario = {self.idScenario}
                    order by 1"""
        qry = f"""select distinct node_to, b.delay 
            from link a
            left join intersection_delay b on (a.linkid = b.id_link and a.id_scenario = b.id_scenario)
            where node_from = {id_destination} 
            and a.id_scenario = {self.idScenario} and node_to != {id_origin} order by 1"""
        qry = f"""select todo.node_to, sum(delay)
            from 
            (
                select distinct node_to, b.delay 
                from link a
                left join intersection_delay b on (a.linkid = b.id_link and a.id_scenario = b.id_scenario)
                where node_from = {id_destination}
                and a.id_scenario = {self.idScenario} and node_to != {id_origin} and b.id is null
                union
                select b.id_node, b.delay 
                from link a
                join intersection_delay b on (a.linkid = b.id_link and a.id_scenario = b.id_scenario)
                where a.id_scenario = {self.idScenario} and b.id_link = '{id_origin}-{id_destination}'
                order by 1 )
            todo 
            group by 1"""

        print(qry)
        result = self.dataBaseSqlite.executeSql(qry)

        if result:
            rowsCount = len(result)
            self.tbl_turns.setRowCount(rowsCount)
            self.tbl_turns.setColumnCount(1)
            self.tbl_turns.setHorizontalHeaderLabels(header) # Headers of columns table
            self.tbl_turns.horizontalHeader().setStretchLastSection(True)

            for index, valor in enumerate(result):
                headerItem = QTableWidgetItem(valor[0])
                if valor[1]!=-1:
                    headerItem.setIcon(QIcon(self.plugin_dir+"/icons/green-light.png"))
                else:
                    headerItem.setIcon(QIcon(self.plugin_dir+"/icons/no-turn-right.png"))
                headerItem.setText(str(valor[0]))
                self.tbl_turns.setVerticalHeaderItem(index,headerItem)

            # Set columns size
            for index,value in enumerate(result):
                    data = result[index][1] if result[index][1] is not None else ''
                    self.tbl_turns.setItem(index, 0, QTableWidgetItem(str(data)))

        else:
            self.tbl_turns.clear()
            self.tbl_turns.setRowCount(0)
            self.tbl_turns.setColumnCount(0)
        return 


    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#E17E68' # orenge
        elif state == QtGui.QValidator.Invalid:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def save_new_link(self):
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        self.load_routes_list()

        if self.idScenario is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Plese Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.length is None or self.length.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Please Write Length", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.capacity is None or self.capacity.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Please Write Capacity", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if not validatorRegex(self.capacity.text(), 'real-negative'):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Field y permit only numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        name = self.name.text() if self.name.text() else ''
        description = self.description.text() if self.description.text() else ''
        delay_data = self.delay.text() if self.delay.text() else ''

        id_type = self.cb_type.itemData(self.cb_type.currentIndex())
        id_origin = self.cb_origin.itemData(self.cb_origin.currentIndex())
        id_destination = self.cb_destination.itemData(self.cb_destination.currentIndex())
        two_way = 1 if self.two_way.isChecked() else 0
        used_in_scenario = 1 if self.used_in_scenario.isChecked() else 0

        if id_origin == id_destination:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Please write another value for origin or destination", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        # Validate Link 
        if self.codeLink is None:
            result_validate = self.dataBaseSqlite.selectAll(' link ', where=f' where node_from={id_origin} and node_to={id_destination}')
            if result_validate:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Duplicated Link", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False

        rowsTurns = self.tbl_turns.rowCount()
        self.turns_delays_arr = []
        
        for index in range(0,rowsTurns):
            turn_to = self.tbl_turns.verticalHeaderItem(index).text()
            delay = self.tbl_turns.item(index, 0).text() if  self.tbl_turns.item(index, 0).text() != 'Inf' else -1
            self.turns_delays_arr.append((turn_to, delay))

        if self.codeLink is None:
            newLink = self.dataBaseSqlite.addLinkFDialog(scenarios, id_origin, id_destination, id_type, name, description, two_way, used_in_scenario, self.length.text(), self.capacity.text(), delay_data, self.id_routes_arr_selected, self.turns_delays_arr)
            if not newLink:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_() 
                return False
        else:
            newLink = self.dataBaseSqlite.updateLinkFDialog(scenarios, id_origin, id_destination, id_type, name, description, two_way, used_in_scenario, self.length.text(), self.capacity.text(), delay_data, self.id_routes_arr_selected, self.turns_delays_arr)

        if newLink is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Link", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        self.close()
        return True


    def load_routes_list(self):
        model = self.tree_routes.model()
        self.id_routes_arr_selected = []
        if model:
            count = model.rowCount()
            for value in range(0,count):
                item = model.itemFromIndex(model.index(value,0))
                # 1 passes_stop 2 passes_only 3 cannot_pass
                typeRoute = 3
                if item.data(Qt.UserRole) == 'passes_stops':
                    typeRoute = 1
                elif item.data(Qt.UserRole)=='passes_only':
                    typeRoute = 2
                idRoute = item.text().split(' ')[0]
                self.id_routes_arr_selected.append((idRoute, typeRoute))

        return True


    def load_scenarios(self):
        self.__get_scenarios_data()


    def __load_cb_type(self):
        types = self.dataBaseSqlite.selectAll(' link_type ')
        self.cb_type.clear()
        for value in types:
            self.cb_type.addItem("%s %s" % (value[0], value[1]), value[0])


    def __load_cb_ori_dest(self):
        nodes = self.dataBaseSqlite.selectAll(' node ')
        self.cb_origin.clear()
        self.cb_destination.clear()
        for value in nodes:
            self.cb_origin.addItem("%s %s" % (value[0],value[3] if value[3] else ''), value[0])
            self.cb_destination.addItem("%s %s" % (value[0],value[3] if value[3] else ''), value[0])


    def load_default_data(self):
        self.cb_origin.setEnabled(False)
        self.cb_destination.setEnabled(False)

        # Basics Data
        data = self.dataBaseSqlite.selectAll(
                ' link ', 
                f""" where linkid = '{self.codeLink}' and id_scenario = {self.idScenario} """,
                columns= "node_from, node_to, id_linktype, id, name, description, length, capacity, delay, two_way, used_in_scenario")

        if not data:
            data = self.dataBaseSqlite.selectAll(
                ' link ', 
                f""" where linkid = '{self.codeLink}' """,
                columns= "node_from, node_to, id_linktype, id, name, description, length, capacity, delay, two_way, used_in_scenario")
        

        resultOrigin = self.dataBaseSqlite.selectAll(' node ', where=f' where id = {data[0][0]}', columns='id, name')
        resultDestination = self.dataBaseSqlite.selectAll(' node ', where=f' where id = {data[0][1]}', columns='id, name')
        resultTypeLink = self.dataBaseSqlite.selectAll(' link_type ', where=f' where id = {data[0][2]}', columns='id, name')

        originText = f"{resultOrigin[0][0]} {resultOrigin[0][1]}" if resultOrigin[0][1] else f"{resultOrigin[0][0]} "
        indexOrigin = self.cb_origin.findText(originText)
        self.cb_origin.setCurrentIndex(indexOrigin)

        destinationText = f"{resultDestination[0][0]} {resultDestination[0][1]}" if resultDestination[0][1] else f"{resultDestination[0][0]} "
        indexDestination = self.cb_destination.findText(destinationText)
        self.cb_destination.setCurrentIndex(indexDestination)

        if resultTypeLink:
            indexLinkType = self.cb_type.findText(str(f'{resultTypeLink[0][0]} {resultTypeLink[0][1]}'))
            self.cb_type.setCurrentIndex(indexLinkType)

        self.name.setText(str(data[0][4] if data[0][4] else ''))
        self.description.setText(str(data[0][5] if data[0][5] else ''))

        self.length.setText(str(data[0][6] if data[0][6] else ''))
        self.capacity.setText(str(data[0][7] if data[0][7] else ''))
        self.delay.setText(str(data[0][8] if data[0][8] else ''))
       
        two_way = True if data[0][9]==1 else False 
        self.two_way.setChecked(two_way)

        used_in_scenario = True if data[0][10]==1 else False 
        self.used_in_scenario.setChecked(used_in_scenario)
        
        # Routes
        qry = f"""select distinct c.id||' '||c.name, b.type_route
                from link a
                join link_route b on (a.linkid = b.id_link)
                join route c on (b.id_route = c.id)
                where a.linkid = '{self.codeLink}' and a.id_scenario = {self.idScenario}
                order by 1"""

        result = self.dataBaseSqlite.executeSql(qry)
        self.modelRoutes.clear()
        self.modelRoutes.setHorizontalHeaderLabels(['Routes'])
        x=0
        for value in result:
            item = QtGui.QStandardItem()
            item.setIcon(self.ic_redlight)
            typeRoute = 'cannot_pass'
            if value[1] == 1:
                item.setIcon(self.ic_bus_stop)
                typeRoute = 'passes_stops'
            if value[1] == 2:
                typeRoute = 'passes_only'
                item.setIcon(self.ic_greenlight)
            
            item.setData(typeRoute,Qt.UserRole)
            item.setText(value[0])
            self.modelRoutes.insertRow(x,item)
            x+=1
        self.tree_routes.setModel(self.modelRoutes)
        self.tree_routes.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)
        

    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
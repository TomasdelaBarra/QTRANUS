# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_route.ui'))

class AddRouteDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, idScenario=None, parent = None, codeRoute=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddRouteDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeRoute = codeRoute
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.idScenario = idScenario

        # Linking objects with controls
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.id_operator = self.findChild(QtWidgets.QComboBox, 'id_operator')
        self.frequency_from = self.findChild(QtWidgets.QLineEdit, 'frequecy_from')
        self.frequency_to = self.findChild(QtWidgets.QLineEdit, 'frequency_to')
        self.max_fleet = self.findChild(QtWidgets.QLineEdit, 'max_fleet')
        self.target_occ = self.findChild(QtWidgets.QLineEdit, 'target_occ')
        self.used = self.findChild(QtWidgets.QCheckBox, 'used')
        self.follows_schedule = self.findChild(QtWidgets.QCheckBox, 'follows_schedule')

        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_route)
        
        #Loads
        self.__get_scenarios_data()
        self.__get_operators_data()
        
        if self.codeRoute is not None:
            self.load_default_data()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def save_new_route(self):
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's name.")
            return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's name.")
            return False

        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's description.")
            return False

        if self.id_operator is None or self.id_operator.currentText() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's attractor factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's code.")
            return False

        if self.frequency_from is None or self.frequency_from.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's attractor factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's code.")
            return False

        if self.frequency_to is None or self.frequency_to.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's price factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's name.")
            return False

        if self.target_occ is None or self.target_occ.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's Target Occ.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's name.")
            return False

        if self.max_fleet is None or self.max_fleet.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's price factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sustite name.")
            return False
        
        used = 1 if self.used.isChecked() else 0
        follows_schedule = 1 if self.follows_schedule.isChecked() else 0
        operator_result = self.dataBaseSqlite.selectAll(' operator ', " where name = '{}'".format(self.id_operator.currentText()))
        id_operator = operator_result[0][1]

        if self.codeRoute is None:
            newRoute = self.dataBaseSqlite.addRoute(scenarios, self.id.text(), self.name.text(), self.description.text(), id_operator, self.frequency_from.text(), self.frequency_to.text(), self.max_fleet.text(), self.target_occ.text(), used, follows_schedule)
            if not newRoute:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new route", "Warning Error while saving database route.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select other previous scenario code.")    
                return False
        else:
            newRoute = self.dataBaseSqlite.updateRoute( self.id.text(), self.name.text(), self.description.text(), id_operator, self.frequency_from.text(), self.frequency_to.text(), self.max_fleet.text(), self.target_occ.text(), used, follows_schedule)
        self.accept()

    def load_scenarios(self):
        self.__get_scenarios_data()


    def load_default_data(self):
        data = self.dataBaseSqlite.selectAll('route', ' where id = {}'.format(self.codeRoute))
        operator_result = self.dataBaseSqlite.selectAll(' operator ', " where id = {}".format(data[0][3]))
        name_operator = operator_result[0][2]
        #print("DATAAA: {}, {}".format(data, name_operator))
        self.id.setText(str(data[0][0]))
        self.name.setText(str(data[0][1]))
        self.description.setText(str(data[0][2]))
        indexIdOperator = self.id_operator.findText(name_operator, Qt.MatchFixedString)
        self.id_operator.setCurrentIndex(indexIdOperator)
        self.frequency_from.setText(str(data[0][4]))
        self.frequency_to.setText(str(data[0][5]))
        self.target_occ.setText(str(data[0][6]))
        self.max_fleet.setText(str(data[0][7]))
        used = True if data[0][8]==1 else False 
        follows_schedule = True if data[0][9]==1 else False 
        self.used.setChecked(used)
        self.follows_schedule.setChecked(follows_schedule)
        


    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()

    def __get_operators_data(self):
        result = self.dataBaseSqlite.selectAll("operator", columns="name")

        items = []
        for value in result:
            items.append(value[0])

        self.id_operator.addItems(items)
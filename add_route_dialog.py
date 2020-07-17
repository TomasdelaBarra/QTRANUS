# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QColor

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Helpers import Helpers
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'

from qgis.gui import QgsColorButton, QgsGradientColorRampDialog, QgsColorRampButton

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
        #self.project = parent.project 
        self.codeRoute = codeRoute
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.idScenario = idScenario
        self.button_color = QgsColorButton(self, 'Color')
        self.label_color = QLabel("Color") 
        
        # Linking objects with controls
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenario_tree')
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.clicked.connect(self.select_scenario)
        
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.cb_operator = self.findChild(QtWidgets.QComboBox, 'id_operator')
        self.frequency_from = self.findChild(QtWidgets.QLineEdit, 'frequecy_from')
        self.frequency_to = self.findChild(QtWidgets.QLineEdit, 'frequency_to')
        self.max_fleet = self.findChild(QtWidgets.QLineEdit, 'max_fleet')

        #self.target_occ = self.findChild(QtWidgets.QLineEdit, 'target_occ')
        self.used = self.findChild(QtWidgets.QCheckBox, 'used')
        self.follows_schedule = self.findChild(QtWidgets.QCheckBox, 'follows_schedule')
        self.layout_data = self.findChild(QtWidgets.QFormLayout, 'formLayout_data')
        self.layout_data.addRow(self.label_color, self.button_color)
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_route)
        
        # Validations
        self.id.setValidator(validatorExpr('integer'))
        self.id.textChanged.connect(self.check_state)
        """
        self.name.setValidator(validatorExpr('alphaNum'))
        self.name.textChanged.connect(self.check_state)
        self.description.setValidator(validatorExpr('alphaNum'))
        self.description.textChanged.connect(self.check_state)
        """
        self.name.setMaxLength(10)
        self.description.setMaxLength(55)

        self.frequency_from.setValidator(validatorExpr('decimal'))
        self.frequency_from.textChanged.connect(self.check_state)
        self.frequency_to.setValidator(validatorExpr('decimal'))
        self.frequency_to.textChanged.connect(self.check_state)
        self.max_fleet.setValidator(validatorExpr('decimal'))
        self.max_fleet.textChanged.connect(self.check_state)
        #self.target_occ.setValidator(validatorExpr('decimal'))
        #self.target_occ.textChanged.connect(self.check_state)
        self.changeLineEditStyle = "color: green; font-weight: bold"

        #Loads
        self.__get_scenarios_data()
        self.__get_operators_data()
        self.__loadId()
        
        if self.codeRoute:
            self.setWindowTitle("Edit Route")
            self.load_default_data()


    def __loadId(self):
        if self.codeRoute is None:
            self.id.setText(str(self.dataBaseSqlite.maxIdTable(" route "))) 

            
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


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.load_default_data()


    def save_new_route(self):
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
        
        if self.codeRoute is None and not self.dataBaseSqlite.validateId(' route ', self.id.text()):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write another route's id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write the route's description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.cb_operator is None or self.cb_operator.currentText() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please select Operator.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.frequency_from is None or self.frequency_from.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write Frequency from.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.frequency_to is None or self.frequency_to.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write Frequency to.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.button_color.isNull():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please select Color.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.max_fleet is None or self.max_fleet.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Route", "Please write Max fleet.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        
        used = 1 if self.used.isChecked() else 0
        follows_schedule = 1 if self.follows_schedule.isChecked() else 0
        id_operator = self.cb_operator.itemData(self.cb_operator.currentIndex())

        if self.codeRoute is None:
            newRoute = self.dataBaseSqlite.addRoute(scenarios, self.id.text(), self.name.text(), self.description.text(), id_operator, self.frequency_from.text(), self.frequency_to.text(), self.max_fleet.text(), self.button_color.color().rgb(), used, follows_schedule)
            if not newRoute:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new route", "Warning Error while saving database route.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
            self.accept()
        else:
            newRoute = self.dataBaseSqlite.updateRoute(scenarios, self.id.text(), self.name.text(), self.description.text(), id_operator, self.frequency_from.text(), self.frequency_to.text(), self.max_fleet.text(), self.button_color.color().rgb(), used, follows_schedule)
            self.accept()


    def load_scenarios(self):
        self.__get_scenarios_data()


    def load_default_data(self):
        
        if self.codeRoute:
            data = self.dataBaseSqlite.selectAll('route', ' where id = {} and id_scenario = {} '.format(self.codeRoute, self.idScenario))
            id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)
            operator_result = self.dataBaseSqlite.selectAll(' operator ', " where id = {} and id_scenario = {} ".format(data[0][4], self.idScenario))
            if id_prevScenario:
                data_prev = self.dataBaseSqlite.selectAll('route', ' where id = {} and id_scenario = {} '.format(self.codeRoute, id_prevScenario[0][0]))
            self.id.setText(str(data[0][0]))
            self.name.setText(str(data[0][2]))
            self.description.setText(str(data[0][3]))
            
            self.cb_operator.setCurrentText(str(operator_result[0][0])+" "+str(operator_result[0][2]))

            self.frequency_from.setText(Helpers.decimalFormat(str(data[0][5])))
            self.frequency_to.setText(Helpers.decimalFormat(str(data[0][6])))
            #self.target_occ.setText(Helpers.decimalFormat(str(data[0][7])))
            self.max_fleet.setText(Helpers.decimalFormat(str(data[0][8])))
            used = True if data[0][9]==1 else False 
            follows_schedule = True if data[0][10]==1 else False 
            self.used.setChecked(used)
            self.follows_schedule.setChecked(follows_schedule)
            
            if len(data[0]) == 12:
                if data[0][11]: 
                    qcolor = QColor()
                    qcolor.setRgb(data[0][11])
                    self.button_color.setColor(qcolor)

            if id_prevScenario and data_prev: 
                if (data[0][5] !=  data_prev[0][5]):
                    self.frequency_from.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.frequency_from.setStyleSheet("")

                if (data[0][6] !=  data_prev[0][6]):
                    self.frequency_to.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.frequency_to.setStyleSheet("")

                """if (data[0][7] !=  data_prev[0][7]):
                    self.target_occ.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.target_occ.setStyleSheet("")"""

                if (data[0][8] !=  data_prev[0][8]):
                    self.max_fleet.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.max_fleet.setStyleSheet("")
        


    def __get_scenarios_data(self):
        result_scenario = self.dataBaseSqlite.selectAll(" scenario ", where=" where id = %s " % self.idScenario )

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        itemsList = self.scenarios_model.findItems(result_scenario[0][1], Qt.MatchContains | Qt.MatchRecursive, 0)
        indexSelected = self.scenarios_model.indexFromItem(itemsList[0])
        modelSelection.setCurrentIndex(indexSelected, QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)

        self.select_scenario(self.scenario_tree.selectedIndexes()[0])

    def __get_operators_data(self):
        result = self.dataBaseSqlite.selectAll("operator", where = f" where id_scenario = {self.idScenario}")
        for value in result:
            self.cb_operator.addItem(str(value[0])+" "+str(value[2]), value[0])

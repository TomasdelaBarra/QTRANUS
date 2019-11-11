# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QIcon

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Helpers import Helpers
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .add_mode_dialog import AddModeDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_category.ui'))

class AddCategoryDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, idScenario=None, parent = None, codeCategory=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddCategoryDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeCategory = codeCategory
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder )
        self.plugin_dir = os.path.dirname(__file__)
        self.idScenario = idScenario

        # Linking objects with controls
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenario_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.volumen_travel_time = self.findChild(QtWidgets.QLineEdit, 'volumen_travel_time')
        self.value_of_waiting_time = self.findChild(QtWidgets.QLineEdit, 'value_of_waiting_time')
        self.min_trip_gener = self.findChild(QtWidgets.QLineEdit, 'min_trip_gener')
        self.max_trip_gener = self.findChild(QtWidgets.QLineEdit, 'max_trip_gener')
        self.elasticity_trip_gener = self.findChild(QtWidgets.QLineEdit, 'elasticity_trip_gener')
        self.choice_elasticity = self.findChild(QtWidgets.QLineEdit, 'choice_elasticity')
        self.mode_cb = self.findChild(QtWidgets.QComboBox, 'mode_cb')
        self.add_mode_btn = self.findChild(QtWidgets.QPushButton, 'add_mode')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_category)

        # Validations
        
        self.id.setValidator(validatorExpr('integer'))
        self.id.textChanged.connect(self.check_state)
        #self.name.setValidator(validatorExpr('alphaNum'))
        #self.name.textChanged.connect(self.check_state)
        #self.description.setValidator(validatorExpr('alphaNum'))
        #self.description.textChanged.connect(self.check_state)
        self.volumen_travel_time.setValidator(validatorExpr('decimal'))
        self.volumen_travel_time.textChanged.connect(self.check_state)
        self.value_of_waiting_time.setValidator(validatorExpr('decimal'))
        self.value_of_waiting_time.textChanged.connect(self.check_state)
        self.min_trip_gener.setValidator(validatorExpr('decimal'))
        self.min_trip_gener.textChanged.connect(self.check_state)
        self.max_trip_gener.setValidator(validatorExpr('decimal'))
        self.max_trip_gener.textChanged.connect(self.check_state)
        self.elasticity_trip_gener.setValidator(validatorExpr('decimal'))
        self.elasticity_trip_gener.textChanged.connect(self.check_state)
        self.choice_elasticity.setValidator(validatorExpr('decimal'))
        self.choice_elasticity.textChanged.connect(self.check_state)
        self.add_mode_btn.clicked.connect(self.open_add_mode)
        
        self.name.setMaxLength(10)
        self.description.setMaxLength(55)
        self.changeLineEditStyle = "color: green; font-weight: bold"

        #Loads
        self.__get_modes_data()
        self.__get_scenarios_data()
        self.__validateSave()
        self.__loadId()
        if self.codeCategory is not None:
            self.setWindowTitle("Edit Category")
            self.load_default_data()

        self.add_mode_btn.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))


    def __loadId(self):
        if self.codeCategory is None:
            self.id.setText(str(self.dataBaseSqlite.maxIdTable(" category "))) 


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        self.load_default_data()


    def __validateSave(self):
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).setEnabled(False)
        if self.dataBaseSqlite.selectAll('mode'):
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).setEnabled(True)
    

    def open_add_mode(self):
        
        dialog = AddModeDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if result:
            self.__get_modes_data()
            self.__validateSave()


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

    def save_new_category(self):
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's name.")
            return False

        if self.codeCategory is None:
            if not self.dataBaseSqlite.validateId(' category ', self.id.text()):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write another Category id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.volumen_travel_time is None or self.volumen_travel_time.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write volumen travel time.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.value_of_waiting_time is None or self.value_of_waiting_time.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write value of waiting time.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.min_trip_gener is None or self.min_trip_gener.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write Min. trip gener.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.max_trip_gener is None or self.max_trip_gener.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write Max. trip gener.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.elasticity_trip_gener is None or self.elasticity_trip_gener.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write Elasticity trip gener.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.choice_elasticity is None or self.choice_elasticity.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Category", "Please write Choice elasticity.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        id_mode = self.mode_cb.itemData(self.mode_cb.currentIndex())

        if self.codeCategory is None:
            newCategory = self.dataBaseSqlite.addCategory(scenarios, self.id.text(), id_mode, self.name.text(), self.description.text(), self.volumen_travel_time.text(), self.value_of_waiting_time.text(), self.min_trip_gener.text(), self.max_trip_gener.text(), self.elasticity_trip_gener.text(), self.choice_elasticity.text())
            if not newCategory:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()   
                return False
        else:
            newCategory = self.dataBaseSqlite.updateCategory(scenarios, self.id.text(), id_mode, self.name.text(), self.description.text(), self.volumen_travel_time.text(), self.value_of_waiting_time.text(), self.min_trip_gener.text(), self.max_trip_gener.text(), self.elasticity_trip_gener.text(), self.choice_elasticity.text())

        if newCategory is not None:
            self.parent().load_scenarios()
            self.accept()
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        return True


    def load_scenarios(self):
        self.__get_scenarios_data()


    def load_default_data(self):
        id_category = self.codeCategory
        id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)
        if id_prevScenario:
            sql = """select a.id, a.name, a.description, a.volumen_travel_time, 
                a.value_of_waiting_time, a.min_trip_gener, a.max_trip_gener, a.elasticity_trip_gener, a.choice_elasticity, b.name
                from category a
                join mode b on (a.id_mode = b.id) 
                where a.id = {} and a.id_scenario = {}""".format(id_category, id_prevScenario[0][0])

            data_prev = self.dataBaseSqlite.executeSql(sql)

        sql = """select a.id, a.name, a.description, a.volumen_travel_time, 
                a.value_of_waiting_time, a.min_trip_gener, a.max_trip_gener, a.elasticity_trip_gener, a.choice_elasticity, b.name
                from category a
                join mode b on (a.id_mode = b.id) 
                where a.id = {} and a.id_scenario = {}""".format(id_category, self.idScenario)

        data = self.dataBaseSqlite.executeSql(sql)
        
        if data and self.codeCategory:
            self.id.setText(str(data[0][0]))
            self.name.setText(str(data[0][1]))
            self.description.setText(str(data[0][2]))
            self.volumen_travel_time.setText(Helpers.decimalFormat(str(data[0][3])))
            self.value_of_waiting_time.setText(Helpers.decimalFormat(str(data[0][4])))
            self.min_trip_gener.setText(Helpers.decimalFormat(str(data[0][5])))
            self.max_trip_gener.setText(Helpers.decimalFormat(str(data[0][6])))
            self.elasticity_trip_gener.setText(Helpers.decimalFormat(str(data[0][7])))
            self.choice_elasticity.setText(Helpers.decimalFormat(str(data[0][8])))

            indexMode = self.mode_cb.findText(data[0][9], Qt.MatchFixedString)
            self.mode_cb.setCurrentIndex(indexMode)
            
            if id_prevScenario and data_prev: 
                if (data[0][1] !=  data_prev[0][1]):
                    self.name.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.name.setStyleSheet("")

                if (data[0][2] !=  data_prev[0][2]):
                    self.description.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.description.setStyleSheet("")
   
                if (data[0][3] !=  data_prev[0][3]):
                    self.volumen_travel_time.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.volumen_travel_time.setStyleSheet("")

                if (data[0][4] !=  data_prev[0][4]):
                    self.value_of_waiting_time.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.value_of_waiting_time.setStyleSheet("")

                if (data[0][5] !=  data_prev[0][5]):
                    self.min_trip_gener.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.min_trip_gener.setStyleSheet("")

                if (data[0][5] !=  data_prev[0][5]):
                    self.min_trip_gener.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.min_trip_gener.setStyleSheet("")

                if (data[0][6] !=  data_prev[0][6]):
                    self.max_trip_gener.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.max_trip_gener.setStyleSheet("")

                if (data[0][7] !=  data_prev[0][7]):
                    self.elasticity_trip_gener.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.elasticity_trip_gener.setStyleSheet("")

                if (data[0][8] !=  data_prev[0][8]):
                    self.choice_elasticity.setStyleSheet(self.changeLineEditStyle)
                else:
                    self.choice_elasticity.setStyleSheet("")
            else:
                self.name.setStyleSheet(self.changeLineEditStyle)
                self.description.setStyleSheet(self.changeLineEditStyle)
                self.volumen_travel_time.setStyleSheet(self.changeLineEditStyle)
                self.value_of_waiting_time.setStyleSheet(self.changeLineEditStyle)
                self.min_trip_gener.setStyleSheet(self.changeLineEditStyle)
                self.min_trip_gener.setStyleSheet(self.changeLineEditStyle)
                self.max_trip_gener.setStyleSheet(self.changeLineEditStyle)
                self.elasticity_trip_gener.setStyleSheet(self.changeLineEditStyle)
                self.choice_elasticity.setStyleSheet(self.changeLineEditStyle)


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


    def __get_modes_data(self):
        result = self.dataBaseSqlite.selectAll("mode")
        self.mode_cb.clear()
        for value in result:
            self.mode_cb.addItem(str(value[1]), value[0])
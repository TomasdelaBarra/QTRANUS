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
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_scenario.ui'))

class AddScenarioDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent = None, codeScenario=None, action=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddScenarioDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeScenario = codeScenario
        self.tranus_folder = tranus_folder
        self.dataBase = DataBase()
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder )
        self.action = action
        # Linking objects with controls
        self.code = self.findChild(QtWidgets.QLineEdit, 'code')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.previous = self.findChild(QtWidgets.QComboBox, 'cb_previous')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')

        # Validations
        self.code.setValidator(validatorExpr('alphaNum',limit=3))
        self.code.textChanged.connect(self.check_state)
        """self.name.setValidator(validatorExpr('any',limit=4))
        self.name.textChanged.connect(self.check_state)
        """
        self.name.setMaxLength(30)

        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_scenario)
        
        #Loads
        self.__load_scenarios_combobox()
        if self.codeScenario and self.action == 'edit':
            self.setWindowTitle("Edit Scenario")
            self.__load_default_data()
        elif self.codeScenario and self.action == 'new':
            self.setWindowTitle("Add Scenario")
            indexPrevious = self.previous.findText(self.codeScenario, Qt.MatchFixedString)
            self.previous.setCurrentIndex(indexPrevious)


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

    def save_new_scenario(self):
        if(self.code is None or self.code.text().strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's code.")
            return False

        if not self.__validate_scenario_code(self.code): 
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write another the scenario's code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please write the scenario's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the scenario's name.")
            return False
    
        previousCode = ''
        if len(self.previous) > 0:    
            if self.previous.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select a previous scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
            else:
                previousCode = (self.previous.currentText().split('-'))[0].strip()
                if self.code.text() == previousCode:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select another previous scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    return False


        old_code = None
        
        if self.action == 'new':
            newMatrix = self.dataBaseSqlite.addScenario(self.code.text(), self.name.text(), previousCode)
            if not newMatrix:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please select another scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
        else:
            if self.codeScenario != self.code.text():
                old_code = self.codeScenario
            else:
                old_code = self.code.text()
            newMatrix = self.dataBaseSqlite.updateScenario(self.code.text(), self.name.text(), previousCode, old_code=old_code)

        result  = self.dataBaseSqlite.selectAll(' scenario ', where=f" where code = '{self.code.text()}'")
        
        self.dataBaseSqlite.syncScenariosDB(result[0][0], result[0][3])
        if newMatrix is not None:
            self.parent().load_scenarios()
            self.accept()

        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new scenario", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        return True
    

    def __load_scenarios_combobox(self): 
        criteria = f""" where code != '{self.codeScenario}'""" if self.action == 'edit' else ''
        scenarios = self.dataBaseSqlite.selectAll('scenario', where=criteria)
        if scenarios is not None:
            if len(scenarios) > 0:
                for scenario in scenarios:
                    self.previous.addItem(scenario[1])

    def __load_default_data(self):
        data = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.codeScenario))     
        self.code.setText(data[0][1])
        self.name.setText(data[0][2])
        indexPrevious = self.previous.findText(data[0][3], Qt.MatchFixedString)
        self.previous.setCurrentIndex(indexPrevious)
        if data[0][3] == '':
            self.previous.clear()


    def __validate_scenario_code(self, code):
        result = self.dataBaseSqlite.selectAll('scenario', " where code = '{}' ".format(code))
        if len(result)==0:
            return True
        else:
            return False
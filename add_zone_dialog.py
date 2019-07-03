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
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_zone.ui'))

class AddZoneDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent = None, codeZone=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddZoneDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeZone = codeZone
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder )

        # Linking objects with controls
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.external = self.findChild(QtWidgets.QCheckBox, 'external')
        self.internal_cost_factor = self.findChild(QtWidgets.QLineEdit, 'internal_cost_factor')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.external.clicked.connect(self.evaluate_external)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_zone)


        # Validations
        self.id.setValidator(validatorExpr('integer'))
        self.id.textChanged.connect(self.check_state)
        self.name.setValidator(validatorExpr('alphaNum'))
        self.name.textChanged.connect(self.check_state)
        self.internal_cost_factor.setValidator(validatorExpr('decimal'))
        self.internal_cost_factor.textChanged.connect(self.check_state)


        #Loads
        self.__get_scenarios_data()
        self.evaluate_external()
        if self.codeZone is not None:
            self.load_default_data()


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

    def evaluate_external(self):
        """
            @summary: Enable or disable Internal Cost Factor LineEdit
        """
        if self.external.isChecked():
            self.internal_cost_factor.setEnabled(False)
            if not self.codeZone:
                self.internal_cost_factor.setText('')
        else:
            self.internal_cost_factor.setEnabled(True)
            if not self.codeZone:
                self.internal_cost_factor.setText('')

    def save_new_zone(self):

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Zone", "Please write the zone id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Zone", "Please write the zone name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        external = 1 if self.external.isChecked() else 0

        if self.internal_cost_factor.text().strip() == '' and external == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Zone", "Please write the Internal cost factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.codeZone is None:
            newZone = self.dataBaseSqlite.addZone(self.id.text(), self.name.text(), external, self.internal_cost_factor.text())
            if not newZone:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Zone", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select other previous scenario code.")    
                return False
        else:
            newZone = self.dataBaseSqlite.updateZone(self.codeZone, self.name.text(), external, self.internal_cost_factor.text())

        if newZone is not None:
            self.parent().load_scenarios()
            self.accept()
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Zone", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's description.")
            return False
        return True


    def load_scenarios(self):
        self.__get_scenarios_data()


    def load_default_data(self):
        data = self.dataBaseSqlite.selectAll('zone', ' where id = {}'.format(self.codeZone))
        """print(self.codeZone)"""
        print(data[0][3])
        self.id.setText(str(data[0][0]))
        self.name.setText(str(data[0][1]))
        externalVal = True if data[0][2]==1 else False 
        self.external.setChecked(externalVal)
        internal_cost_factor = str(data[0][3]) if data[0][3] is not None else ''
        self.internal_cost_factor.setText(internal_cost_factor)
        self.evaluate_external()


    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
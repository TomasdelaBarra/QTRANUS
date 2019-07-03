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
    os.path.dirname(__file__), 'add_sector.ui'))

class AddSectorDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent=None, codeSector=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddSectorDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeSector = codeSector
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)

        # Linking objects with controls
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.transportable = self.findChild(QtWidgets.QCheckBox, 'transportable')
        self.price_factor = self.findChild(QtWidgets.QLineEdit, 'price_factor')
        self.attractor_factor = self.findChild(QtWidgets.QLineEdit, 'attractor_factor')
        self.location_choice_elasticity = self.findChild(QtWidgets.QLineEdit, 'location_choice_elasticity')
        self.sustitute = self.findChild(QtWidgets.QLineEdit, 'sustitute')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenario_tree')

        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_sector)
        self.transportable.clicked.connect(self.evaluate_transportable)

        # Validations
        self.id.setValidator(validatorExpr('integer'))
        self.id.textChanged.connect(self.check_state)
        self.name.setValidator(validatorExpr('alphaNum'))
        self.name.textChanged.connect(self.check_state)
        self.description.setValidator(validatorExpr('alphaNum'))
        self.description.textChanged.connect(self.check_state)
        self.price_factor.setValidator(validatorExpr('decimal'))
        self.price_factor.textChanged.connect(self.check_state)
        self.attractor_factor.setValidator(validatorExpr('decimal'))
        self.attractor_factor.textChanged.connect(self.check_state)
        self.location_choice_elasticity.setValidator(validatorExpr('decimal'))
        self.location_choice_elasticity.textChanged.connect(self.check_state)
        self.sustitute.setValidator(validatorExpr('decimal'))
        self.sustitute.textChanged.connect(self.check_state)

        #Loads
        self.__get_scenarios_data()
        self.evaluate_transportable()
        if self.codeSector is not None:
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


    def evaluate_transportable(self):
        """
            @summary: Enable or disable location choice elasticity LineEdit
        """
        if self.transportable.isChecked():
            self.location_choice_elasticity.setEnabled(True)
            if not self.codeSector:
                self.location_choice_elasticity.setText('')
        else:
            self.location_choice_elasticity.setEnabled(False)
            if not self.codeSector:
                self.location_choice_elasticity.setText('')


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def save_new_sector(self):

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write the sector's id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.codeSector is None:
            if not self.dataBaseSqlite.validateId(' sector ', self.id.text()):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write other sector id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write the sector's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write the sector's description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if  self.transportable.isChecked() and self.location_choice_elasticity.text().strip()=='':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write Location Choice elasticity.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.attractor_factor is None or self.attractor_factor.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write the sector's attractor factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        
        if self.price_factor is None or self.price_factor.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write the sector's price factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.sustitute is None or self.sustitute.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please write Sustitute.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        transportable = 1 if self.transportable.isChecked() else 0        

        if self.codeSector is None:
            newSector = self.dataBaseSqlite.addSector(self.id.text(), self.name.text(), self.description.text(), transportable, self.location_choice_elasticity.text(), self.attractor_factor.text(), self.price_factor.text(), self.sustitute.text())
            if not newSector:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select other previous scenario code.")    
                return False
        else:
            newSector = self.dataBaseSqlite.updateSector(self.id.text(), self.name.text(), self.description.text(), transportable, self.location_choice_elasticity.text(), self.attractor_factor.text(), self.price_factor.text(), self.sustitute.text())

        if newSector is not None:
            self.parent().load_scenarios()
            self.accept()
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new sector", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please write the sector's description.")
            return False
        return True


    def load_scenarios(self):
        self.__get_scenarios_data()


    def load_default_data(self):
        data = self.dataBaseSqlite.selectAll('sector', ' where id = {}'.format(self.codeSector))
        self.id.setText(str(data[0][0]))
        self.name.setText(str(data[0][1]))
        self.description.setText(str(data[0][2]))
        transporableValue = True if data[0][3]==1 else False 
        self.transportable.setChecked(transporableValue)
        self.location_choice_elasticity.setText(str('' if data[0][4] is None else data[0][4]))
        self.attractor_factor.setText(str(data[0][5]))
        self.price_factor.setText(str(data[0][6]))
        self.sustitute.setText(str(data[0][7]))
        self.evaluate_transportable()


    def __get_scenarios_data(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenarios'])
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
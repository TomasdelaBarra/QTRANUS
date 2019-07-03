# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .add_scenario_dialog import AddScenarioDialog
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'configuration.ui'))

class ConfigurationDialog(QtWidgets.QDialog, FORM_CLASS):

	def __init__(self, tranus_folder, parent = None):
		"""
			@summary: Class constructor
			@param parent: Class that contains project information
		"""
		super(ConfigurationDialog, self).__init__(parent)
		self.setupUi(self)
		self.dataProject = None
		self.tranus_folder = tranus_folder
		self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
		objValidatorRange = QtGui.QDoubleValidator(self)
		objValidatorRange.setRange(0, 1000.0, 2)

		self.projectName = self.findChild(QtWidgets.QLineEdit, 'name')
		self.projectDescription = self.findChild(QtWidgets.QLineEdit, 'description')
		self.projectAuthor = self.findChild(QtWidgets.QLineEdit, 'author')

		self.projectTransIter = self.findChild(QtWidgets.QLineEdit, 'trans_iterations')
		self.projectTransConver = self.findChild(QtWidgets.QLineEdit, 'trans_convergence')
		self.projectTransSmoothingFact = self.findChild(QtWidgets.QLineEdit, 'trans_smoothing_factor')
		self.projectTransRouteSimil = self.findChild(QtWidgets.QLineEdit, 'trans_route_similarity')

		self.projectLandUseIter = self.findChild(QtWidgets.QLineEdit, 'land_iterations')
		self.projectLandUseConver = self.findChild(QtWidgets.QLineEdit, 'land_convergence')
		self.projectLandUseSmoothingFact = self.findChild(QtWidgets.QLineEdit, 'land_smoothing_factor')

		self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
		self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_scenario)
		self.load_deafult_data()
		
		#Validations Alpha Numeric
		self.projectName.setValidator(validatorExpr('alphaNum',limit=3))
		self.projectName.textChanged.connect(self.check_state)
		self.projectDescription.setValidator(validatorExpr('alphaNum'))
		self.projectDescription.textChanged.connect(self.check_state)
		self.projectAuthor.setValidator(validatorExpr('alphaNum'))
		self.projectAuthor.textChanged.connect(self.check_state)

		# Validations Double Fields
		self.projectTransIter.setValidator(validatorExpr('decimal'))
		self.projectTransIter.textChanged.connect(self.check_state)
		self.projectTransConver.setValidator(validatorExpr('decimal'))
		self.projectTransConver.textChanged.connect(self.check_state)
		self.projectTransSmoothingFact.setValidator(validatorExpr('decimal'))
		self.projectTransSmoothingFact.textChanged.connect(self.check_state)
		self.projectTransRouteSimil.setValidator(validatorExpr('decimal'))
		self.projectTransRouteSimil.textChanged.connect(self.check_state)

		# Validations Double Fields
		self.projectLandUseIter.setValidator(validatorExpr('decimal'))
		self.projectLandUseIter.textChanged.connect(self.check_state)
		self.projectLandUseConver.setValidator(validatorExpr('decimal'))
		self.projectLandUseConver.textChanged.connect(self.check_state)
		self.projectLandUseSmoothingFact.setValidator(validatorExpr('decimal'))
		self.projectLandUseSmoothingFact.textChanged.connect(self.check_state)


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


	def save_new_scenario(self):

		if len(self.projectName.text())>3:
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's name with max three characters.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's code.")
			return False

		if self.projectName is None or self.projectName.text().strip() == '' or (len(self.projectName.text())>3):
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's code.")
			return False

		if self.projectDescription is None or self.projectDescription.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's name.")
			return False
		    
		if self.projectAuthor is None or self.projectAuthor.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's author.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's description.")
			return False

		if self.projectTransIter is None or self.projectTransIter.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Transport Iterations.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's iter.")
			return False

		if self.projectTransConver is None or self.projectTransConver.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Transport Convergence.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's convergence.")
			return False
		    
		if self.projectTransSmoothingFact is None or self.projectTransSmoothingFact.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Transport Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's Smoothing factor.")
			return False

		if self.projectTransRouteSimil is None or self.projectTransRouteSimil.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Transport Route similarity.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's route similarity.")
			return False

		if self.projectLandUseIter is None or self.projectLandUseIter.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Land use Iterations.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's iter.")
			return False

		if self.projectLandUseConver is None or self.projectLandUseConver.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Land use Convergence.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's convergence.")
			return False

		if self.projectLandUseSmoothingFact is None or self.projectLandUseSmoothingFact.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Land use Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			print("Please write the project's Smoothing factor.")
			return False

		transport = dict(type='transport', iterations=self.projectTransIter.text(), convergence=self.projectTransConver.text(), smoothing_factor=self.projectTransSmoothingFact.text(), route_similarity_factor=self.projectTransRouteSimil.text())
		landUse = dict(type='landuse', iterations=self.projectLandUseIter.text(), convergence=self.projectLandUseConver.text(), smoothing_factor=self.projectLandUseSmoothingFact.text())
		configMode = [transport, landUse]

		if self.dataProject:
			result = self.dataBaseSqlite.updateProjectConfig(self.projectName.text(), self.projectDescription.text(), self.projectAuthor.text(), configMode)
		else:
			result = self.dataBaseSqlite.addProjectConfig(self.projectName.text(), self.projectDescription.text(), self.projectAuthor.text(), configMode)

		if result:
			self.accept()
		else:
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the project's Land use Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

	def load_deafult_data(self):
		self.dataProject = self.dataBaseSqlite.selectAll('project')

		if self.dataProject:
			result = self.dataProject
			result_model_trans = self.dataBaseSqlite.selectAll('config_model',"where type='transport'")
			result_model_landuse = self.dataBaseSqlite.selectAll('config_model',"where type='landuse'")
			self.projectName.setText(result[0][1])
			self.projectDescription.setText(result[0][2])
			self.projectAuthor.setText(result[0][3])

			self.projectTransIter.setText(str(result_model_trans[0][2]))
			self.projectTransConver.setText(str(result_model_trans[0][3]))
			self.projectTransSmoothingFact.setText(str(result_model_trans[0][4]))
			self.projectTransRouteSimil.setText(str(result_model_trans[0][5]))

			self.projectLandUseIter.setText(str(result_model_landuse[0][2]))
			self.projectLandUseConver.setText(str(result_model_landuse[0][3]))
			self.projectLandUseSmoothingFact.setText(str(result_model_landuse[0][4]))
			
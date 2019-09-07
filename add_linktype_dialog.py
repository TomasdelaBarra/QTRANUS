# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np
from string import *

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
from .classes.general.Validators import validatorRegex

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_linktype.ui'))

class AddLinkTypeDialog(QtWidgets.QDialog, FORM_CLASS):

	def __init__(self, tranus_folder, idScenario=None, linkTypeSelected=None, parent = None):
		"""
			@summary: Class constructor
			@param parent: Class that contains project information
		"""
		super(AddLinkTypeDialog, self).__init__(parent)
		self.setupUi(self)
		self.dataProject = None
		self.tranus_folder = tranus_folder
		self.plugin_dir = os.path.dirname(__file__)
		self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
		self.model = QtGui.QStandardItemModel()
		self.idScenario = idScenario

		self.header = ['Speed', 'Charges', 'Penaliz.', 'Distance Cost', 'Equiv Vehicules', 'Overlap Factor', 'Marg. Maint. Cost']
		self.columnLinkTypeDb = ['speed', 'charges', 'penaliz', 'distance_cost', 'equiv_vahicules', 'overlap_factor', 'margin_maint_cost']
		self.vertical_header_operator = []
		self.linkTypeSelected = linkTypeSelected
		self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
		self.scenario_tree.clicked.connect(self.select_scenario)
		# Definition Section
		self.id = self.findChild(QtWidgets.QLineEdit, 'id')
		self.name = self.findChild(QtWidgets.QLineEdit, 'name')
		self.description = self.findChild(QtWidgets.QLineEdit, 'description')
		self.cb_administrator = self.findChild(QtWidgets.QComboBox, 'id_administrator')
		
		# Basics Section
		self.capacity_factor = self.findChild(QtWidgets.QLineEdit, 'capacity_factor')
		self.min_maintenance_cost = self.findChild(QtWidgets.QLineEdit, 'min_maintenance_cost')
		self.porc_speed_reduction = self.findChild(QtWidgets.QLineEdit, 'porc_speed_reduction')
		self.porc_max_speed_reduction = self.findChild(QtWidgets.QLineEdit, 'porc_max_speed_reduction')
		self.vc_max_reduction = self.findChild(QtWidgets.QLineEdit, 'vc_max_reduction')

		# Operator Data Section
		self.operator_table = self.findChild(QtWidgets.QTableWidget, 'operator_table')

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

		self.capacity_factor.setValidator(validatorExpr('decimal'))
		self.capacity_factor.textChanged.connect(self.check_state)
		self.min_maintenance_cost.setValidator(validatorExpr('decimal'))
		self.min_maintenance_cost.textChanged.connect(self.check_state)
		self.porc_speed_reduction.setValidator(validatorExpr('decimal'))
		self.porc_speed_reduction.textChanged.connect(self.check_state)
		self.porc_max_speed_reduction.setValidator(validatorExpr('decimal'))
		self.porc_max_speed_reduction.textChanged.connect(self.check_state)
		self.vc_max_reduction.setValidator(validatorExpr('decimal'))
		self.vc_max_reduction.textChanged.connect(self.check_state)

		self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
		#self.operator_table.itemChanged.connect(self.__update_operator_linktype)
		
		self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_linktype)
		self.__load_fields()
		self.__get_scenarios_data()

		if self.linkTypeSelected:
			self.setWindowTitle("Edit Link Type")
			self.load_default_data()

		self.operator_table.itemChanged.connect(self.__validate_operators)


	def select_scenario(self, selectedIndex):
		"""
		    @summary: Set Scenario selected
		"""
		self.scenarioSelectedIndex = selectedIndex
		self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
		scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
		self.idScenario = scenarioData[0][0]
		self.load_default_data()


	def __validate_operators(self, item):
		if item.text()!=None and item.text()!='':
			column = item.column()
			item_value = item.text()
			row = item.row()
			result = validatorRegex(item_value, 'real')
			if not result:
				messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
				messagebox.exec_()
				self.operator_table.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))
			else:
				self.__update_operator_linktype



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


	def save_new_linktype(self):
		id_scenario = self.idScenario
		scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
		scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
		if self.id is None or self.id.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.linkTypeSelected is None:
			if self.dataBaseSqlite.validateId('link_type', self.id.text()) is False:
				messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write an id valid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
				messagebox.exec_()
				return False

		if self.name is None or self.name.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write a name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
		    
		if self.description is None or self.description.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write a description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.cb_administrator is None or self.cb_administrator.currentText().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write the operator's Author.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.capacity_factor is None or self.capacity_factor.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write Capacity factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
		    
		if self.min_maintenance_cost is None or self.min_maintenance_cost.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write Min. maintenance cost.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.porc_speed_reduction is None or self.porc_speed_reduction.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write Speed reduction.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.porc_max_speed_reduction is None or self.porc_max_speed_reduction.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write Max. Speed reduction.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.vc_max_reduction is None or self.vc_max_reduction.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Link Type", "Please write VC max. reduction.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		id_administrator = self.cb_administrator.itemData(self.cb_administrator.currentIndex())

		if self.linkTypeSelected is None:
			result = self.dataBaseSqlite.addLinkType(scenarios, self.id.text(), self.name.text(), self.description.text(), id_administrator, self.capacity_factor.text(), self.min_maintenance_cost.text(), self.porc_speed_reduction.text(), self.porc_max_speed_reduction.text(), self.vc_max_reduction.text())
		else:
			result = self.dataBaseSqlite.updateLinkType(scenarios, self.id.text(), self.name.text(), self.description.text(), id_administrator, self.capacity_factor.text(), self.min_maintenance_cost.text(), self.porc_speed_reduction.text(), self.porc_max_speed_reduction.text(), self.vc_max_reduction.text())
		# Save Operator Data Table
		operatorTable = self.operator_table.rowCount()
	
		for index in range(0, operatorTable):
			id_operator = self.operator_table.verticalHeaderItem(index).text().split(" ")[0] 
			id_linktype = self.id.text()
			speed = self.operator_table.item(index, 0).text()
			charges = self.operator_table.item(index, 1).text()
			penaliz = self.operator_table.item(index, 2).text()
			distance_cost = self.operator_table.item(index, 3).text()
			equiv_vahicules = self.operator_table.item(index, 4).text()
			overlap_factor = self.operator_table.item(index, 5).text()
			margin_maint_cost = self.operator_table.item(index, 6).text()
			self.dataBaseSqlite.addLinkTypeOperator(scenarios, id_operator, id_linktype, speed, charges, penaliz, distance_cost, equiv_vahicules, overlap_factor, margin_maint_cost )

		if result:
			self.accept()
		else:
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the operator's Land use Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False


	def __update_operator_linktype(self,item):
		
		if item.text()!=None and item.text()!='' and self.id.text()!='':
			column = item.column()
			item_value = item.text()
			row = item.row()

			id_linktype = self.id.text()
			dataColumn = self.columnLinkTypeDb[column]
			operator_name = self.vertical_header_operator[row]
			id_operator = operator_name.split(" ")[0]
			id_scenario = self.idScenario
			ifExist = self.dataBaseSqlite.selectAll('link_type_operator', " where id_linktype = {} and id_operator = {} ".format(id_linktype, id_operator))
			
			if len(ifExist) == 0:
				if not self.dataBaseSqlite.addLinkTypeOperator(scenarios, id_linktype, id_operator, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()
			else: 
				if not self.dataBaseSqlite.updateLinkTypeOperator(scenarios, id_linktype, id_operator, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add  new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()


	def load_default_data(self):
		linktype_result = self.dataBaseSqlite.selectAll(' link_type ', " where id = {} and id_scenario = {}".format(self.linkTypeSelected, self.idScenario))
		
		self.id.setText(str(linktype_result[0][0]))
		self.name.setText(str(linktype_result[0][2]))
		self.description.setText(str(linktype_result[0][3]))
		
		nameAdministrator = self.dataBaseSqlite.selectAll(' administrator ', ' where id = {}'.format(linktype_result[0][4]))[0][2]
		indexAdministrator = self.cb_administrator.findText(nameAdministrator, Qt.MatchFixedString)
		self.cb_administrator.setCurrentIndex(indexAdministrator)

		self.capacity_factor.setText(str(linktype_result[0][5]))
		self.min_maintenance_cost.setText(str(linktype_result[0][6]))
		self.porc_speed_reduction.setText(str(linktype_result[0][7]))
		self.porc_max_speed_reduction.setText(str(linktype_result[0][8]))
		self.vc_max_reduction.setText(str(linktype_result[0][9]))
		

	def __load_fields(self):
		
		administrator_result = self.dataBaseSqlite.selectAll(' administrator ', where=f" where id_scenario = {self.idScenario}")
		for value in administrator_result:
			self.id_administrator.addItem(value[2], value[0])

		# Table data
		if self.linkTypeSelected:
			sql = """select a.id||' '||a.name, b.speed, b.charges, b.penaliz, b.distance_cost,
					  b.equiv_vahicules, b.overlap_factor, b.margin_maint_cost 
				 	from 
					operator a
					left join link_type_operator b on a.id = b.id_operator
					where b.id_linktype = {} """.format(self.linkTypeSelected)
			existOperatorLinkType = self.dataBaseSqlite.executeSql(sql)
		else:
			existOperatorLinkType = []	

		if self.linkTypeSelected and len(existOperatorLinkType) > 0:
			sql = """
				WITH operator_base as (
						SELECT id, name, id_scenario from operator
					),
					link_type_data as (
						select a.id, a.id||' '||a.name as name, b.speed, b.charges, b.penaliz, b.distance_cost,
						b.equiv_vahicules, b.overlap_factor, b.margin_maint_cost, a.id_scenario
						from 
						operator a
						left join link_type_operator b on (a.id = b.id_operator) and (a.id_scenario = b.id_scenario)
						where b.id_linktype = {0} and a.id_scenario = {1}
					)
					select case WHEN b.name is null then a.id||' '||a.name else b.name end name, b.speed, b.charges, b.penaliz, 
						b.distance_cost, b.equiv_vahicules, b.overlap_factor, b.margin_maint_cost
					from 
						operator_base a
					left join link_type_data b on a.id = b.id and a.id_scenario = b.id_scenario 
					WHERE a.id_scenario = {1}
					""".format(self.linkTypeSelected, self.idScenario)
		else:
			sql = """select a.id||' '||a.name, '' speed, '' charges, '' penaliz, '' distance_cost,
					 '' equiv_vahicules, '' overlap_factor, '' margin_maint_cost 
				 	from
				 		operator a 
				 	where id_scenario = %s
					""" % (self.idScenario)
		
		result_ope = self.dataBaseSqlite.executeSql(sql)
		
		rowsCount = len(result_ope)
		columsCount = len(result_ope[0])-1
		self.operator_table.setRowCount(rowsCount)
		self.operator_table.setColumnCount(columsCount)
		self.operator_table.setHorizontalHeaderLabels(self.header) # Headers of columns table
		
		for index, valor in enumerate(result_ope):
			self.vertical_header_operator.append(valor[0])
			headerItem = QTableWidgetItem(valor[0])
			headerItem.setIcon(QIcon(self.plugin_dir+"/icons/category.jpg"))
			self.operator_table.setVerticalHeaderItem(index,headerItem)

		# Set columns size
		for indice,valor in enumerate(result_ope):
			x = 0
			for z in range(1,len(valor)):
				data = result_ope[indice][z] if result_ope[indice][z] is not None else ''
				self.operator_table.setItem(indice, x, QTableWidgetItem(str(data)))
				x+=1


	def __get_scenarios_data(self):
		model = QtGui.QStandardItemModel()
		model.setHorizontalHeaderLabels(['Scenarios'])

		self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
		self.scenario_tree.setModel(self.scenarios_model)
		self.scenario_tree.expandAll()

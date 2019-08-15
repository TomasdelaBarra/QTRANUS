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
from .classes.general.Validators import validatorExpr  # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .classes.general.Validators import validatorRegex


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_operator.ui'))

class AddOperatorDialog(QtWidgets.QDialog, FORM_CLASS):

	def __init__(self, tranus_folder, codeOperator=None, idScenario=None, parent = None):
		"""
			@summary: Class constructor
			@param parent: Class that contains project information
		"""
		super(AddOperatorDialog, self).__init__(parent)
		self.setupUi(self)
		self.dataProject = None
		self.tranus_folder = tranus_folder
		self.plugin_dir = os.path.dirname(__file__)
		self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
		self.model = QtGui.QStandardItemModel()
		self.header = ['Tariff Factor', 'Penal Factor']
		self.columnOperatorCetegoryDb = ['tariff_factor', 'penal_factor']
		self.vertical_header_cat = []
		self.operatorSelected = codeOperator
		self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
		self.idScenario = idScenario

		# Definition Section
		self.id = self.findChild(QtWidgets.QLineEdit, 'id')
		self.name = self.findChild(QtWidgets.QLineEdit, 'name')
		self.description = self.findChild(QtWidgets.QLineEdit, 'description')
		self.cb_mode = self.findChild(QtWidgets.QComboBox, 'cb_mode')
		self.cb_type = self.findChild(QtWidgets.QComboBox, 'cb_type')

		# Basics Section
		self.basics_modal_constant = self.findChild(QtWidgets.QLineEdit, 'basics_modal_constant')
		#self.basics_path_asc = self.findChild(QtWidgets.QLineEdit, 'basics_path_asc')
		self.basics_occupency = self.findChild(QtWidgets.QLineEdit, 'basics_occupency')
		self.basics_time_factor = self.findChild(QtWidgets.QLineEdit, 'basics_time_factor')
		self.basics_fixed_wating_factor = self.findChild(QtWidgets.QLineEdit, 'basics_fixed_wating_factor')
		self.basics_boarding_tariff = self.findChild(QtWidgets.QLineEdit, 'basics_boarding_tariff')
		self.basics_distance_tariff = self.findChild(QtWidgets.QLineEdit, 'basics_distance_tariff')
		self.basics_time_tariff = self.findChild(QtWidgets.QLineEdit, 'basics_time_tariff')

		# By Category Section
		self.by_category_tbl = self.findChild(QtWidgets.QTableWidget, 'by_category_table')
		
		# Energy Section
		self.energy_min = self.findChild(QtWidgets.QLineEdit, 'energy_min')
		self.energy_max = self.findChild(QtWidgets.QLineEdit, 'energy_max')
		self.energy_slope = self.findChild(QtWidgets.QLineEdit, 'energy_slope')
		self.energy_cost = self.findChild(QtWidgets.QLineEdit, 'energy_cost')

		# Cost Section
		self.cost_time_operation = self.findChild(QtWidgets.QLineEdit, 'cost_time_operation')
		self.cost_porc_paid_by_user = self.findChild(QtWidgets.QLineEdit, 'cost_porc_paid_by_user')

		# Stops Section
		self.stops_min_stop_time = self.findChild(QtWidgets.QLineEdit, 'stops_min_stop_time')
		self.stops_unit_boarding_time = self.findChild(QtWidgets.QLineEdit, 'stops_unit_boarding_time')
		self.stops_unit_alight_time = self.findChild(QtWidgets.QLineEdit, 'stops_unit_alight_time')

		self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
		self.by_category_tbl.itemChanged.connect(self.__update_category)
		
		# Validations
		self.id.setValidator(validatorExpr('integer'))
		self.id.textChanged.connect(self.check_state)
		
		self.name.setMaxLength(10)
		self.description.setMaxLength(55)

		self.basics_modal_constant.setValidator(validatorExpr('decimal'))
		self.basics_modal_constant.textChanged.connect(self.check_state)
		"""self.basics_path_asc.setValidator(validatorExpr('decimal'))
		self.basics_path_asc.textChanged.connect(self.check_state)"""
		self.basics_occupency.setValidator(validatorExpr('decimal'))
		self.basics_occupency.textChanged.connect(self.check_state)
		self.basics_time_factor.setValidator(validatorExpr('decimal'))
		self.basics_time_factor.textChanged.connect(self.check_state)
		self.basics_fixed_wating_factor.setValidator(validatorExpr('decimal'))
		self.basics_fixed_wating_factor.textChanged.connect(self.check_state)
		self.basics_boarding_tariff.setValidator(validatorExpr('decimal'))
		self.basics_boarding_tariff.textChanged.connect(self.check_state)
		self.basics_distance_tariff.setValidator(validatorExpr('decimal'))
		self.basics_distance_tariff.textChanged.connect(self.check_state)
		self.basics_time_tariff.setValidator(validatorExpr('decimal'))
		self.basics_time_tariff.textChanged.connect(self.check_state)

		self.energy_min.setValidator(validatorExpr('decimal'))
		self.energy_min.textChanged.connect(self.check_state)
		self.energy_max.setValidator(validatorExpr('decimal'))
		self.energy_max.textChanged.connect(self.check_state)
		self.energy_slope.setValidator(validatorExpr('decimal'))
		self.energy_slope.textChanged.connect(self.check_state)
		self.energy_cost.setValidator(validatorExpr('decimal'))
		self.energy_cost.textChanged.connect(self.check_state)

		self.cost_time_operation.setValidator(validatorExpr('decimal'))
		self.cost_time_operation.textChanged.connect(self.check_state)
		self.cost_porc_paid_by_user.setValidator(validatorExpr('decimal'))
		self.cost_porc_paid_by_user.textChanged.connect(self.check_state)

		self.stops_min_stop_time.setValidator(validatorExpr('decimal'))
		self.stops_min_stop_time.textChanged.connect(self.check_state)
		self.stops_unit_boarding_time.setValidator(validatorExpr('decimal'))
		self.stops_unit_boarding_time.textChanged.connect(self.check_state)
		self.stops_unit_alight_time.setValidator(validatorExpr('decimal'))
		self.stops_unit_alight_time.textChanged.connect(self.check_state)

		self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_operator)
		self.__load_fields()
		self.__get_scenarios_data()

		if self.operatorSelected:
			self.setWindowTitle("Edit Operator")
			self.load_default_data()
		self.by_category_tbl.itemChanged.connect(self.__validate_category)	


	def __validate_category(self, item):
		if item.text()!=None and item.text()!='':
			column = item.column()
			item_value = item.text()
			row = item.row()
			result = validatorRegex(item_value, 'real')
			if not result:
				messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Warning", "Only Numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
				messagebox.exec_()
				self.by_category_tbl.setItem(item.row(),  item.column(), QTableWidgetItem(str('')))



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

	def save_new_operator(self):

		id_type = self.cb_type.itemData(self.cb_type.currentIndex())
		id_scenario = self.idScenario
		scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
		scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)

		if self.id is None or self.id.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.dataBaseSqlite.validateId('operator', self.id.text()) is False and self.operatorSelected is None:
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write an id valid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.name is None or self.name.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
		    
		if self.description is None or self.description.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.cb_mode is None or self.cb_mode.currentText().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Author.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.cb_type is None or self.cb_type.currentText().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Transport Convergence.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
		    
		if self.basics_modal_constant is None or self.basics_modal_constant.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Modal constant.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.basics_occupency is None or self.basics_occupency.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Occupancy.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.basics_time_factor is None or self.basics_time_factor.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Time factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.basics_fixed_wating_factor is None or self.basics_fixed_wating_factor.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the Fixed wating factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.basics_boarding_tariff is None or self.basics_boarding_tariff.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Boarding tariff.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.basics_distance_tariff is None or self.basics_distance_tariff.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Distance tariff.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.basics_time_tariff is None or self.basics_time_tariff.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Time tariff.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.energy_min is None or self.energy_min.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Energy min.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.energy_max is None or self.energy_max.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Energy Max.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.energy_slope is None or self.energy_slope.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Energy slope.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.energy_cost is None or self.energy_cost.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Energy cost.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.cost_time_operation is None or self.cost_time_operation.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Time operation.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.cost_porc_paid_by_user is None or self.cost_porc_paid_by_user.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Perc. paid by user.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.stops_min_stop_time is None or self.stops_min_stop_time.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Min stop time.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.stops_unit_boarding_time is None or self.stops_unit_boarding_time.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Unit boarding time.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.stops_unit_alight_time is None or self.stops_unit_alight_time.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write Unit alight time.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
		
		id_mode = self.cb_mode.itemData(self.cb_mode.currentIndex())

		data = dict(id=self.id.text(), name=self.name.text(), description=self.description.text(), id_mode=id_mode, 
			   type=id_type, basics_modal_constant=self.basics_modal_constant.text(), basics_occupency=self.basics_occupency.text(),
			   basics_time_factor=self.basics_time_factor.text(), basics_fixed_wating_factor=self.basics_fixed_wating_factor.text(), 
			   basics_boarding_tariff=self.basics_boarding_tariff.text(),  basics_distance_tariff=self.basics_distance_tariff.text(), 
			   basics_time_tariff=self.basics_time_tariff.text(), energy_min = self.energy_min.text(), 
			   energy_max=self.energy_max.text(), energy_slope = self.energy_slope.text(), energy_cost=self.energy_cost.text(),
			   cost_time_operation=self.cost_time_operation.text(),cost_porc_paid_by_user=self.cost_porc_paid_by_user.text(), 
			   stops_min_stop_time=self.stops_min_stop_time.text(),stops_unit_boarding_time=self.stops_unit_boarding_time.text(), 
			   stops_unit_alight_time=self.stops_unit_alight_time.text()
			   )
		
		if self.operatorSelected:
			result = self.dataBaseSqlite.updateOperator(data)
		else:
			data.update(scenarios=scenarios)
			result = self.dataBaseSqlite.addOperator(data)

		if result:
			self.accept()
		else:
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the operator's Land use Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False


	def __update_category(self,item):
		
		if item.text()!=None and item.text()!='' and self.id.text()!='':
			column = item.column()
			item_value = item.text()
			row = item.row()

			id_operator = self.id.text()
			dataColumn = self.columnOperatorCetegoryDb[column]
			category_name = self.vertical_header_cat[row]
			id_category = self.dataBaseSqlite.selectAll('category', " where name = '"+str(category_name)+"'")
			id_category = id_category[0][0]

			ifExist = self.dataBaseSqlite.selectAll('operator_category', " where id_operator = {} and id_category = {} ".format(id_operator, id_category))
			
			if len(ifExist) == 0:
				if not self.dataBaseSqlite.addOperatorCategory(id_operator, id_category, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()
			else: 
				if not self.dataBaseSqlite.updateOperatorCategory(id_operator, id_category, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add  new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()


	def load_default_data(self):
		operator_result = self.dataBaseSqlite.selectAll(' operator ', " where id = {}".format(self.operatorSelected))
		
		types = ['Normal', 'Transit','Transit with Routes','Non Motorized']
		self.cb_type.clear()
		for index, valor in enumerate(types):
			self.cb_type.addItem(valor, index+1)
		
		mode_result = self.dataBaseSqlite.selectAll(' mode ')
		self.cb_mode.clear()
		for value in mode_result:
			self.cb_mode.addItem(value[1], value[0])

		sql = """ select a.name category, b.tariff_factor, b.penal_factor 
				from category a 
				left join operator_category b on (a.id = b.id)
				where b.id_operator = %s """ % (self.operatorSelected)
		
		result = self.dataBaseSqlite.executeSql(sql)

		self.model.setHorizontalHeaderLabels(self.header)
		for x in range(0, len(result)):
		    self.model.insertRow(x)
		    z=0
		    for y in range(0,3):
		        self.model.setData(self.model.index(x, y), result[x][z])
		        z+=1

		self.id.setText(str(operator_result[0][0]))
		self.name.setText(str(operator_result[0][1]))
		self.description.setText(str(operator_result[0][2]))
		indexMode = self.cb_mode.findText(self.dataBaseSqlite.selectAll(' mode ', ' where id = {}'.format(operator_result[0][3]))[0][1], Qt.MatchFixedString)
		self.cb_mode.setCurrentIndex(indexMode)

		self.cb_type.itemData(operator_result[0][4])

		self.basics_modal_constant.setText(str(operator_result[0][5]))
		self.basics_occupency.setText(str(operator_result[0][6]))
		self.basics_time_factor.setText(str(operator_result[0][7]))
		self.basics_fixed_wating_factor.setText(str(operator_result[0][8]))
		self.basics_boarding_tariff.setText(str(operator_result[0][9]))
		self.basics_distance_tariff.setText(str(operator_result[0][10]))
		self.basics_time_tariff.setText(str(operator_result[0][11]))
		
		self.energy_min.setText(str(operator_result[0][12]))
		self.energy_max.setText(str(operator_result[0][13]))
		self.energy_slope.setText(str(operator_result[0][14]))
		self.energy_cost.setText(str(operator_result[0][15]))

		self.cost_time_operation.setText(str(operator_result[0][16]))
		self.cost_porc_paid_by_user.setText(str(operator_result[0][17]))

		self.stops_min_stop_time.setText(str(operator_result[0][18]))
		self.stops_unit_boarding_time.setText(str(operator_result[0][19]))
		self.stops_unit_alight_time.setText(str(operator_result[0][20]))


	def __load_fields(self):
		types = ['Normal', 'Transit','Transit with Routes','Non Motorized']
		
		for index, valor in enumerate(types):
			self.cb_type.addItem(types[index],index+1)
		
		mode_result = self.dataBaseSqlite.selectAll(' mode ')
		for value in mode_result:
			self.cb_mode.addItem(value[1], value[0])

		if self.operatorSelected:
			sql =""" select a.name category, b.tariff_factor, b.penal_factor 
					from category a left join operator_category b on (a.id = b.id_category)
					where b.id_operator = %s """ % self.operatorSelected
			existOperatorCategory = self.dataBaseSqlite.executeSql(sql)
		else:
			existOperatorCategory = []
		# Table data
		if self.operatorSelected and len(existOperatorCategory)>0:
			sql = """ select a.name category, b.tariff_factor, b.penal_factor 
			from category a left join operator_category b on (a.id = b.id_category)
			where b.id_operator = {} """.format(self.operatorSelected)
		else:	
			sql= """select name category, '' tariff_factor, '' penal_factor 
				from category """

		result_cat = self.dataBaseSqlite.executeSql(sql)
		
		rowsCount = len(result_cat)
		columsCount = len(result_cat[0])-1
		self.by_category_tbl.setRowCount(rowsCount)
		self.by_category_tbl.setColumnCount(columsCount)
		self.by_category_tbl.setHorizontalHeaderLabels(self.header) # Headers of columns table

		for index, valor in enumerate(result_cat):
			self.vertical_header_cat.append(valor[0])
			headerItem = QTableWidgetItem(valor[0])
			headerItem.setIcon(QIcon(self.plugin_dir+"/icons/category.jpg"))
			self.by_category_tbl.setVerticalHeaderItem(index,headerItem)

		# Set columns size
		header = self.by_category_tbl.horizontalHeader()       
		for x in range(0,columsCount):
			header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)
		for indice,valor in enumerate(result_cat):
			x = 0
			for z in range(1,len(valor)):
				data = result_cat[indice][z] if result_cat[indice][z] is not None else ''
				self.by_category_tbl.setItem(indice, x, QTableWidgetItem(str(data)))
				x+=1


	def __get_scenarios_data(self):
		model = QtGui.QStandardItemModel()
		model.setHorizontalHeaderLabels(['Scenarios'])

		self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
		self.scenario_tree.setModel(self.scenarios_model)
		self.scenario_tree.expandAll()

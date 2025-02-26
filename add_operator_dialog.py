# -*- coding: utf-8 -*-
import os, re, webbrowser, json, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
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
from .classes.general.Helpers import Helpers
from .add_scenario_dialog import AddScenarioDialog
from .classes.general.Validators import validatorExpr  # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .classes.general.Validators import validatorRegex

from qgis.gui import QgsColorButton, QgsGradientColorRampDialog, QgsColorRampButton

from qgis.core import QgsProject, QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsSymbol, QgsLineSymbol, QgsSymbolLayer, QgsSimpleLineSymbolLayer, QgsMarkerLineSymbolLayer, QgsArrowSymbolLayer, QgsSimpleLineSymbolLayer, QgsMarkerLineSymbolLayer


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
		self.header = ['Penal Factor', 'Tariff Factor']
		self.columnOperatorCetegoryDb = ['penal_factor', 'tariff_factor']
		self.vertical_header_cat = []
		self.operatorSelected = codeOperator
		self.idScenario = idScenario

		# Style of LineEdit
		self.changeLineEditStyle = "color: green; font-weight: bold"

		# Scenario Section
		self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
		self.scenario_tree.clicked.connect(self.select_scenario)

		# Definition Section
		self.id = self.findChild(QtWidgets.QLineEdit, 'id')
		self.name = self.findChild(QtWidgets.QLineEdit, 'name')
		self.description = self.findChild(QtWidgets.QLineEdit, 'description')
		self.cb_mode = self.findChild(QtWidgets.QComboBox, 'cb_mode')
		self.cb_type = self.findChild(QtWidgets.QComboBox, 'cb_type')
		self.button_color = QgsColorButton(self, 'Color')
		self.label_color = QLabel("Color") 

		# Basics Section
		self.basics_modal_constant = self.findChild(QtWidgets.QLineEdit, 'basics_modal_constant')
		#self.basics_path_asc = self.findChild(QtWidgets.QLineEdit, 'basics_path_asc')
		self.basics_occupency = self.findChild(QtWidgets.QLineEdit, 'basics_occupency')
		self.basics_time_factor = self.findChild(QtWidgets.QLineEdit, 'basics_time_factor')
		self.basics_fixed_wating_factor = self.findChild(QtWidgets.QLineEdit, 'basics_fixed_wating_factor')
		self.basics_boarding_tariff = self.findChild(QtWidgets.QLineEdit, 'basics_boarding_tariff')
		self.basics_distance_tariff = self.findChild(QtWidgets.QLineEdit, 'basics_distance_tariff')
		self.basics_time_tariff = self.findChild(QtWidgets.QLineEdit, 'basics_time_tariff')
		
		self.layout_operator = self.findChild(QtWidgets.QFormLayout, 'formLayout_operator')
		self.layout_operator.addRow(self.label_color, self.button_color)
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
		#self.by_category_tbl.itemChanged.connect(self.__update_category)
		
		# Validations
		self.id.setValidator(validatorExpr('integer'))
		self.id.textChanged.connect(self.check_state)
		
		self.name.setMaxLength(10)
		self.description.setMaxLength(55)

		self.basics_modal_constant.setValidator(validatorExpr('decimal'))
		self.basics_modal_constant.textChanged.connect(self.check_state)
		"""
		self.basics_path_asc.setValidator(validatorExpr('decimal'))
		self.basics_path_asc.textChanged.connect(self.check_state)ç
		"""
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
		self.__loadId()

		if self.operatorSelected:
			self.setWindowTitle("Edit Operator")
			self.load_default_data()
		self.by_category_tbl.itemChanged.connect(self.__validate_category)	


	def __loadId(self):
		if self.operatorSelected is None:
			self.id.setText(str(self.dataBaseSqlite.maxIdTable(" operator "))) 


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

	
	def select_scenario(self, selectedIndex):
		"""
		    @summary: Set Scenario selected
		"""
		self.scenarioSelectedIndex = selectedIndex
		self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
		scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
		self.idScenario = scenarioData[0][0]
		self.load_default_data()
		# self.__load_fields()


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
		
		if self.button_color.isNull():
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Route", "Please select Color.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
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
			   stops_unit_alight_time=self.stops_unit_alight_time.text(), color=self.button_color.color().rgb()
			   )
		
		if self.operatorSelected:
			data.update(scenarios=scenarios)
			result = self.dataBaseSqlite.updateOperator(data)
		else:
			data.update(scenarios=scenarios)
			result = self.dataBaseSqlite.addOperator(data)

		rowsCategory = self.by_category_tbl.rowCount()
		ope_cat_arr = []
		for index in range(0,rowsCategory):
			id_operator = self.id.text()
			id_category = self.by_category_tbl.verticalHeaderItem(index).text().split(" ")[0] 
			penal_factor = self.by_category_tbl.item(index, 0).text()
			tariff_factor = self.by_category_tbl.item(index, 1).text()
			
			ifExist = self.dataBaseSqlite.selectAll('operator_category', " where id_operator = {} and id_category = {} and id_scenario = {}".format(id_operator, id_category, self.idScenario))
			
			ope_cat_arr.append((id_operator, id_category, tariff_factor, penal_factor))

			if not self.dataBaseSqlite.operatorCategoryInsertUpdate(scenarios, ope_cat_arr):	
				messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
				messagebox.exec_()
		
		if result:
			self.accept()
		else:
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Project Configuration", "Please write the operator's Land use Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False


	def __update_category(self,item):
		id_scenario = self.idScenario
		scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
		scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
		
		if item.text()!=None and item.text()!='' and self.id.text()!='':
			column = item.column()
			item_value = item.text()
			row = item.row()

			id_operator = self.id.text()
			dataColumn = self.columnOperatorCetegoryDb[column]
			category_name = self.vertical_header_cat[row]
			id_category = self.dataBaseSqlite.selectAll(' category ', " where id = '"+str(category_name.split(" ")[0])+"'")
			id_category = id_category[0][0]

			ifExist = self.dataBaseSqlite.selectAll('operator_category', " where id_operator = {} and id_category = {} and id_scenario = {}".format(id_operator, id_category, self.idScenario))
			
			if len(ifExist) == 0:
				if not self.dataBaseSqlite.addOperatorCategory(scenarios, id_operator, id_category, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()
			else: 
				if not self.dataBaseSqlite.updateOperatorCategory(scenarios, id_operator, id_category, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add  new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()


	def load_default_data(self):
		types = ['Normal', 'Transit','Transit with Routes','Non Motorized']
		icons_types = ['normal.png', 'transit_icon.png','transit_with_routes.png','non_motorized.png']
		id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)
		self.cb_type.clear()
		
		for index, valor in enumerate(types):
			symbol_json_str = self.operators_symbols_lst(index+1)
			image = self.get_symbol_object(symbol_json_str).asImage(QSize(15,7))
		
			self.cb_type.addItem(QIcon(QPixmap.fromImage(image)), types[index],index+1)

		mode_result = self.dataBaseSqlite.selectAll(' mode ')
		self.cb_mode.clear()
		for value in mode_result:
			self.cb_mode.addItem(value[1], value[0])

		id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)
		if id_prevScenario:
			operator_result_prev = self.dataBaseSqlite.selectAll(' operator ', " where id = {} and id_scenario = {}".format(self.operatorSelected, id_prevScenario[0][0]))
		
		operator_result = self.dataBaseSqlite.selectAll(' operator ', " where id = {} and id_scenario = {}".format(self.operatorSelected, self.idScenario))
		if operator_result and self.operatorSelected:
			
			self.id.setText(str(operator_result[0][0]))
			self.name.setText(str(operator_result[0][2]))
			self.description.setText(str(operator_result[0][3]))
			
			indexMode = self.cb_mode.findText(self.dataBaseSqlite.selectAll(' mode ', ' where id = {}'.format(operator_result[0][4]))[0][1], Qt.MatchFixedString)
			self.cb_mode.setCurrentIndex(indexMode)

			indexType = self.cb_type.findText(types[operator_result[0][5]-1])
			self.cb_type.setCurrentIndex(indexType)

			self.basics_modal_constant.setText(Helpers.decimalFormat(str(operator_result[0][6])))
			self.basics_occupency.setText(Helpers.decimalFormat(str(operator_result[0][7])))
			self.basics_time_factor.setText(Helpers.decimalFormat(str(operator_result[0][8])))
			self.basics_fixed_wating_factor.setText(Helpers.decimalFormat(str(operator_result[0][9])))
			self.basics_boarding_tariff.setText(Helpers.decimalFormat(str(operator_result[0][10])))
			self.basics_distance_tariff.setText(Helpers.decimalFormat(str(operator_result[0][11])))
			self.basics_time_tariff.setText(Helpers.decimalFormat(str(operator_result[0][12])))
			
			self.energy_min.setText(Helpers.decimalFormat(str(operator_result[0][13])))
			self.energy_max.setText(Helpers.decimalFormat(str(operator_result[0][14])))
			self.energy_slope.setText(Helpers.decimalFormat(str(operator_result[0][15])))
			self.energy_cost.setText(Helpers.decimalFormat(str(operator_result[0][16])))

			self.cost_time_operation.setText(Helpers.decimalFormat(str(operator_result[0][17])))
			self.cost_porc_paid_by_user.setText(Helpers.decimalFormat(str(operator_result[0][18])))

			self.stops_min_stop_time.setText(Helpers.decimalFormat(str(operator_result[0][19])))
			self.stops_unit_boarding_time.setText(Helpers.decimalFormat(str(operator_result[0][20])))
			self.stops_unit_alight_time.setText(Helpers.decimalFormat(str(operator_result[0][21])))

			if operator_result[0][22]: 
				qcolor = QColor()
				qcolor.setRgb(operator_result[0][22])
				self.button_color.setColor(qcolor)

			if id_prevScenario and operator_result_prev:
				if (operator_result[0][1] !=  operator_result_prev[0][1]):
					self.name.setStyleSheet(self.changeLineEditStyle)
				else:
					self.name.setStyleSheet("")

				if (operator_result[0][2] !=  operator_result_prev[0][2]):
					self.description.setStyleSheet(self.changeLineEditStyle)
				else:
					self.description.setStyleSheet("")

				if (operator_result[0][6] !=  operator_result_prev[0][6]):
					self.basics_modal_constant.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_modal_constant.setStyleSheet("")

				if (operator_result[0][7] !=  operator_result_prev[0][7]):
					self.basics_occupency.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_occupency.setStyleSheet("")

				if (operator_result[0][8] !=  operator_result_prev[0][8]):
					self.basics_time_factor.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_time_factor.setStyleSheet("")

				if (operator_result[0][9] !=  operator_result_prev[0][9]):
					self.basics_fixed_wating_factor.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_fixed_wating_factor.setStyleSheet("")

				if (operator_result[0][10] !=  operator_result_prev[0][10]):
					self.basics_boarding_tariff.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_boarding_tariff.setStyleSheet("")

				if (operator_result[0][11] !=  operator_result_prev[0][11]):
					self.basics_distance_tariff.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_distance_tariff.setStyleSheet("")

				if (operator_result[0][12] !=  operator_result_prev[0][12]):
					self.basics_time_tariff.setStyleSheet(self.changeLineEditStyle)
				else:
					self.basics_time_tariff.setStyleSheet("")

				if (operator_result[0][13] !=  operator_result_prev[0][13]):
					self.energy_min.setStyleSheet(self.changeLineEditStyle)
				else:
					self.energy_min.setStyleSheet("")

				if (operator_result[0][14] !=  operator_result_prev[0][14]):
					self.energy_max.setStyleSheet(self.changeLineEditStyle)
				else:
					self.energy_max.setStyleSheet("")

				if (operator_result[0][15] !=  operator_result_prev[0][15]):
					self.energy_slope.setStyleSheet(self.changeLineEditStyle)
				else:
					self.energy_slope.setStyleSheet("")

				if (operator_result[0][16] !=  operator_result_prev[0][16]):
					self.energy_cost.setStyleSheet(self.changeLineEditStyle)
				else:
					self.energy_cost.setStyleSheet("")

				if (operator_result[0][17] !=  operator_result_prev[0][17]):
					self.cost_time_operation.setStyleSheet(self.changeLineEditStyle)
				else:
					self.cost_time_operation.setStyleSheet("")

				if (operator_result[0][18] !=  operator_result_prev[0][18]):
					self.cost_porc_paid_by_user.setStyleSheet(self.changeLineEditStyle)
				else:
					self.cost_porc_paid_by_user.setStyleSheet("")

				if (operator_result[0][19] !=  operator_result_prev[0][19]):
					self.stops_min_stop_time.setStyleSheet(self.changeLineEditStyle)
				else:
					self.stops_min_stop_time.setStyleSheet("")

				if (operator_result[0][20] !=  operator_result_prev[0][20]):
					self.stops_unit_boarding_time.setStyleSheet(self.changeLineEditStyle)
				else:
					self.stops_unit_boarding_time.setStyleSheet("")

				if (operator_result[0][21] !=  operator_result_prev[0][21]):
					self.stops_unit_alight_time.setStyleSheet(self.changeLineEditStyle)
				else:
					self.stops_unit_alight_time.setStyleSheet("")

	def __load_fields(self):
		types = ['Normal', 'Transit','Transit with Routes','Non Motorized']
		icons_types = ['normal.png', 'transit_icon.png','transit_with_routes.png','non_motorized.png']
		id_prevScenario = self.dataBaseSqlite.previousScenario(self.idScenario)

		self.cb_type.clear()
		
		for index, valor in enumerate(types):
			symbol_json_str = self.operators_symbols_lst(index+1)
			image = self.get_symbol_object(symbol_json_str).asImage(QSize(15,7))
			self.cb_type.addItem(QIcon(QPixmap.fromImage(image)), types[index],index+1)

		"""
		self.cb_type.clear()
		for index, valor in enumerate(types):
			self.cb_type.addItem(QIcon(f"{self.plugin_dir}/icons/{icons_types[index]}"), types[index],index+1)
		"""
		
		mode_result = self.dataBaseSqlite.selectAll(' mode ')
		self.cb_mode.clear()
		for value in mode_result:
			self.cb_mode.addItem(value[1], value[0])

		if self.operatorSelected:
			sql =""" select a.name category, b.penal_factor, b.tariff_factor 
					from category a left join operator_category b on (a.id = b.id_category and a.id_scenario = b.id_scenario)
					where b.id_operator = %s and a.id_scenario = %s """ % (self.operatorSelected, self.idScenario)
			existOperatorCategory = self.dataBaseSqlite.executeSql(sql)
		else:
			existOperatorCategory = []

		operatorSql = " b.id_operator = {0}".format(self.operatorSelected) if self.operatorSelected else  'b.id_operator is null '
		# Table data
		sql = """with base as (
			select a.id||' '||a.name category, b.penal_factor, b.tariff_factor, a.id
			from category a 
			join operator_category b on (a.id = b.id_category and a.id_scenario = b.id_scenario)
			where {0} and a.id_scenario = {1}
		),
		operator_only as (
			select id||' '||name category, '' penal_factor, '' tariff_factor, id
			from category where id_scenario = {1}
		)
		SELECT * FROM
			base
		UNION
			select * from 
			operator_only
			where category not in (select category from base)
		ORDER BY 4""".format(operatorSql, self.idScenario)
		
		result_cat = self.dataBaseSqlite.executeSql(sql) 
		result_cat_prev = ''
		if id_prevScenario and self.operatorSelected:
			sql = """with base as (
				select a.id||' '||a.name category, b.penal_factor, b.tariff_factor 
				from category a 
				join operator_category b on (a.id = b.id_category and a.id_scenario = b.id_scenario)
				where b.id_operator = {0} and a.id_scenario = {1}
			),
			operator_only as (
				select id||' '||name category, '' penal_factor, '' tariff_factor 
				from category where id_scenario = {1}
			)
			select * from 
				base
			UNION
				select * from 
				operator_only
				where category not in (select category from base)""".format(self.operatorSelected, id_prevScenario[0][0])

			result_cat_prev = self.dataBaseSqlite.executeSql(sql)
		
		rowsCount = len(result_cat)
		columsCount = len(result_cat[0])-2
		self.by_category_tbl.setRowCount(rowsCount)
		self.by_category_tbl.setColumnCount(columsCount)
		self.by_category_tbl.setHorizontalHeaderLabels(self.header) # Headers of columns table
		self.by_category_tbl.horizontalHeader().setStretchLastSection(True)
		for index, valor in enumerate(result_cat):
			self.vertical_header_cat.append(valor[0])
			headerItem = QTableWidgetItem(valor[0])
			headerItem.setIcon(QIcon(self.plugin_dir+"/icons/category.png"))
			self.by_category_tbl.setVerticalHeaderItem(index,headerItem)

		# Set columns size
		header = self.by_category_tbl.horizontalHeader()       
		for x in range(0,columsCount):
			header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)
		# Fill values of the table
		for indice,valor in enumerate(result_cat):
			x = 0
			for z in range(1,len(valor)-1):
				data = result_cat[indice][z] if result_cat[indice][z] is not None else ''
				data_prev = data
				if result_cat_prev:
					data_prev = result_cat_prev[indice][z] if result_cat_prev[indice][z] is not None else ''
				font = QFont()
				font.setBold(True)
				itemText = QTableWidgetItem()
				itemText.setText(Helpers.decimalFormat(str(data)))
				if data != data_prev:
					itemText.setForeground(QColor("green"))
					itemText.setFont(font)
				
				self.by_category_tbl.setItem(indice, x, itemText)
				x+=1


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


	def get_symbol_object(self, symbol_srt):
		""" Return dictionary with objects of symbol """
		# TODO: resolver tema de la symbologia correcta
		symbol_obj = json.loads(symbol_srt.replace("'",'"'))
		symbol_layers = QgsLineSymbol()

		for layer_symbol in symbol_obj['layers_list']:
			obj_symbol = eval(f"Qgs{layer_symbol['type_layer']}SymbolLayer.create({layer_symbol['properties_layer']})")
			symbol_layers.appendSymbolLayer(obj_symbol)
		symbol_layers.deleteSymbolLayer(0)
		return symbol_layers
	

	def operators_symbols_lst(self, type):
        # Type: 1 Transit
        # Type: 2 Non motorized
        # Type: 3 Transit with routes
        # Type: 4 Normal		
		symbol_group_list = [
			"""{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'dash', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}""",
			"""{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'round', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'round', 'line_color': '0,0,0,255', 'line_style': 'solid', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '-1', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}, {'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'round', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'round', 'line_color': '0,0,0,255', 'line_style': 'solid', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}""",
			"""{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'solid', 'line_width': '0.26', 'line_width_unit': 'MM', 'offset': '1.2', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}, {'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'solid', 'line_width': '1.06', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}, {'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'solid', 'line_width': '0.26', 'line_width_unit': 'MM', 'offset': '-1.2', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}""",
			"""{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'dot', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}"""
		]

		return symbol_group_list[type-1]
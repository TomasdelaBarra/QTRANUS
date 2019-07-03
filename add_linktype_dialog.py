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
		# Definition Section
		self.id = self.findChild(QtWidgets.QLineEdit, 'id')
		self.name = self.findChild(QtWidgets.QLineEdit, 'name')
		self.description = self.findChild(QtWidgets.QLineEdit, 'description')
		self.id_administrator = self.findChild(QtWidgets.QComboBox, 'id_administrator')
		
		# Basics Section
		self.capacity_factor = self.findChild(QtWidgets.QLineEdit, 'capacity_factor')
		self.min_maintenance_cost = self.findChild(QtWidgets.QLineEdit, 'min_maintenance_cost')
		self.porc_speed_reduction = self.findChild(QtWidgets.QLineEdit, 'porc_speed_reduction')
		self.porc_max_speed_reduction = self.findChild(QtWidgets.QLineEdit, 'porc_max_speed_reduction')
		self.vc_max_reduction = self.findChild(QtWidgets.QLineEdit, 'vc_max_reduction')

		# Operator Data Section
		self.operator_table = self.findChild(QtWidgets.QTableWidget, 'operator_table')
		
		self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
		self.operator_table.itemChanged.connect(self.__update_operator_linktype)
		
		self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_linktype)
		self.__load_fields()
		self.__get_scenarios_data()

		if self.linkTypeSelected:
			self.load_default_data()


	def save_new_linktype(self):
		id_scenario = self.idScenario
		scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
		scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
		if self.id is None or self.id.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
			
		if self.linkTypeSelected is None:
			if self.dataBaseSqlite.validateId('link_type', self.id.text()) is False:
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

		if self.id_administrator is None or self.id_administrator.currentText().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Author.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.capacity_factor is None or self.capacity_factor.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Transport Convergence.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False
		    
		if self.min_maintenance_cost is None or self.min_maintenance_cost.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Transport Smoothing factor.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.porc_speed_reduction is None or self.porc_speed_reduction.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Transport Route similarity.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.porc_max_speed_reduction is None or self.porc_max_speed_reduction.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Land use Iterations.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		if self.vc_max_reduction is None or self.vc_max_reduction.text().strip() == '':
			messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Operator", "Please write the operator's Land use Convergence.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
			messagebox.exec_()
			return False

		result = self.dataBaseSqlite.selectAll('administrator', " where name = '"+self.id_administrator.currentText()+"'") 
		id_administrator = result[0][0]		
		
		if self.linkTypeSelected is None:
			result = self.dataBaseSqlite.addLinkType(scenarios, self.id.text(), self.name.text(), self.description.text(), id_administrator, self.capacity_factor.text(), self.min_maintenance_cost.text(), self.porc_speed_reduction.text(), self.porc_max_speed_reduction.text(), self.vc_max_reduction.text())
		else:
			result = self.dataBaseSqlite.updateLinkType(self.id.text(), self.name.text(), self.description.text(), id_administrator, self.capacity_factor.text(), self.min_maintenance_cost.text(), self.porc_speed_reduction.text(), self.porc_max_speed_reduction.text(), self.vc_max_reduction.text())

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
			id_operator = self.dataBaseSqlite.selectAll('operator', " where name = '"+str(operator_name)+"'")
			id_operator = id_operator[0][0]
			id_scenario = self.idScenario
			ifExist = self.dataBaseSqlite.selectAll('link_type_operator', " where id_linktype = {} and id_operator = {} ".format(id_linktype, id_operator))
			
			if len(ifExist) == 0:
				if not self.dataBaseSqlite.addLinkTypeOperator(id_linktype, id_operator, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()
			else: 
				if not self.dataBaseSqlite.updateLinkTypeOperator(id_linktype, id_operator, column=dataColumn, value=item_value):
					messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add  new Operator Category", "Error while insert data into database.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
					messagebox.exec_()


	def load_default_data(self):
		linktype_result = self.dataBaseSqlite.selectAll(' link_type ', " where id = {}".format(self.linkTypeSelected))
		print("linktype_result ", linktype_result)
		self.id.setText(str(linktype_result[0][0]))
		self.name.setText(str(linktype_result[0][1]))
		self.description.setText(str(linktype_result[0][2]))

		nameAdministrator = self.dataBaseSqlite.selectAll(' administrator ', ' where id = {}'.format(linktype_result[0][3]))[0][1]
		indexAdministrator = self.id_administrator.findText(nameAdministrator, Qt.MatchFixedString)
		self.id_administrator.setCurrentIndex(indexAdministrator)

		self.capacity_factor.setText(str(linktype_result[0][4]))
		self.min_maintenance_cost.setText(str(linktype_result[0][5]))
		self.porc_speed_reduction.setText(str(linktype_result[0][6]))
		self.porc_max_speed_reduction.setText(str(linktype_result[0][7]))
		self.vc_max_reduction.setText(str(linktype_result[0][8]))
		

	def __load_fields(self):
		
		administrator_result = self.dataBaseSqlite.selectAll(' administrator ')
		for value in administrator_result:
			self.id_administrator.addItem(value[1])

		# Table data
		if self.linkTypeSelected:
			sql = """select a.name, b.speed, b.charges, b.penaliz, b.distance_cost,
					  b.equiv_vahicules, b.overlap_factor, b.margin_maint_cost 
				 	from 
					operator a
					left join link_type_operator b on a.id = b.id_operator
					where b.id_linktype = {} """.format(self.linkTypeSelected)
			existOperatorLinkType = self.dataBaseSqlite.executeSql(sql)
		else:
			existOperatorLinkType = []	

		if self.linkTypeSelected and len(existOperatorLinkType) > 0:
			sql = """select a.name, b.speed, b.charges, b.penaliz, b.distance_cost,
					  b.equiv_vahicules, b.overlap_factor, b.margin_maint_cost 
				 	from 
					operator a
					left join link_type_operator b on a.id = b.id_operator
					where b.id_linktype = {} """.format(self.linkTypeSelected)
		else:
			sql = """select a.name, '' speed, '' charges, '' penaliz, '' distance_cost,
					 '' equiv_vahicules, '' overlap_factor, '' margin_maint_cost 
				 	from
				 		operator a 
					"""
		#print("sql {}".format(sql))
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
		#for x in range(0,columsCount):
		#	self.header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)
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

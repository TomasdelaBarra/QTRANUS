# -*- coding: utf-8 -*-
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets 
from PyQt5.QtCore import *
from qgis.gui import QgsMessageBar
from PyQt5.Qt import QAbstractItemView, QStandardItemModel, QStandardItem, QMainWindow, QToolBar, QHBoxLayout
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsField, QgsProject

from .classes.ExpressionData import ExpressionData
from .classes.general.FileManagement import FileManagement as FileM
from .classes.general.Helpers import Helpers
from .scenarios_model import ScenariosModel
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.data.DataBaseSqlite import DataBaseSqlite


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zonelayer.ui'))

class ZoneLayerDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, tranus_folder, parent=None, layerId=None):
        super(ZoneLayerDialog, self).__init__(parent)
        self.setupUi(self)
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        self.tranus_folder = tranus_folder
        self.project = parent.project
        self.dataBaseSqlite = DataBaseSqlite( self.tranus_folder )
        self.proj = QgsProject.instance()
        self.tempLayerName = ''
        self.layerId = layerId

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.layerName = self.findChild(QtWidgets.QLineEdit, 'layerName')
        self.base_scenario = self.findChild(QtWidgets.QComboBox, 'base_scenario')
        self.sectors = self.findChild(QtWidgets.QListWidget, 'sectors')
        self.scenarios = self.findChild(QtWidgets.QTreeView, 'scenarios')
        self.expression = self.findChild(QtWidgets.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtWidgets.QComboBox, 'base_scenario')
        self.operators = self.findChild(QtWidgets.QComboBox, name='cb_operator')
        self.alternateScenario = self.findChild(QtWidgets.QComboBox, name='cb_alternate_scenario')
        self.fields = self.findChild(QtWidgets.QComboBox, 'comboField')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')        
        self.progressBar = self.findChild(QtWidgets.QProgressBar, 'progressBar')        

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layerName.keyPressEvent = self.keyPressEvent
        self.buttonBox.accepted.connect(self.ready)
        self.baseScenario.currentIndexChanged.connect(self.scenario_changed)
        self.operators.currentIndexChanged.connect(self.operator_changed)
        self.sectors.itemDoubleClicked.connect(self.sector_selected)
        
        # Loads combo-box controls
        self.__load_scenarios_combobox()
        self.__load_sectors_combobox()
        self.__load_fields_combobox()
        self.__load_operators()
        # self.reload_scenarios()
        self.__load_scenarios()

        if self.layerId:
            self.__load_default_data()
    
    
    def __load_scenarios(self):

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenarios.setSelectionModel(modelSelection)


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'zones.html')
        webbrowser.open_new_tab(filename)
    
    def keyPressEvent(self, event):
        """
            @summary: Detects when a key is pressed
            @param event: Key press event
            @type event: Event object
        """
        QtWidgets.QLineEdit.keyPressEvent(self.layerName, event)
        if not self.validate_string(event.text()):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Layer Name", "Invalid character: " + event.text() + ".", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            if self.layerName.isUndoAvailable():
                self.layerName.setText(self.tempLayerName)
        else:
            self.tempLayerName = self.layerName.text()


    def validate_string(self, input):
        """
            @summary: Validates invalid characters
            @param input: Input string
            @type input: String object
        """
        pattern = re.compile('[\\\/\:\*\?\"\<\>\|]')
        if re.match(pattern, input) is None:
            return True
        else:
            return False
            

    def scenario_changed(self, newIndex):
        """
            @summary: Detects when an scenario was changed
        """
        if self.operators.currentText() != '':
            self.alternateScenario.clear()
            self.__load_alternate_scenario_combobox()

    def operator_changed(self, newIndex):
        """
            @summary: Detects when an operator was changed
        """
        currentOperator = self.operators.currentText()
        if self.operators.currentText() == '':
            self.alternateScenario.clear()
            self.alternateScenario.setEnabled(False)
        else:
            if len(self.alternateScenario) == 0:
                self.alternateScenario.setEnabled(True)
                self.alternateScenario.clear()
                self.__load_alternate_scenario_combobox()
    
    def sector_selected(self, item):
        """
            @summary: Detects when an item in the list is double clicked
            @param item: Item selected
            @type item: QListWidget item 
        """
        textToAdd = item.text()
            
        if self.expression.text().strip() == '':
            self.expression.setText(self.expression.text() + textToAdd)
        else:
            self.expression.setText(self.expression.text() + " + " + textToAdd)
    
    """def reload_scenarios(self):
        
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)"""
        

    def ready(self):
        """
            @summary: Triggered when accept button is clicked
        """
        validationResult, scenariosExpression, sectorsExpression, sectorsExpressionText = self.__validate_data() 
        
        if validationResult:
            self.progressBar.show()
            self.progressBar.setValue(10)

            if not self.layerId:
                result = self.project.addZonesLayer(self.progressBar, self.layerName.text(), scenariosExpression, str(self.fields.currentText()), sectorsExpression, sectorsExpressionText)
            else:
                result = self.project.editZonesLayer(self.progressBar, self.layerName.text(), scenariosExpression, str(self.fields.currentText()), sectorsExpression, sectorsExpressionText, self.layerId)

            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Zones", "Layer generated without information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()  
            self.accept()
        else:
            print("New zones layer was not created.")
            

    def __load_scenarios_combobox(self):
        """
            @summary: Loads scenarios combo-box
        """

        items = self.project.map_data.get_sorted_scenarios()
        self.base_scenario.addItems(items)
        
        
    def __load_sectors_combobox(self):
        """
            @summary: Loads sectors combo-box
        """

        for key in sorted(self.project.map_data.sectors_dic):
            self.sectors.addItem(self.project.map_data.sectors_dic[key])

        
    def __load_fields_combobox(self):
        """
            @summary: Loads fields combo-box
        """
        items = self.project.map_data.get_sorted_fields()
        if items is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no fields to load, please reload SHP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no fields to load, please reload SHP file.")
        else:
            self.fields.addItems(items)
        
    def __load_operators(self):
        """
            @summary: Loads operators combo-box
        """
        items = ["", "-", "/"]
        self.operators.addItems(items)

    def __load_alternate_scenario_combobox(self):
        """
            @summary: Loads alternate scenario combo-box
        """
        baseScenario = self.baseScenario.currentText()
        items = self.project.map_data.get_sorted_scenarios()
        for item in items:
            if item != baseScenario:
                self.alternateScenario.addItem(item)
                
    def __validate_data(self):
        """
            @summary: Fields validation
            @return: Validation result, scenariosExpression and sectorsExpression 
        """
        scenariosExpression = []
        # Base validations
        if self.layerName.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Layer Name", "Please write Layer Name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write Layer Name.")
            return False, None, None, None
        
        if self.expression.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Expression", "Please write an expression to be evaluated.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write an expression to be evaluated.")
            return False, None, None, None
        
        if len(self.base_scenario) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Base Scenario", "There are no Base Scenarios loaded.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no Base Scenarios loaded.")
            return False, None, None, None
        else:
            scenariosExpression.append(str(self.baseScenario.currentText()))
        
        if len(self.fields) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no Fields loaded.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("There are no Fields loaded.")
            return False, None, None, None
        
        # Validations for alternate scenario
        if self.operators.currentText() != '':
            scenariosExpression.append(str(self.operators.currentText()))
            if self.alternateScenario.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Alternate Scenario", "Please select an Alternate Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select an Alternate Scenario.")
                return False, None, None, None
            else:
                scenariosExpression.append(str(self.alternateScenario.currentText()))
        scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
        
        if scenariosExpressionResult:
            sectorsExpressionResult, sectorsExpressionList = ExpressionData.validate_sectors_expression(self.expression.text().strip())
            sectorsExpressionText = self.expression.text()
        
        if scenariosExpressionStack.tp > 1 and len(sectorsExpressionList) > 1:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Expression", "Expression with conditionals only applies for one scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Expression with conditionals only applies for one scenario.")
            return False, None, None, None
        
        return scenariosExpressionResult and sectorsExpressionResult, scenariosExpressionStack, sectorsExpressionList, sectorsExpressionText
    
    
    # Load data to edit the zones layer
    def __load_default_data(self):
        data = self.dataBaseSqlite.selectAll(' results_zones ', f""" where id = '{self.layerId}'""")
    
        if data:
            self.layerName.setText(data[0][1])
            self.expression.setText(data[0][2])

            indexFields = self.fields.findText(data[0][4], Qt.MatchFixedString)
            self.fields.setCurrentIndex(indexFields)
            scenario = data[0][3]
            scenario = scenario.split(",")
            scenario[0] = scenario[0].replace("'", "").replace("[", "").replace("]", "")
            indexBaseScenario = self.base_scenario.findText(scenario[0], Qt.MatchFixedString)
            self.base_scenario.setCurrentIndex(indexBaseScenario)
            
            if len(scenario) == 3:           
                scenario[2] = scenario[2].replace("'", "").replace("]", "").strip()
                indexOperators = self.operators.findText(scenario[2] , Qt.MatchFixedString)
                self.operators.setCurrentIndex(indexOperators)
                
                scenario[1] = scenario[1].replace("'", "").strip()
                indexAlternateScenario = self.alternateScenario.findText(scenario[1], Qt.MatchFixedString)
                self.alternateScenario.setCurrentIndex(indexAlternateScenario)
            
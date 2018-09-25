# -*- coding: utf-8 -*-
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets 
from PyQt5.QtCore import *
from qgis.gui import QgsMessageBar
from .classes.ExpressionData import ExpressionData

from .classes.general.FileManagement import FileManagement as FileM
from .scenarios_model import ScenariosModel
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsField, QgsProject
from .classes.general.QTranusMessageBox import QTranusMessageBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zonelayer.ui'))

class ZoneLayerDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None, layerId=None):
        super(ZoneLayerDialog, self).__init__(parent)
        self.setupUi(self)

        self.project = parent.project
        self.proj = QgsProject.instance()
        self.tempLayerName = ''

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

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layerName.keyPressEvent = self.keyPressEvent
        self.buttonBox.accepted.connect(self.ready)
        #self.baseScenario.activated.connect(self.baseScenario,PyQt5.QtCore.SIGNAL("currentIndexChanged(int)"),self.scenario_changed)
        #self.operators.activated.connect(self.operators, PyQt5.QtCore.SIGNAL("currentIndexChanged(int)"), self.operator_changed)
        self.baseScenario.currentIndexChanged.connect(self.scenario_changed)
        self.operators.currentIndexChanged.connect(self.operator_changed)
        self.sectors.itemDoubleClicked.connect(self.sector_selected)
        
        # Loads combo-box controls
        self.__load_scenarios_combobox()
        self.__load_sectors_combobox()
        self.__load_fields_combobox()
        self.__load_operators()
        self.reload_scenarios()

        if layerId:
            self.layerId = layerId
            self.__load_default_data()
    
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
        self.expression.setText(self.expression.text() + item.text())
    
    def reload_scenarios(self):
        """
            @summary: Reloads scenarios
        """
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)
        
    def ready(self):
        """
            @summary: Triggered when accept button is clicked
        """
        validationResult, scenariosExpression, sectorsExpression, sectorsExpressionText = self.__validate_data() 
        print("validationResult {}, scenariosExpression {}, sectorsExpression {}".format(validationResult,scenariosExpression,sectorsExpression))
        if validationResult:
            self.project.addZonesLayer(self.layerName.text(), scenariosExpression, str(self.fields.currentText()), sectorsExpression, sectorsExpressionText)
            self.accept()
        else:
            #QMessageBox.critical(None, "New Layer", "New layer was not created.")
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
            #print(("key: {}, Value: ").format(str(self.project.map_data.sectors_dic[key])))
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
            return False, None, None
        
        if self.expression.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Expression", "Please write an expression to be evaluated.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write an expression to be evaluated.")
            return False, None, None
        
        if len(self.base_scenario) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Base Scenario", "There are no Base Scenarios loaded.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no Base Scenarios loaded.")
            return False, None, None
        else:
            scenariosExpression.append(str(self.baseScenario.currentText()))
        
        if len(self.fields) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no Fields loaded.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("There are no Fields loaded.")
            return False, None, None
        
        # Validations for alternate scenario
        if self.operators.currentText() != '':
            scenariosExpression.append(str(self.operators.currentText()))
            if self.alternateScenario.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Alternate Scenario", "Please select an Alternate Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select an Alternate Scenario.")
                return False, None, None
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
            return False, None, None
        
        return scenariosExpressionResult and sectorsExpressionResult, scenariosExpressionStack, sectorsExpressionList, sectorsExpressionText
    
    # Load data to edit the zones layer
    def __load_default_data(self):
        projectPath = self.project.shape[0:max(self.project.shape.rfind('\\'), self.project.shape.rfind('/'))]
        
        # Get data from XML File with the parameters
        expression, field, name, scenario = FileM.find_layer_data(projectPath, self.layerId)

        self.layerName.setText(name)
        self.expression.setText(expression)
        indexFields = self.fields.findText(field, Qt.MatchFixedString)
        self.fields.setCurrentIndex(indexFields)
        
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
            
            
        


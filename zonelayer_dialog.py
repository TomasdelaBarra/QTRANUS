
import os, re, webbrowser

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from qgis.gui import QgsMessageBar
from classes.ExpressionData import ExpressionData

from .scenarios_model import ScenariosModel
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsProject
from PyQt4.Qt import QMessageBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zonelayer.ui'))

class ZoneLayerDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(ZoneLayerDialog, self).__init__(parent)
        self.setupUi(self)

        self.project = parent.project
        self.proj = QgsProject.instance()
        self.tempLayerName = ''

        # Linking objects with controls
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.layerName = self.findChild(QtGui.QLineEdit, 'layerName')
        self.base_scenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.sectors = self.findChild(QtGui.QListWidget, 'sectors')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.expression = self.findChild(QtGui.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.operators = self.findChild(QtGui.QComboBox, name='cb_operator')
        self.alternateScenario = self.findChild(QtGui.QComboBox, name='cb_alternate_scenario')
        self.fields = self.findChild(QtGui.QComboBox, 'comboField')
        self.buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')        

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layerName.keyPressEvent = self.keyPressEvent
        self.buttonBox.accepted.connect(self.ready)
        self.baseScenario.connect(self.baseScenario,SIGNAL("currentIndexChanged(int)"),self.scenario_changed)
        self.operators.connect(self.operators, SIGNAL("currentIndexChanged(int)"), self.operator_changed)
        self.sectors.itemDoubleClicked.connect(self.sector_selected)
        
        # Loads combo-box controls
        self.__load_scenarios_combobox()
        self.__load_sectors_combobox()
        self.__load_fields_combobox()
        self.__load_operators()
        self.reload_scenarios()
    
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
        QtGui.QLineEdit.keyPressEvent(self.layerName, event)
        if not self.validate_string(event.text()):
            QMessageBox.warning(None, "Layer Name", "Invalid character: " + event.text() + ".")
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
        validationResult, scenariosExpression, sectorsExpression = self.__validate_data() 
        if validationResult:
            self.project.addZonesLayer(self.layerName.text(), scenariosExpression, str(self.fields.currentText()), sectorsExpression)
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
            #print("key: {0}, Value: {1}").format(key, self.project.map_data.sectors_dic[key])
            self.sectors.addItem(self.project.map_data.sectors_dic[key])

        
    def __load_fields_combobox(self):
        """
            @summary: Loads fields combo-box
        """
        items = self.project.map_data.get_sorted_fields()
        if items is None:
            QMessageBox.warning(None, "Fields", "There are no fields to load, please reload SHP file.")
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
            QMessageBox.warning(None, "Layer Name", "Please write Layer Name.")
            print ("Please write Layer Name.")
            return False, None, None
        
        if self.expression.text().strip() == '':
            QMessageBox.warning(None, "Expression", "Please write an expression to be evaluated.")
            print ("Please write an expression to be evaluated.")
            return False, None, None
        
        if len(self.base_scenario) == 0:
            QMessageBox.warning(None, "Base Scenario", "There are no Base Scenarios loaded.")
            print ("There are no Base Scenarios loaded.")
            return False, None, None
        else:
            scenariosExpression.append(str(self.baseScenario.currentText()))
        
        if len(self.fields) == 0:
            QMessageBox.warning(None, "Fields", "There are no Fields loaded.")
            print("There are no Fields loaded.")
            return False, None, None
        
        # Validations for alternate scenario
        if self.operators.currentText() != '':
            scenariosExpression.append(str(self.operators.currentText()))
            if self.alternateScenario.currentText() == '':
                QMessageBox.warning(None, "Alternate Scenario", "Please select an Alternate Scenario.")
                print("Please select an Alternate Scenario.")
                return False, None, None
            else:
                scenariosExpression.append(str(self.alternateScenario.currentText()))
        
        scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
        
        if scenariosExpressionResult:
            sectorsExpressionResult, sectorsExpressionList = ExpressionData.validate_sectors_expression(self.expression.text().strip())
        
        if scenariosExpressionStack.tp > 1 and len(sectorsExpressionList) > 1:
            QMessageBox.warning(None, "Expression", "Expression with conditionals only applies for one scenario.")
            print("Expression with conditionals only applies for one scenario.")
            return False, None, None
        
        return scenariosExpressionResult and sectorsExpressionResult, scenariosExpressionStack, sectorsExpressionList 
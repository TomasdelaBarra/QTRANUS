
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from qgis.gui import QgsMessageBar
from classes.ExpressionData import ExpressionData

from .scenarios_model import ScenariosModel
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zonelayer.ui'))

class ZoneLayerDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(ZoneLayerDialog, self).__init__(parent)
        #QDialog.__init__(self)
        self.setupUi(self)

        self.project = parent.project

        #self.bar = QgsMessageBar()
        #self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )

        # Linking objects with controls
        self.base_scenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.sectors = self.findChild(QtGui.QListWidget, 'sectors')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.layerName = self.findChild(QtGui.QLineEdit, 'layerName')
        self.expression = self.findChild(QtGui.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.operators = self.findChild(QtGui.QComboBox, name='cb_operator')
        self.alternateScenario = self.findChild(QtGui.QComboBox, name='cb_alternate_scenario')
        self.fields = self.findChild(QtGui.QComboBox, 'comboField')
        self.buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')
        
        self.proj = QgsProject.instance()

        # Control Actions
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
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)
        
    def ready(self):
        """
            @summary: Triggered when accept button is clicked
        """
        validationResult, scenariosExpression, sectorsExpression = self.__validate_data() 
        if validationResult:
            self.project.addLayer(self.layerName.text(), scenariosExpression, str(self.fields.currentText()), sectorsExpression)
        else:
            print("New layer was not created.")
            
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
        self.fields.addItems(items)
        
    def __load_operators(self):
        """
            @summary: Loads operators combo-box
        """
        items = ["", "-", "/"]
        self.operators.addItems(items)
        #self.bar.pushMessage("Hello", "World", level=QgsMessageBar.INFO)

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
            @return: Validation result, scenariosExpression adn sectorsExpression 
        """
        scenariosExpression = []
        # Base validations
        if self.layerName.text().strip() == '':
            print ("Please write Layer Name.")
            return False, None, None
        
        if self.expression.text().strip() == '':
            print ("Please write an expression to be evaluated.")
            return False, None, None
        
        if len(self.base_scenario) == 0:
            print ("There are no Base Scenarios loaded.")
            return False, None, None
        else:
            scenariosExpression.append(str(self.baseScenario.currentText()))
        
        if len(self.fields) == 0:
            print("There are no Fields loaded.")
            return False, None, None
        
        # Validations for alternate scenario
        if self.operators.currentText() != '':
            scenariosExpression.append(str(self.operators.currentText()))
            if self.alternateScenario.currentText() == '':
                print("Please select an Alternate Scenario.")
                return False, None, None
            else:
                scenariosExpression.append(str(self.alternateScenario.currentText()))
        
        scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
        
        if scenariosExpressionResult:
            sectorsExpressionResult, sectorsExpressionList = ExpressionData.validate_sectors_expression(self.expression.text().strip())
        
        if scenariosExpressionStack.tp > 1 and len(sectorsExpressionList) > 1:
            print("Expression with conditionals only apply for one scenario.")
            return False, None, None
        
        return scenariosExpressionResult and sectorsExpressionResult, scenariosExpressionStack, sectorsExpressionList 
import os, re, webbrowser
from PyQt4 import QtGui, uic
from PyQt4.Qt import QMessageBox
from string import *
from .scenarios_model import ScenariosModel
from classes.ExpressionData import ExpressionData
from classes.network.Network import Network
from classes.network.Level import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'networklayer.ui'))

class NetworkLayerDialog(QtGui.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        super(NetworkLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.network = Network()
        self.level = None
        
        # Linking objects with controls
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.layerName = self.findChild(QtGui.QLineEdit, 'layerName')
        self.expression = self.findChild(QtGui.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.scenarioOperator = self.findChild(QtGui.QComboBox, name='cb_operator')
        self.alternateScenario = self.findChild(QtGui.QComboBox, name='cb_alternate_scenario')
        self.variablesList = self.findChild(QtGui.QComboBox, name='cb_variables')
        self.total = self.findChild(QtGui.QRadioButton, 'rbtn_total')
        self.operators = self.findChild(QtGui.QRadioButton, 'rbtn_operators')
        self.routes = self.findChild(QtGui.QRadioButton, 'rbtn_routes')
        self.list = self.findChild(QtGui.QListWidget, 'list')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layerName.keyPressEvent = self.keyPressEvent
        self.buttonBox.accepted.connect(self.create_layer)
        self.scenarioOperator.currentIndexChanged[int].connect(self.scenario_operator_changed)
        self.baseScenario.currentIndexChanged[int].connect(self.scenario_changed)
        self.total.clicked.connect(self.total_checked)
        self.operators.clicked.connect(self.operator_checked)
        self.routes.clicked.connect(self.routes_checked)
        self.list.itemDoubleClicked.connect(self.list_item_selected)
        
        # Controls settings
        self.alternateScenario.setEnabled(False)
        
        # Loads combo-box controls
        self.__load_scenario_operators()
        self.__load_scenarios_combobox()
        self.__load_variable_combobox()
        self.__reload_scenarios()


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'matrix.html')
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
    
    def __load_scenarios_combobox(self):
        """
            @summary: Loads scenarios combo-box
        """
        self.network.load_network_scenarios(self.project['tranus_folder'])
        items = self.network.get_sorted_scenarios()
        if items is not None:
            self.base_scenario.addItems(items)
    
    def __load_alternate_scenario_combobox(self):
        """
            @summary: Loads alternate scenario combo-box
        """
        baseScenario = self.baseScenario.currentText()
        items = self.network.get_sorted_scenarios()
        for item in items:
            if item != baseScenario:
                self.alternateScenario.addItem(item)
    
    def __load_variable_combobox(self):
        self.project.network_model.load_dictionaries()
        items = self.project.network_model.get_sorted_variables()
        if items is None:
            QMessageBox.warning(None, "Variables", "There are no variables to load.")
            print ("There are no variables to load.")
        else:
            self.variablesList.addItems(items)
            
    def scenario_changed(self, newIndex):
        """
            @summary: Detects when an scenario was changed
        """
        if self.scenarioOperator.currentText() != '':
            self.alternateScenario.clear()
            self.__load_alternate_scenario_combobox()
    
    def scenario_operator_changed(self):
        """
            @summary: Detects when an operator was changed
        """
        currentOperator = self.scenarioOperator.currentText()
        if self.scenarioOperator.currentText() == '':
            self.alternateScenario.clear()
            self.alternateScenario.setEnabled(False)
        else:
            if len(self.alternateScenario) == 0:
                self.alternateScenario.setEnabled(True)
                self.alternateScenario.clear()
                self.__load_alternate_scenario_combobox()
    
    def __load_scenario_operators(self):
        """
            @summary: Loads operators combo-box
        """
        items = ["", "-"]
        self.scenarioOperator.addItems(items)
        
    def __reload_scenarios(self):
        """
            @summary: Reloads scenarios
        """
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)
    
    def total_checked(self):
        self.list.clear()
        self.expression.clear()
        self.expression.setEnabled(False)
        self.level = Level.Total
    
    def operator_checked(self):
        if self.operators.isChecked():
            self.list.clear()
            self.expression.clear()
            self.expression.setEnabled(True)
            self.network.load_operators(self.project['tranus_folder'], self.baseScenario.currentText())
            self.level = Level.Operators
            operators = self.network.get_operators_dictionary()
            if operators is not None:
                self.list.addItem("All")
                for key, value in operators.items():
                    self.list.addItem(str(key) + ' - ' + value)
            
    def routes_checked(self):
        if self.routes.isChecked():
            self.list.clear()
            self.expression.clear()
            self.expression.setEnabled(True)
            self.network.load_routes(self.project['tranus_folder'], self.baseScenario.currentText())
            self.level = Level.Routes
            routes = self.network.get_routes_dictionary()
            if routes is not None:
                self.list.addItem("All")

                for key, value in sorted(routes.items()):
                    self.list.addItem(str(key) + ' - ' + value)
        
    def list_item_selected(self, item):
        textToAdd = ''
        if item.text() == 'All':
            if self.level == Level.Operators:# self.operators.isChecked():
                itemsDic = self.network.get_operators_dictionary()
            
            if self.level == Level.Routes:#self.routes.isChecked():
                itemsDic = self.network.get_routes_dictionary()
            
            if itemsDic is not None:
                for value in itemsDic.values():
                    textToAdd = value if textToAdd.strip() == '' else textToAdd + ' + ' +  value
        else:
            posStrFound = item.text().find(" - ")
            textToAdd = item.text() if posStrFound == -1 else item.text()[posStrFound + 3:] 
            
        if self.expression.text().strip() == '':
            self.expression.setText(self.expression.text() + textToAdd)
        else:
            self.expression.setText(self.expression.text() + " + " + textToAdd)
    
    def __validate_data(self):
        """
            @summary: Fields validation
            @return: Validation result, matrixExpressionResult and sectorsExpression
        """
        scenariosExpression = []
        
        if self.layerName.text().strip() == '':
            QMessageBox.warning(None, "Layer Name", "Please write Layer Name.")
            print ("Please write Layer Name.")
            return False, None, None
        
        if self.expression.text().strip() == '' and (self.level is not Level.Total):#self.operators.isChecked() or self.routes.isChecked()):
            QMessageBox.warning(None, "Expression", "Please write an expression to be evaluated.")
            print ("Please write an expression to be evaluated.")
            return False, None, None
        
        #projectPath = self.project['tranus_folder'][0:max(self.project['tranus_folder'].rfind('\\'), self.project['tranus_folder'].rfind('/'))]
        
        # Base scenario
        if len(self.base_scenario) == 0:
            QMessageBox.warning(None, "Base Scenario", "There are no Base Scenarios loaded.")
            print ("There are no Base Scenarios loaded.")
            return False, None, None
        else:
            if self.baseScenario.currentText().strip() != '':
                scenariosExpression.append(str(self.baseScenario.currentText()))
            else:
                QMessageBox.warning(None, "Base Scenario", "Please select a Base Scenario.")
                print("Please select a Base Scenario.")
                return False, None, None
            
        # Validations for alternate scenario
        if self.scenarioOperator.currentText() != '':
            scenariosExpression.append(str(self.scenarioOperator.currentText()))
            if self.alternateScenario.currentText() == '':
                QMessageBox.warning(None, "Alternate Scenario", "Please select an Alternate Scenario.")
                print("Please select an Alternate Scenario.")
                return False, None, None
        
        
        if self.variablesList.currentText() == '':
            QMessageBox.warning(None, "Variable", "Please select a variable.")
            print ("Please write an expression to be evaluated.")
            return False, None, None
        
        scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
        
        if scenariosExpressionResult:
            if self.level == Level.Total:#self.total.isChecked():
                networkExpressionResult = True
                networkExpressionList = None
            else:
                networkExpressionResult, networkExpressionList = ExpressionData.validate_sectors_expression(self.expression.text().strip())
        
        if self.level is not Level.Total:# not self.total.isChecked():
            if scenariosExpressionStack.tp > 1 and len(networkExpressionList) > 1:
                QMessageBox.warning(None, "Expression", "Expression with conditionals only applies for one scenario.")
                print("Expression with conditionals only applies for one scenario.")
                return False, None, None
        
        return scenariosExpressionResult and networkExpressionResult, scenariosExpressionStack, networkExpressionList
        
    def create_layer(self):
        validationResult, scenariosExpression, networkExpression = self.__validate_data()
        if validationResult:
            self.network.addNetworkLayer(self.layerName.text(), scenariosExpression, networkExpression, self.variablesList.currentText(), self.level, self.project['tranus_folder'], self.project.get_layers_group(), self.project.network_link_shape_path)
            self.accept()
        else:
            print("New network layer was not created.")
        
        return True
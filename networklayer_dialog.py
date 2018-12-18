# -*- coding: utf-8 -*-
import os, re, webbrowser
from ast import literal_eval
from string import *

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QColor

from qgis.gui import QgsColorButton, QgsGradientColorRampDialog, QgsColorRampButton
from qgis.core import QgsGradientColorRamp, QgsProject

from .scenarios_model import ScenariosModel
from .classes.ExpressionData import ExpressionData
from .classes.network.Network import Network
from .classes.network.Level import *
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.FileManagement import FileManagement as FileM
from .classes.general.Helpers import Helpers as HP

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'networklayer.ui'))

class NetworkLayerDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None, layerId=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(NetworkLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.network = Network()
        self.level = None
        self.tempLayerName = ''
        self.tempExpression = ''
        self.layerId = layerId  
        self.labelColor = QLabel("Color") 
        self.buttonColorRamp = QgsColorRampButton(self, 'Color Ramp')
        self.buttonColorRamp.hide()
        self.buttonColor = QgsColorButton(self, 'Color')
        self.buttonColor.hide()
        #self.buttonColorRamp = QgsColorRampButton(self, 'Color Ramp')

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.layerName = self.findChild(QtWidgets.QLineEdit, 'layerName')
        self.expression = self.findChild(QtWidgets.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtWidgets.QComboBox, 'base_scenario')
        self.scenarioOperator = self.findChild(QtWidgets.QComboBox, name='cb_operator')
        self.alternateScenario = self.findChild(QtWidgets.QComboBox, name='cb_alternate_scenario')
        self.variablesList = self.findChild(QtWidgets.QComboBox, name='cb_variables')
        self.method = self.findChild(QtWidgets.QComboBox, name='cb_method')
        self.total = self.findChild(QtWidgets.QRadioButton, 'rbtn_total')
        self.operators = self.findChild(QtWidgets.QRadioButton, 'rbtn_operators')
        self.routes = self.findChild(QtWidgets.QRadioButton, 'rbtn_routes')
        self.list = self.findChild(QtWidgets.QListWidget, 'list')
        self.scenarios = self.findChild(QtWidgets.QTreeView, 'scenarios')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.progressBar = self.findChild(QtWidgets.QProgressBar, 'progressBar')
        

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layerName.keyPressEvent = self.keyPressEvent
        self.expression.keyPressEvent = self.expression_key_press_event
        self.buttonBox.accepted.connect(self.create_layer)
        self.scenarioOperator.currentIndexChanged[int].connect(self.scenario_operator_changed)
        self.baseScenario.currentIndexChanged[int].connect(self.scenario_changed)
        self.variablesList.currentIndexChanged[int].connect(self.variable_changed)
        self.method.currentIndexChanged[int].connect(self.method_changed)
        self.total.clicked.connect(self.total_checked)
        self.operators.clicked.connect(self.operator_checked)
        self.routes.clicked.connect(self.routes_checked)
        self.list.itemDoubleClicked.connect(self.list_item_selected)
        #self.color.clicked.connect(self.color_picker)
        
        # Controls settings
        self.alternateScenario.setEnabled(False)
        
        # Loads combo-box controls
        self.__load_scenario_operators()
        self.__load_scenarios_combobox()
        self.__load_variable_combobox()
        self.__reload_scenarios()

        if self.layerId:
            self.__load_default_data()

    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
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

    def method_changed(self, event):
        if self.method.currentText() == "Color":
            self.labelColor.setText("Color Ramp")    
            self.formLayout = self.findChild(QFormLayout, 'formLayout_4')
            self.formLayout.takeAt(10)
            self.buttonColor.hide()
            self.buttonColorRamp.show()
            self.buttonColorRamp.setShowGradientOnly(True)
            self.formLayout.addRow(self.labelColor, self.buttonColorRamp)
        elif self.method.currentText() == "Size":
            self.labelColor.setText("Color")    
            self.formLayout = self.findChild(QFormLayout, 'formLayout_4')
            self.formLayout.takeAt(10)
            self.buttonColorRamp.hide()
            self.buttonColor.show()
            self.formLayout.addRow(self.labelColor, self.buttonColor)
            
    def expression_key_press_event(self, event):
        """
            @summary: Detects when a key is pressed
            @param event: Key press event
            @type event: Event object
        """
        QtWidgets.QLineEdit.keyPressEvent(self.expression, event)
        if not self.invalid_expression_characters(event.text()):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network Expression", "Invalid character: " + event.text() + ".", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            if self.expression.isUndoAvailable():
                self.expression.setText(self.tempExpression)
        else:
            self.tempExpression = self.expression.text()
    
    def validate_string(self, input):
        """
            @summary: Validates invalid characters
            @param input: Input string
            @type input: String object
            @return: Result of the evaluation
        """
        pattern = re.compile('[\\\/\:\*\?\"\<\>\|]')
        if re.match(pattern, input) is None:
            return True
        else:
            return False

    def invalid_expression_characters(self, input):
        """
            @summary: Validates invalid characters
            @param input: Input string
            @type input: String object
            @return: Result of the evaluation
        """
        pattern = re.compile('[\\\/\:\*\-\<\>\|\=]')
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
        """
            @summary: Loads data to variable combo-box control
        """
        self.project.network_model.load_dictionaries()
        items = self.project.network_model.get_sorted_variables()
        if items is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Variables", "There are no variables to load.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
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

    def variable_changed(self, newIndex):
        """
            @summary: Detects when an scenario was changed
        """
        if self.variablesList.currentText() != '':
            method = HP.method_x_varible(self.variablesList.currentText())
            indexMethod = self.method.findText(method, Qt.MatchFixedString)
            self.method.setCurrentIndex(indexMethod)
    
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
        """
            @summary: Functionality when user click total radio button
        """
        self.list.clear()
        self.expression.clear()
        self.expression.setEnabled(False)
        self.level = Level.Total
    
    def operator_checked(self):
        """
            @summary: Functionality when user click operator radio button
        """
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
        """
            @summary: Functionality when user click routes radio button
        """
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
        """
            @summary: Selects item clicked from the list.
            @param item:  Item selected
            @type item: String
        """
        textToAdd = ''
        if item.text() == 'All':
            if self.level == Level.Operators:
                itemsDic = self.network.get_operators_dictionary()
            
            if self.level == Level.Routes:
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
            
        self.tempExpression = self.expression.text()
    
    def __validate_data(self):
        """
            @summary: Fields validation
            @return: Validation result, matrixExpressionResult and sectorsExpression
        """
        scenariosExpression = []
        
        if self.layerName.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Layer Name", "Please write Layer Name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write Layer Name.")
            return False, None, None, None
        
        if self.expression.text().strip() == '' and (self.level is not Level.Total):#self.operators.isChecked() or self.routes.isChecked()):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Expression", "Please write an expression to be evaluated.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write an expression to be evaluated.")
            return False, None, None, None
        
        # Base scenario
        if len(self.base_scenario) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Base Scenario", "There are no Base Scenarios loaded.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no Base Scenarios loaded.")
            return False, None, None, None
        else:
            if self.baseScenario.currentText().strip() != '':
                scenariosExpression.append(str(self.baseScenario.currentText()))
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Base Scenario", "Please select a Base Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select a Base Scenario.")
                return False, None, None, None
            
        # Validations for alternate scenario
        if self.scenarioOperator.currentText() != '':
            scenariosExpression.append(str(self.scenarioOperator.currentText()))
            if self.alternateScenario.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Alternate Scenario", "Please select an Alternate Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select an Alternate Scenario.")
                return False, None, None, None
            else:
                scenariosExpression.append(str(self.alternateScenario.currentText()))
        
        if self.variablesList.currentText() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Variable", "Please select a variable.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write an expression to be evaluated.")
            return False, None, None, None
        
        scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
        
        if scenariosExpressionResult:
            if self.level == Level.Total:
                networkExpressionResult = True
                networkExpressionList = None
            else:
                networkExpressionResult, networkExpressionList = ExpressionData.validate_sectors_expression(self.expression.text().strip())
        
        if self.level is not Level.Total:
            if scenariosExpressionStack.tp > 1 and len(networkExpressionList) > 1:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Expression", "Expression with conditionals only applies for one scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Expression with conditionals only applies for one scenario.")
                return False, None, None, None

        if self.method.currentText()=='Color' and self.buttonColorRamp.isNull():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Color Ramp", "Color Ramp is required.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Color Ramp is NULL.")
            return False, None, None, None
        elif self.method.currentText()=='Size' and self.buttonColor.isNull():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Color", "Color is required.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Color is NULL.")
            return False, None, None, None

        return scenariosExpressionResult and networkExpressionResult, scenariosExpressionStack, networkExpressionList, self.expression.text()
      

    def create_layer(self):
        """
            @summary: Method that creates new network layer.
            @return: Result of the process
        """
        validationResult, scenariosExpression, networkExpression, expressionNetworkText = self.__validate_data()

        if validationResult:
            self.progressBar.show()
            self.progressBar.setValue(10)
            if self.method.currentText()=="Size":
                color = self.buttonColor.color()
                color = color.rgb()
            elif self.method.currentText()=="Color":
                color = self.buttonColorRamp.colorRamp()
                color = color.properties()

            # Set Custom Project Variable to save Project path
            projectPath = self.project.network_link_shape_path[0:max(self.project.network_link_shape_path.rfind('\\'), self.project.network_link_shape_path.rfind('/'))]
            tranus_dictionary = dict(project_qtranus_folder=projectPath, project_qtranus_network_shape=self.project.network_link_shape_path)
            self.project.custom_variables_dict.update(tranus_dictionary)
            QgsProject.instance().setCustomVariables(self.project.custom_variables_dict)

            if not self.layerId: 
                result = self.network.addNetworkLayer(self.progressBar, self.layerName.text(), scenariosExpression, networkExpression, self.variablesList.currentText(), self.level, self.project['tranus_folder'], self.project.get_layers_group(), self.project.network_link_shape_path, self.method.currentText(), expressionNetworkText, color)
            else:
                result = self.network.editNetworkLayer(self.progressBar, self.layerName.text(), scenariosExpression, networkExpression, self.variablesList.currentText(), self.level, self.project['tranus_folder'], self.project.get_layers_group(), self.project.network_link_shape_path, self.method.currentText(), self.layerId, expressionNetworkText, color)
            
            if not result:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network", "Could not create network layer.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                self.project['network_links_shape_file_path'] = ''
                self.project['network_links_shape_id'] = ''

            self.accept()
        else:
            print("New network layer was not created.")
        #print("Color Ramp {} ".format(self.buttonColorRamp.colorRampName()))
        return True

    # Load data to edit the zones layer
    def __load_default_data(self):
        projectPath = self.project.shape[0:max(self.project.shape.rfind('\\'), self.project.shape.rfind('/'))]
        
        # Get data from XML File with the parameters
        expression, field, name, scenario, fieldName, method, level, color = FileM.find_layer_data(projectPath, self.layerId)
        
        self.layerName.setText(name)
        
        if level == "1":
            self.total.click()
            self.rbtn_total.setChecked(True)
        elif level == "2":
            self.rbtn_operators.setChecked(True)
            self.operators.click()
        elif level == "3":
            self.rbtn_routes.setChecked(True)
            self.routes.click()
        
        self.expression.setText(expression)
        
        scenario = scenario.split(",")
        scenario[0] = scenario[0].replace("'", "").replace("[", "").replace("]", "")

        indexBaseScenario = self.base_scenario.findText(scenario[0], Qt.MatchFixedString)
        self.base_scenario.setCurrentIndex(indexBaseScenario)

        indexVariable = self.variablesList.findText(field, Qt.MatchFixedString)
        self.variablesList.setCurrentIndex(indexVariable)

        indexMethod = self.method.findText(method, Qt.MatchFixedString)
        self.method.setCurrentIndex(indexMethod)

        if method == 'Size':
            qcolor = QColor()
            qcolor.setRgb(int(color))
            self.buttonColor.setColor(qcolor)
            
        if method == 'Color':
            color = literal_eval(color)
            arrColor1 = color['color1'].split(",")
            arrColor2 = color['color2'].split(",")
            arrColor1 = list(map(lambda x:int(x),arrColor1))
            arrColor2 = list(map(lambda x:int(x),arrColor2))

            qcolor1 = QColor(arrColor1[0], arrColor1[1], arrColor1[2])
            qcolor2 = QColor(arrColor2[0], arrColor2[1], arrColor2[2])

            qColorRamp = QgsGradientColorRamp()
            qColorRamp.setColor1(qcolor1)
            qColorRamp.setColor2(qcolor2)
            self.buttonColorRamp.setColorRamp(qColorRamp)

        if len(scenario) == 3:           
            scenario[2] = scenario[2].replace("'", "").replace("]", "").strip()
            indexOperators = self.scenarioOperator.findText(scenario[2] , Qt.MatchFixedString)
            self.scenarioOperator.setCurrentIndex(indexOperators)
            
            scenario[1] = scenario[1].replace("'", "").strip()
            indexAlternateScenario = self.alternateScenario.findText(scenario[1], Qt.MatchFixedString)
            self.alternateScenario.setCurrentIndex(indexAlternateScenario)

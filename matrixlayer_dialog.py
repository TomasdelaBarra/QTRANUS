# -*- coding: utf-8 -*-
import os, re, csv, webbrowser
from PyQt4 import QtGui, uic
from classes.general.QTranusMessageBox import QTranusMessageBox
from PyQt4.QtCore import *
from .scenarios_model import ScenariosModel
from qgis.core import QgsProject
from classes.ExpressionData import ExpressionData 

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'matrixlayer.ui'))

class MatrixLayerDialog(QtGui.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        super(MatrixLayerDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.project = parent.project
        self.proj = QgsProject.instance()
        self.tempLayerName = ''
        
        # Linking objects with controls
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.layerName = self.findChild(QtGui.QLineEdit, 'layerName')
        self.expression = self.findChild(QtGui.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.operators = self.findChild(QtGui.QComboBox, name='cb_operator')
        self.alternateScenario = self.findChild(QtGui.QComboBox, name='cb_alternate_scenario')
        self.originList = self.findChild(QtGui.QListWidget, name='lw_origin')
        self.originList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.destinationList = self.findChild(QtGui.QListWidget, name='lw_destination')
        self.destinationList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.filter = self.findChildren(QtGui.QLineEdit, name='filter')
        self.categories = self.findChild(QtGui.QListWidget, 'categories')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layerName.keyPressEvent = self.keyPressEvent
        self.buttonBox.accepted.connect(self.create_layer)
        self.operators.currentIndexChanged[int].connect(self.operator_changed)
        self.baseScenario.currentIndexChanged[int].connect(self.scenario_changed)
        self.categories.itemDoubleClicked.connect(self.category_selected)
        
        # Controls settings
        self.alternateScenario.setEnabled(False)
        
        # Loads combo-box controls
        self.__load_operators()
        self.__load_scenarios_combobox()
        self.__load_zone_lists()
        self.__load_categories()
        #self.__load_centroids()
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
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Layer Name", "Invalid character: " + event.text() + ".", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
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
    
    def __load_scenarios_combobox(self):
        """
            @summary: Loads scenarios combo-box
        """
        items = self.project.map_data.get_sorted_scenarios()
        self.base_scenario.addItems(items)
    
    def __load_alternate_scenario_combobox(self):
        """
            @summary: Loads alternate scenario combo-box
        """
        baseScenario = self.baseScenario.currentText()
        items = self.project.map_data.get_sorted_scenarios()
        for item in items:
            if item != baseScenario:
                self.alternateScenario.addItem(item)
    
    def scenario_changed(self, newIndex):
        """
            @summary: Detects when an scenario was changed
        """
        if self.operators.currentText() != '':
            self.alternateScenario.clear()
            self.__load_alternate_scenario_combobox()
    
    def operator_changed(self):
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
    
    def __load_operators(self):
        """
            @summary: Loads operators combo-box
        """
        items = ["", "-", "/"]
        self.operators.addItems(items)
    
    def __reload_scenarios(self):
        """
            @summary: Reloads scenarios
        """
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)
        
    def __load_zone_lists(self):
        """
            @summary: Loads zones lists
        """
        items = self.project.map_data.get_matrix_zones()
        if items is not None:
            self.originList.addItem("All")
            self.originList.addItems(items)
            self.destinationList.addItem("All")
            self.destinationList.addItems(items)
    
    def __load_categories(self):
        """
            @summary: Loads categories list
        """
        items = self.project.map_data.get_matrix_categories()
        if items is not None:
            self.categories.addItem("All")
            self.categories.addItems(items)

    def __load_centroids(self):
        """
            @summary: Loads centroids layer
        """
        if not self.project.centroids_file_path is None:
            self.project.load_zones_centroids_data()
        else:
            self.__create_centroids_file()
    
    def __create_centroids_file(self):
        """
            @summary: Creates centroids file
        """
        self.project.load_zones_centroids()
    
    def create_layer(self):
        """
            @summary: Creates matrix layer
        """
        validationResult, scenariosExpression, matrixExpression = self.__validate_data() 
        if validationResult:
            originZones = []
            destinationZones = []
            
            allOrigins = next((item for item in self.originList.selectedItems() if item.text() == 'All'), None)
            allDestinations = next((item for item in self.destinationList.selectedItems() if item.text() == 'All'), None)
            
            if allOrigins is None:
                for item in self.originList.selectedItems():
                    originZones.append(item.text())
            else:
                for index in xrange(self.originList.count()):
                    if self.originList.item(index).text() != 'All':
                        originZones.append(self.originList.item(index).text())
            
            if allDestinations is None:
                for item in self.destinationList.selectedItems():
                    destinationZones.append(item.text())
            else:
                for index in xrange(self.destinationList.count()):
                    if self.destinationList.item(index).text() != 'All':
                        destinationZones.append(self.destinationList.item(index).text())
            
            self.project.addMatrixLayer(self.layerName.text(), scenariosExpression, originZones, destinationZones, matrixExpression)
            self.accept()
        else:
            #QMessageBox.critical(None, "New Layer", "New layer was not created.")
            print("New matrix layer was not created.")
            
    def category_selected(self, item):
        """
            @summary: Detects when an item in the list is double clicked
            @param item: Item selected
            @type item: QListWidget item 
        """
        
        textToAdd = ''
        if item.text() == 'All':
            for index in range(1, self.categories.count()):
                textToAdd = self.categories.item(index).text() if textToAdd.strip() == '' else textToAdd + ' + ' +  self.categories.item(index).text()
        else:
            textToAdd = item.text()
            
        if self.expression.text().strip() == '':
            self.expression.setText(self.expression.text() + textToAdd)
        else:
            self.expression.setText(self.expression.text() + " + " + textToAdd)
        
    def __validate_matrix_scenario(self, scenario):
        """
            @summary: Validates the format of the file
            @param scenario: Scenario Id
            @type scenario: String
        """
        if len(self.project.map_data.trip_matrices) > 0:
            for trip in self.project.map_data.trip_matrices:
                if trip.Id == scenario:
                    if len(trip.tripMatrix.dtype) != 7:
                        messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Matrix Scenario", "Scenario " + scenario + ", has an incorrect format.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                        messagebox.exec_()
                        print ("Scenario {0}, has an incorrect format.").format(scenario)
                        return False
                    else:
                        return True
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Matrix Scenario", "There are not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print ("Matrix Scenario", "There are not scenarios information.")
            return False 
        
    def __validate_data(self):
        """
            @summary: Fields validation
            @return: Validation result, matrixExpressionResult and sectorsExpression
        """
        scenariosExpression = []
        
        if self.layerName.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Layer Name", "Please write Layer Name.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write Layer Name.")
            return False, None, None
        
        if self.expression.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Expression", "Please write an expression to be evaluated.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please write an expression to be evaluated.")
            return False, None, None
        
        projectPath = self.project.shape[0:max(self.project.shape.rfind('\\'), self.project.shape.rfind('/'))]
        
        if len(self.base_scenario) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Base Scenario", "There are no Base Scenarios loaded.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no Base Scenarios loaded.")
            return False, None, None
        else:
            if self.project.load_map_trip_structure(projectPath, self.baseScenario.currentText()):
                if self.__validate_matrix_scenario(self.baseScenario.currentText()) == False:
                    return False, None, None
                scenariosExpression.append(str(self.baseScenario.currentText()))
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Base Scenario", "Selected Base Scenario has no information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                messagebox.exec_()
                print ("Selected Base Scenario has no information.")
                return False, None, None
            
        # Validations for alternate scenario
        if self.operators.currentText() != '':
            scenariosExpression.append(str(self.operators.currentText()))
            if self.alternateScenario.currentText() == '':
                messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Alternate Scenario", "Please select an Alternate Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select an Alternate Scenario.")
                return False, None, None
            else:
                if self.project.load_map_trip_structure(projectPath, self.alternateScenario.currentText()):
                    if self.__validate_matrix_scenario(self.alternateScenario.currentText()) == False:
                        return False, None, None
                    scenariosExpression.append(str(self.alternateScenario.currentText()))
                else:
                    messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Alternate Scenario", "Selected Alternate Scenario has no information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                    messagebox.exec_()
                    print ("Selected Alternate Scenario has no information.")
                    return False, None, None
        
        originSelectedCounter = len(self.originList.selectedItems())
        destinationSelectedCounter = len(self.destinationList.selectedItems())
        if originSelectedCounter == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Origin Zones", "Please select at least one origin zone.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please select at least one origin zone.")
            return False, None, None
        
        if destinationSelectedCounter == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Destination Zones", "Please select at least one destination zone.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print ("Please select at least one destination zone.")
            return False, None, None
        
        if originSelectedCounter == 1 and destinationSelectedCounter == 1:
            if self.originList.selectedItems()[0].text() == self.destinationList.selectedItems()[0].text():
                if self.originList.selectedItems()[0].text() != "All":
                    messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Zones", "You must select different origin and destination.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                    messagebox.exec_()
                    print ("You must select different origin and destination.")
                    return False, None, None
        
        scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
        
        if scenariosExpressionResult:
            matrixExpressionResult, matrixExpressionList = ExpressionData.validate_sectors_expression(self.expression.text().strip())
        
        if scenariosExpressionStack.tp > 1 and len(matrixExpressionList) > 1:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Expression", "Expression with conditionals only applies for one scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Expression with conditionals only applies for one scenario.")
            return False, None, None
        
        return scenariosExpressionResult and matrixExpressionResult, scenariosExpressionStack, matrixExpressionList
    
import os, re, csv
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from .scenarios_model import ScenariosModel
from qgis.core import QgsProject 

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
        self.scale = self.findChildren(QtGui.QLineEdit, name='scale')
        self.categories = self.findChild(QtGui.QListWidget, 'categories')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.layerName.keyPressEvent = self.keyPressEvent
        self.buttonBox.accepted.connect(self.ready)
        #self.baseScenario.connect(self.baseScenario,SIGNAL("currentIndexChanged(int)"),self.scenario_changed)
        self.baseScenario.currentIndexChanged[int].connect(self.scenario_changed)
        self.categories.itemDoubleClicked.connect(self.category_selected)
        
        # Loads combo-box controls
        self.__load_operators()
        self.__load_scenarios_combobox()
        self.__load_zone_lists()
        self.__load_categories()
        self.__load_centroids()
        self.reload_scenarios()
        
    #def __load_matrix_data(self):
        
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
    
    def __load_operators(self):
        """
            @summary: Loads operators combo-box
        """
        items = ["+"]
        self.operators.addItems(items)
    
    def reload_scenarios(self):
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
            self.originList.addItems(items)
            self.destinationList.addItems(items)
    
    def __load_categories(self):
        """
            @summary: Loads categories list
        """
        items = self.project.map_data.get_matrix_categories()
        if items is not None:
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
    
    def ready(self):
        pass
            
    def category_selected(self, item):
        """
            @summary: Detects when an item in the list is double clicked
            @param item: Item selected
            @type item: QListWidget item 
        """
        self.expression.setText(self.expression.text() + item.text())
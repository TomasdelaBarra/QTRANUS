# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *

from qgis.core import QgsMessageLog, QgsProject, QgsVectorLayer, QgsFields, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo, QgsProject, QgsMapUnitScale, QgsSimpleLineSymbolLayer, QgsLineSymbol, QgsPointXY

from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.node.Node import Node
from .classes.general.Helpers import Helpers
from .classes.general.Validators import * # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .scenarios_model_sqlite import ScenariosModelSqlite

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_node.ui'))

class AddNodeDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, idScenario = None, parent = None, codeNode=None, nodeShapeFields=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddNodeDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.codeNode = codeNode
        self.tranus_folder = tranus_folder
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder )
        self.node_shape_fields = nodeShapeFields if nodeShapeFields else None
        print("Dentrod de ADD NODE", self.node_shape_fields)
        self.idScenario = idScenario
        resolution_dict = Helpers.screenResolution(40)
        self.resize(resolution_dict['width'], resolution_dict['height'])


        # Linking objects with controls
        self.id = self.findChild(QtWidgets.QLineEdit, 'id')
        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.description = self.findChild(QtWidgets.QLineEdit, 'description')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenario_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.cb_type = self.findChild(QtWidgets.QComboBox, 'cb_type')
        self.le_x = self.findChild(QtWidgets.QLineEdit, 'le_x')
        self.le_y = self.findChild(QtWidgets.QLineEdit, 'le_y')

        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_new_node)

        # Validations
        self.id.setValidator(validatorExpr('integer'))
        self.id.textChanged.connect(self.check_state)
        """
        self.name.setValidator(validatorExpr('alphaNum'))
        self.name.textChanged.connect(self.check_state)
        self.description.setValidator(validatorExpr('alphaNum'))
        self.description.textChanged.connect(self.check_state)
        """
        self.name.setMaxLength(10)
        self.description.setMaxLength(55)
        self.le_x.setMaxLength(10)
        self.le_y.setMaxLength(10)
        
        self.__load_cb_type()
        #Loads
        self.__get_scenarios_data()
        self.__loadId()

        if self.codeNode is not None:
            self.setWindowTitle("Edit Node")
            self.load_default_data()


    def __loadId(self):
        if self.codeNode is None:
            self.id.setText(str(self.dataBaseSqlite.maxIdTable(" node "))) 


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = scenarioData[0][0]
        #self.load_default_data()


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


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)

    def save_new_node(self):
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
        if self.idScenario is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Plese Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please write id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.dataBaseSqlite.validateId('node', self.id.text()) is False and self.codeNode is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Node", "Please write an id valid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        """if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please write the name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please write the description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False"""

        if self.le_x is None or self.le_x.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please Write X", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if not validatorRegex(self.le_x.text(), 'real-negative'):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Field x permit only numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.le_y is None or self.le_y.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please Write Y", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if not validatorRegex(self.le_y.text(), 'real-negative'):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Field y permit only numbers", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        id_type = self.cb_type.itemData(self.cb_type.currentIndex())
        name = self.name.text() if self.name.text() else None
        description = self.description.text() if self.description.text() else None
        
        if self.codeNode is None:
            newNode = self.dataBaseSqlite.addNode(scenarios, self.id.text(), id_type, name, description, self.le_x.text(),  self.le_y.text())
            if newNode:
                project = QgsProject.instance()
                layerIds = [layer.id() for layer in project.mapLayers().values()]
                layerId = [ value for value in layerIds if re.match('Network_Nodes',value)][0]
                if not Node.addNodeFeatureShape(layerId, self.le_x.text(), self.le_y.text(), self.id.text(), name, id_type, nodeShapeFields=self.node_shape_fields):
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_() 
                    return False
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_() 
                return False
        else:
            newNode = self.dataBaseSqlite.updateNode(scenarios, self.id.text(), id_type, self.name.text(), self.description.text(), self.le_x.text(),  self.le_y.text())

        if newNode is not None:
            self.parent().load_scenarios()
            self.accept()
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Node", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        return True


    def load_scenarios(self):
        self.__get_scenarios_data()


    def __load_cb_type(self):
        types = ['Internal', 'External','Node']
        self.cb_type.clear()
        for index, valor in enumerate(types):
            self.cb_type.addItem(valor, index+1)


    def load_default_data(self):
        types = ['Internal', 'External','Node']
        data = self.dataBaseSqlite.selectAll('node', ' where id = {}'.format(self.codeNode), columns= "id, id_type, name, description, x, y")

        indexType = self.cb_type.findText(types[data[0][1]-1])
        self.cb_type.setCurrentIndex(indexType)

        self.id.setText(str(data[0][0]))
        self.name.setText(str(data[0][2]) if data[0][2] else '')
        self.description.setText(str(data[0][3]) if data[0][3] else '')
        self.le_x.setText(Helpers.decimalFormat(str(data[0][4])))
        self.le_y.setText(Helpers.decimalFormat(str(data[0][5])))


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
# -*- coding: utf-8 -*-
import os, webbrowser
from PyQt5 import QtWidgets, uic
from PyQt5.Qt import QAbstractItemView, QStandardItemModel, QStandardItem, QMainWindow, QToolBar, QHBoxLayout
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from qgis.core import QgsProject
from qgis.utils import iface


from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Helpers import Helpers
from .scenarios_model import ScenariosModel 
from .zonelayer_dialog import ZoneLayerDialog
from .matrixlayer_dialog import MatrixLayerDialog
from .networklayer_dialog import NetworkLayerDialog
from .scenarios_model_sqlite import ScenariosModelSqlite

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'results.ui'))

class ResultsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent = None):
        super(ResultsDialog, self).__init__(parent)
        self.setupUi(self)
        # Resize Dialog for high resolution monitor
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], resolution_dict['height'])
        self.tranus_folder = tranus_folder
        self.project = parent.project
        
        self.plugin_dir = os.path.dirname(__file__)
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.button_box = self.findChild(QtWidgets.QDialogButtonBox, 'button_box')
        self.layer_zone = self.findChild(QtWidgets.QListWidget, 'layerZone')
        self.layer_network = self.findChild(QtWidgets.QListWidget, 'layerNetwork')
        self.layer_matrix = self.findChild(QtWidgets.QListWidget, 'layerMatrix')
        self.zones_btn = self.findChild(QtWidgets.QCommandLinkButton, 'zones')
        self.network_btn = self.findChild(QtWidgets.QCommandLinkButton, 'network')
        self.matrix_btn = self.findChild(QtWidgets.QCommandLinkButton, 'matrix')
        self.scenarios = self.findChild(QtWidgets.QTreeView, 'scenarios')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layer_zone.installEventFilter(self)
        self.layer_network.installEventFilter(self)
        self.layer_matrix.installEventFilter(self)
        self.zones_btn.clicked.connect(self.zone_layer_dialog)
        self.network_btn.clicked.connect(self.network_layer_dialog)
        self.matrix_btn.clicked.connect(self.matrix_layer_dialog)
        
        # Loads
        #self.__reload_scenarios()
        self.__load_scenarios()
        self.__load_layers_list()
            
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'results.html')
        webbrowser.open_new_tab(filename)
    
    """def __reload_scenarios(self):
       
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)"""


    def __load_scenarios(self):

        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenarios.setSelectionModel(modelSelection)
    
    def __load_layers_list(self):
        """
            @summary: Reloads List Layers
        """
        for valor in ['zones', 'network', 'matrix']:
            lstLayers = self.project.getLayers(valor)
            if valor == 'zones':
                self.layer_zone.clear()
            elif valor == 'network':
                self.layer_network.clear()
            elif valor == 'matrix':
                self.layer_matrix.clear()

            for i in lstLayers:
                item = QtWidgets.QListWidgetItem()
                item.setData(11, i['id'])
                item.setText(i['text'])
                if valor == 'zones':
                    self.layer_zone.addItem(item)
                if valor == 'network':
                    self.layer_network.addItem(item)
                if valor == 'matrix':
                    self.layer_matrix.addItem(item)


    def zone_layer_dialog(self):
        """
            @summary: Opens zone layer window
        """
        if self.project.map_data.get_sorted_fields() is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no fields to load, please reload SHP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no fields to load, please reload SHP file.")
        else:
            self.zones_dialog = ZoneLayerDialog(self.tranus_folder, parent=self)
            self.zones_dialog.show()
            result = self.zones_dialog.exec_()
            self.__load_layers_list()


    def eventFilter(self, source, event):
        """
            @summary: EventFilter to filter Right Click
        """
        if (event.type() == QtCore.QEvent.ContextMenu and (source is self.layer_zone or source is self.layer_network or source is self.layer_matrix)):
            menu = QtWidgets.QMenu()
            openLayer = menu.addAction(QIcon(self.plugin_dir+"/icons/open-layer.svg"),'Open Layer')
            editLayer = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"), 'Edit Layer')
            deleteLayer = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-layer.svg"),'Delete Layer')
            action = menu.exec_(event.globalPos())

            if action == editLayer:
                item = source.itemAt(event.pos())
                layerId = item.data(11)
                print(f"Layer ID:  {layerId}")
                dialog = ZoneLayerDialog(parent=self,layerId=layerId) if source is self.layer_zone else NetworkLayerDialog(parent=self, layerId=layerId) if source is self.layer_network else MatrixLayerDialog(parent=self, layerId=layerId)
                dialog.show()
                result = dialog.exec_()
                if result==1:
                    self.close()
            elif action == deleteLayer:
                item = source.itemAt(event.pos())
                layerId = item.data(11)
                QgsProject.instance().removeMapLayers([layerId])
                self.__load_layers_list()
            elif action == openLayer:
                item = source.itemAt(event.pos())
                layerId = item.data(11)
                registry = QgsProject.instance()
                layer = registry.mapLayer(layerId)
                iface.setActiveLayer(layer)
                self.close()
            return True
        return super(ResultsDialog, self).eventFilter(source, event)

    def matrix_layer_dialog(self):
        """
            @summary: Opens matrix layer window 
        """
        if self.project.map_data.get_sorted_fields() is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no fields to load, please reload SHP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            
            print ("There are no fields to load, please reload SHP file.")
        else:
            dialog = MatrixLayerDialog(self.tranus_folder, parent = self)
            dialog.show()
            result = dialog.exec_()
            self.__load_layers_list()

    def network_layer_dialog(self):
        """
            @summary: Opens network layer window 
        """
        if self.project.network_link_shape_path is None or self.project.network_link_shape_path.strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network Shape File", "Please select a network link shape file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

            print ("Please select a network link shape file.")
        else:
            dialog = NetworkLayerDialog(self.tranus_folder, parent = self)
            dialog.show()
            result = dialog.exec_()
            self.__load_layers_list()
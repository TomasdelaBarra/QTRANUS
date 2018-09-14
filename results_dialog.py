# -*- coding: utf-8 -*-
import os, webbrowser
from PyQt5 import QtWidgets, uic
from PyQt5 import QtWidgets

from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model import ScenariosModel 
from .zonelayer_dialog import ZoneLayerDialog
from .matrixlayer_dialog import MatrixLayerDialog
from .networklayer_dialog import NetworkLayerDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'results.ui'))

class ResultsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        super(ResultsDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.button_box = self.findChild(QtWidgets.QDialogButtonBox, 'button_box')
        self.zones_btn = self.findChild(QtWidgets.QCommandLinkButton, 'zones')
        #self.matrix_btn = self.findChild(QtWidgets.QCommandLinkButton, 'matrix')
        #self.network_btn = self.findChild(QtWidgets.QCommandLinkButton, 'network')
        self.scenarios = self.findChild(QtWidgets.QTreeView, 'scenarios')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.zones_btn.clicked.connect(self.zone_layer_dialog)
        #self.matrix_btn.clicked.connect(self.matrix_layer_dialog)
        #self.network_btn.clicked.connect(self.network_layer_dialog)
        
        # Loads
        self.__reload_scenarios()
        
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'results.html')
        webbrowser.open_new_tab(filename)
    
    def __reload_scenarios(self):
        """
            @summary: Reloads scenarios
        """
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)
    
    def zone_layer_dialog(self):
        """
            @summary: Opens zone layer window
        """
        if self.project.map_data.get_sorted_fields() is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no fields to load, please reload SHP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There are no fields to load, please reload SHP file.")
        else:
            dialog = ZoneLayerDialog(parent=self)
            dialog.show()
            result = dialog.exec_()

    def matrix_layer_dialog(self):
        """
            @summary: Opens matrix layer window 
        """
        if self.project.map_data.get_sorted_fields() is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Fields", "There are no fields to load, please reload SHP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            
            print ("There are no fields to load, please reload SHP file.")
        else:
            dialog = MatrixLayerDialog(parent = self)
            dialog.show()
            result = dialog.exec_()

    def network_layer_dialog(self):
        """
            @summary: Opens network layer window 
        """
        if self.project.network_link_shape_path is None or self.project.network_link_shape_path.strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network Shape File", "Please select a network link shape file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

            print ("Please select a network link shape file.")
        else:
            dialog = NetworkLayerDialog(parent = self)
            dialog.show()
            result = dialog.exec_()
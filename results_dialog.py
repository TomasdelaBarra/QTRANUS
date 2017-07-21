# -*- coding: utf-8 -*-
import os, webbrowser
from PyQt4 import QtGui, uic
from PyQt4.Qt import QMessageBox

from .scenarios_model import ScenariosModel 
from .zonelayer_dialog import ZoneLayerDialog
from .matrixlayer_dialog import MatrixLayerDialog
from .networklayer_dialog import NetworkLayerDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'results.ui'))

class ResultsDialog(QtGui.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        super(ResultsDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        
        # Linking objects with controls
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.button_box = self.findChild(QtGui.QDialogButtonBox, 'button_box')
        self.zones_btn = self.findChild(QtGui.QCommandLinkButton, 'zones')
        self.matrix_btn = self.findChild(QtGui.QCommandLinkButton, 'matrix')
        self.network_btn = self.findChild(QtGui.QCommandLinkButton, 'network')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.zones_btn.clicked.connect(self.zone_layer_dialog)
        self.matrix_btn.clicked.connect(self.matrix_layer_dialog)
        self.network_btn.clicked.connect(self.network_layer_dialog)
        
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
            QMessageBox.warning(None, "Fields", "There are no fields to load, please reload SHP file.")
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
            QMessageBox.warning(None, "Fields", "There are no fields to load, please reload SHP file.")
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
            messagebox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Network Shape File", "Please select a network link shape file", buttons = QtGui.QMessageBox.Ok, parent=self)
            messagebox.setWindowIcon(QtGui.QIcon(":/plugins/QTranus/icon.png"))
            messagebox.exec_()

            print ("Please select a network link shape file.")
        else:
            dialog = NetworkLayerDialog(parent = self)
            dialog.show()
            result = dialog.exec_()
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QTranusDialog
                                 A QGIS plugin
 qtranus
                             -------------------
        begin                : 2015-07-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by qtranus
        Collaborators        : Tomas de la Barra    - delabarra@gmail.com
                               Omar Valladolid      - omar.valladolidg@gmail.com
                               Pedro Buron          - pedroburonv@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, webbrowser


from PyQt4 import QtGui, uic
from PyQt4.Qt import QMessageBox

#from .settings_dialog import SettingsDialog
from .zonelayer_dialog import ZoneLayerDialog
from .scenarios_model import ScenariosModel
from .matrixlayer_dialog import MatrixLayerDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qtranus_dialog_base.ui'))

class QTranusDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, project, parent=None):
        """Constructor."""
        super(QTranusDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.project = project

        # Linking objects with controls
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.layers_group_name = self.findChild(QtGui.QLineEdit, 'layers_group_name')
        self.tranus_folder = self.findChild(QtGui.QLineEdit, 'tranus_folder')
        self.zone_shape = self.findChild(QtGui.QLineEdit, 'zone_shape')
        self.net_shape = self.findChild(QtGui.QLineEdit, 'net_shape')
        self.centroid_shape = self.findChild(QtGui.QLineEdit, 'centroid_shape')
        self.button_box = self.findChild(QtGui.QDialogButtonBox, 'button_box')
        self.zones_btn = self.findChild(QtGui.QCommandLinkButton, 'zones')
        self.matrix_btn = self.findChild(QtGui.QCommandLinkButton, 'matrix')
        self.tranus_folder_btn = self.findChild(QtGui.QToolButton, 'tranus_folder_btn')
        self.zones_shape_btn = self.findChild(QtGui.QToolButton, 'zones_shape_btn')
        self.net_shape_btn = self.findChild(QtGui.QToolButton, 'net_shape_btn')
        self.centroid_shape_btn = self.findChild(QtGui.QToolButton, 'centroid_shape_btn')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.zones_shape_fields = self.findChild(QtGui.QComboBox, 'cb_zones_shape_fields')
        
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layers_group_name.textEdited.connect(self.save_layers_group_name)
        self.zones_btn.clicked.connect(self.zone_layer_dialog)
        self.matrix_btn.clicked.connect(self.matrix_layer_dialog)
        self.tranus_folder_btn.clicked.connect(self.select_tranus_folder)
        self.zones_shape_btn.clicked.connect(self.select_shape(self.select_zones_shape))
        self.centroid_shape_btn.clicked.connect(self.select_centroid_shape_file(self.select_centroid_shape))
        self.zones_shape_fields.currentIndexChanged[int].connect(self.zones_shape_fields_changed)
        
        # Loads
        self.reload_scenarios()
	
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'index.html')
        webbrowser.open_new_tab(filename)
    	
    def save_layers_group_name(self):
        """
            @summary: Saves layer group name
        """
        self.project['project_name'] = self.layers_group_name.text()
        self.check_configure()

    def select_zones_shape(self, file_name):
        """
            @summary: Loads selected zone shape file
            @param file_name: Path and name of the shape file
            @type file_name: String
        """
        result, zoneShapeFieldNames = self.project.load_zones_shape(file_name) 
        if result:
            self.zone_shape.setText(file_name)
            self.load_zone_shape_fields(zoneShapeFieldNames)
        else:
            self.zone_shape.setText('')
        self.check_configure()
        
    def select_centroid_shape(self, file_name):
        """
            @summary: Loads selected centroid shape file
            @param file_name: Path and name of the shape file
            @type file_name: String
        """
        result = self.project.load_centroid_file(file_name)
        if result:
            self.centroid_shape.setText(file_name)
        else:
            self.centroid_shape.setText('')

    def select_tranus_folder(self):
        """
            @summary: Sets selected Tranus workspace
        """
        folder = QtGui.QFileDialog.getExistingDirectory(self, "Select directory")
        if folder:
            self.tranus_folder.setText(folder)
            if not self.project.load_tranus_folder(folder):
                self.tranus_folder.setText('')
            self.reload_scenarios()
        self.check_configure()

    def select_shape(self, callback):
        """
            @summary: Opens selected zone shape file
        """
        def select_file():
            file_name = QtGui.QFileDialog.getOpenFileName(parent=self, caption="Select file", filter="*.*, *.shp")
            if file_name:
                callback(file_name)

        return select_file
    
    def select_centroid_shape_file(self, callback):
        """
            @summary: Opens selected centroid shape file
        """
        def select_file():
            file_name = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Select file', directory='', filter='*.*, *.shp')
            if file_name:
                callback(file_name)
        
        return select_file

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

    def show(self):
        """
            @summary: Opens dialog window
        """
        self.project.load()
        if self.project['project_name']:
            self.layers_group_name.setText(self.project['project_name'])
        else:
            self.layers_group_name.setText('QTranus Project')
            self.layers_group_name.selectAll()
        if self.project['zones_shape']:
            self.zone_shape.setText(self.project['zones_shape'])
        if self.project.tranus_project:
            self.tranus_folder.setText(self.project.tranus_project.path)
        self.check_configure()
        super(QTranusDialog, self).show()

    def close(self):
        """
            @summary: Closes the main window
        """
        pass

    def reload_scenarios(self):
        """
            @summary: Reloads scenarios
        """        
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)

    def check_configure(self):
        """
            @summary: Validates configuration
        """
        self.zones_btn.setEnabled(self.project.is_valid())
        self.matrix_btn.setEnabled(self.project.is_valid())

    def load_zone_shape_fields(self, fields):
        """
            @summary: Loads zone shape fields combo
            @param fields: Zone shape fields
            @type fields: List object
        """
        
        if fields is None:
            QMessageBox.warning(None, "Zone Shape Fields", "There are no fields to load.")
            print ("There are no fields to load.")
        else:
            print(fields)
            self.zones_shape_fields.setEnabled(True)
            self.zones_shape_fields.addItems(fields)
            
    def zones_shape_fields_changed(self):
        """
            @summary: Detects when the zones shape fields combo change
        """
        if self.zones_shape_fields.currentText() != '':
            self.project.zonesIdFieldName = self.zones_shape_fields.currentText()
            print(self.zones_shape_fields.currentText())
            

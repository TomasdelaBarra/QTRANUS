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

        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.layers_group_name = self.findChild(QtGui.QLineEdit, 'layers_group_name')
        self.tranus_folder = self.findChild(QtGui.QLineEdit, 'tranus_folder')
        self.zone_shape = self.findChild(QtGui.QLineEdit, 'zone_shape')
        self.net_shape = self.findChild(QtGui.QLineEdit, 'net_shape')
        self.centroid_shape = self.findChild(QtGui.QLineEdit, 'centroid_shape')
        self.button_box = self.findChild(QtGui.QDialogButtonBox, 'button_box')
        self.zones_btn = self.findChild(QtGui.QCommandLinkButton, 'zones')
        self.tranus_folder_btn = self.findChild(QtGui.QToolButton, 'tranus_folder_btn')
        self.zones_shape_btn = self.findChild(QtGui.QToolButton, 'zones_shape_btn')
        self.net_shape_btn = self.findChild(QtGui.QToolButton, 'net_shape_btn')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layers_group_name.textEdited.connect(self.save_layers_group_name)
        self.zones_btn.clicked.connect(self.zone_layer_dialog)
        self.tranus_folder_btn.clicked.connect(self.select_tranus_folder)
        self.zones_shape_btn.clicked.connect(self.select_shape(self.select_zones_shape))
        
        # Loads
        self.reload_scenarios()
	
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'index.html')
        webbrowser.open_new_tab(filename)
    	
    def save_layers_group_name(self):
        self.project['project_name'] = self.layers_group_name.text()
        self.check_configure()

    def select_zones_shape(self, file_name):
        if self.project.load_zones_shape(file_name):
            self.zone_shape.setText(file_name)
        else:
            self.zone_shape.setText('')
        self.check_configure()

    def select_tranus_folder(self):
        folder = QtGui.QFileDialog.getExistingDirectory(self, "Select directory")
        if folder:
            self.tranus_folder.setText(folder)
            if not self.project.load_tranus_folder(folder):
                self.tranus_folder.setText('')
            self.reload_scenarios()
        self.check_configure()

    def select_shape(self, callback):
        def select_file():
            file_name = QtGui.QFileDialog.getOpenFileName(parent=self, caption="Select file", filter="*.*, *.shp")
            if file_name:
                callback(file_name)

        return select_file

    def zone_layer_dialog(self):
        if self.project.map_data.get_sorted_fields() is None:
            QMessageBox.warning(None, "Fields", "There are no fields to load, please reload SHP file.")
            print ("There are no fields to load, please reload SHP file.")
        else:
            dialog = ZoneLayerDialog(parent=self)
            dialog.show()
            result = dialog.exec_()

    def show(self):
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
        pass

    def reload_scenarios(self):
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)

    def check_configure(self):
        self.zones_btn.setEnabled(self.project.is_valid())

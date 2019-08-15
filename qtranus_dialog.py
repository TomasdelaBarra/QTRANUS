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

import os, re, webbrowser


from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QMessageBox
from PyQt5.QtCore import *
from qgis.core import QgsProject

from .zonelayer_dialog import ZoneLayerDialog
from .scenarios_model import ScenariosModel
from .networklayer_dialog import NetworkLayerDialog
from .results_dialog import ResultsDialog
from .data_window import DataWindow
from .classes.general.FileManagement import FileManagement
from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.CustomExceptions import InputFileSourceError

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qtranus_dialog_base.ui'))

class QTranusDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, project, parent=None):
        """Constructor."""
        super(QTranusDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        resolution_dict = Helpers.screenResolution(50)
        self.resize(resolution_dict['width'], resolution_dict['height'])

        self.project = project
        self.projectInst = QgsProject.instance()
        self.folder_ws = ''

        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.layers_group_name = self.findChild(QtWidgets.QLineEdit, 'layers_group_name')
        #self.db_folder_btn = self.findChild(QtWidgets.QToolButton, 'db_folder_btn')
        #self.new_db_btn = self.findChild(QtWidgets.QPushButton, name='new_project_btn')
        self.tranus_folder = self.findChild(QtWidgets.QLineEdit, 'tranus_folder')
        self.zone_shape = self.findChild(QtWidgets.QLineEdit, 'zone_shape')
        self.network_links_shape = self.findChild(QtWidgets.QLineEdit, 'network_links_shape')
        self.network_nodes_shape = self.findChild(QtWidgets.QLineEdit, 'network_nodes_shape')
        self.centroid_shape = self.findChild(QtWidgets.QLineEdit, 'centroid_shape')
        self.button_box = self.findChild(QtWidgets.QDialogButtonBox, 'button_box')
        self.data_btn = self.findChild(QtWidgets.QCommandLinkButton, 'data')
        self.results_btn = self.findChild(QtWidgets.QCommandLinkButton, 'results')
        self.run_btn = self.findChild(QtWidgets.QCommandLinkButton, 'run')
        self.tranus_folder_btn = self.findChild(QtWidgets.QToolButton, 'tranus_folder_btn')
        self.zones_shape_btn = self.findChild(QtWidgets.QToolButton, 'zones_shape_btn')
        self.network_links_shape_btn = self.findChild(QtWidgets.QToolButton, 'network_links_shape_btn')
        self.network_nodes_shape_btn = self.findChild(QtWidgets.QToolButton, 'network_nodes_shape_btn')
        self.centroid_shape_btn = self.findChild(QtWidgets.QToolButton, 'centroid_shape_btn')
        self.scenarios = self.findChild(QtWidgets.QTreeView, 'scenarios')
        self.zones_shape_fields = self.findChild(QtWidgets.QComboBox, 'cb_zones_shape_fields')
        self.pg_loading = self.findChild(QtWidgets.QProgressBar, 'pg_loading')
        self.lbl_loading = self.findChild(QtWidgets.QLabel, 'lbl_load')

        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layers_group_name.textEdited.connect(self.save_layers_group_name)
        #self.db_folder_btn.clicked.connect(self.select_db_zip_file(self.select_db))
        #self.new_db_btn.clicked.connect(self.new_db)
        self.data_btn.clicked.connect(self.data_dialog)
        self.results_btn.clicked.connect(self.results_dialog)
        self.run_btn.clicked.connect(self.run_dialog)
        self.tranus_folder_btn.clicked.connect(self.select_tranus_folder)
        self.zones_shape_btn.clicked.connect(self.select_shape(self.select_zones_shape))
        self.centroid_shape_btn.clicked.connect(self.select_centroid_shape_file(self.select_centroid_shape))
        #self.zones_shape_fields.currentIndexChanged[int].connect(self.zones_shape_fields_changed)
        self.zones_shape_fields.currentIndexChanged.connect(self.zones_shape_fields_changed)
        self.network_links_shape_btn.clicked.connect(self.select_network_links_shape_file(self.select_network_links_shape))
        self.network_nodes_shape_btn.clicked.connect(self.select_network_nodes_shape_file(self.select_network_nodes_shape))
        #self.projectInst.cleared(self.clear_project)  
        #self.proj.removeAll.connect(self.clearObjects)
        self.pg_loading.setVisible(False)
        self.lbl_loading.setVisible(False)
        # Loads
        self.reload_scenarios()
        if self.project['zones_id_field_name']:
            self.default_data()

        self.projectInst.removeAll.connect(self.deleteObjects)


    def deleteObjects(self):
        """
            @summary: Opens QTranus users help
        """
        self.folder_ws = ''
        self.tranus_folder.setText('')
        self.zone_shape.setText('')
        self.zones_shape_fields.clear()
        self.centroid_shape.setText('')
        self.network_links_shape.setText('')
        self.centroid_shape.setText('')
        self.network_links_shape.setText('')
        self.network_nodes_shape.setText('')
        self.results_btn.setEnabled(False)


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
    
    def __validate_string(self, input):
        """
            @summary: Validates invalid characters
            @param input: Input string
            @type input: String object
        """
        pattern = re.compile('[\\+\/+\:+\*+\?+\"+\<+\>+\|+\.+]')
        #[\\\/\:\*\?\"\<\>\|\.]
        
        if re.match(pattern, input) is None:
            print('None')
            return True
        else:
            print('No None')
            return False

    def new_db(self):
        if(self.project['tranus_folder'] is None or self.project['tranus_folder'].strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select workspace path.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please select workspace path.")
        else:
#             if not self.__validate_string(self.layers_group_name.text().strip()):
#                 messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "QTranus", "Please write only the name of the file without extensions or file path.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
#                 messagebox.exec_()
#                 print("Please write only the name of the file without extensions or file path.")
#             else:
            newDB = DataBase()
            if(newDB.create_new_data_base(self.project['tranus_folder'], self.layers_group_name.text().strip())):
                self.project.load_db_file(self.project['tranus_folder'] + "\\" + self.layers_group_name.text().strip() + ".zip")
                self.data_btn.setEnabled(True)
            
                print(self.project.db_path)

    def select_zones_shape(self, file_name):
        """
            @summary: Loads selected zone shape file
            @param file_name: Path and name of the shape file
            @type file_name: String
        """
        try:
            result, zoneShapeFieldNames = self.project.load_zones_shape(file_name[0]) 
            if result:
                self.zone_shape.setText(file_name[0])
                self.load_zone_shape_fields(zoneShapeFieldNames)
            else:
                self.zone_shape.setText('')
            self.check_configure()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while reading files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

        

        
    def select_centroid_shape(self, file_name):
        """
            @summary: Loads selected centroid shape file
            @param file_name: Path and name of the shape file
            @type file_name: String
        """
        result = self.project.load_centroid_file(file_name)
        
        if result:
            self.centroid_shape.setText(file_name[0])
        else:
            self.centroid_shape.setText('')
            
    def select_network_links_shape(self, file_name):
        result = self.project.load_network_links_shape_file(file_name)
        if result:
            self.network_links_shape.setText(file_name[0])
            self.results_btn.setEnabled(self.project.is_valid_network())
        else:
            self.network_links_shape.setText('')
        self.check_configure()
            
    def select_network_nodes_shape(self, file_name):
        result = self.project.load_network_nodes_shape_file(file_name)
        if result:
            self.network_nodes_shape.setText(file_name[0])
            self.results_btn.setEnabled(self.project.is_valid_network())
        else:
            self.network_nodes_shape.setText('')
            
    def select_db(self, file_name):
        self.project.load_db_file(file_name)
        self.layers_group_name.setText(file_name)
        self.data_btn.setEnabled(True)

    def select_tranus_folder(self):
        """
            @summary: Sets selected Tranus workspace
        """
        self.folder_ws = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory")
        if self.folder_ws:
            self.tranus_folder.setText(self.folder_ws)
            self.project.load_tranus_folder(self.folder_ws)
            self.reload_scenarios()
        self.check_configure()

    def select_shape(self, callback):
        """
            @summary: Opens selected zone shape file
        """
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select zones shape file", directory=str(self.folder_ws), filter="*.*, *.shp")
            if file_name:
                callback(file_name)

        return select_file
    
    def select_centroid_shape_file(self, callback):
        """
            @summary: Opens selected centroid shape file
        """
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Select centroids shape file', directory=str(self.folder_ws), filter='*.*, *.shp')
            if file_name:
                callback(file_name)
        
        return select_file

    def select_network_links_shape_file(self, callback):
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Select network links shape file', directory=str(self.folder_ws), filter='*.*, *.shp')
            if file_name:
                callback(file_name)
        
        return select_file
    
    def select_network_nodes_shape_file(self, callback):
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Select network nodes shape file', directory=str(self.folder_ws), filter='*.*, *.shp')
            if file_name:
                callback(file_name)
        
        return select_file
    
    def select_db_zip_file(self, callback):
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Select DB zip file', directory='', filter='*.*, *.zip')
            if file_name:
                file_name = file_name.replace('/', '\\')
                print(file_name)
                callback(file_name)
        
        return select_file

    def data_dialog(self):
        """
            @summary: Opens data window
        """
        if(self.layers_group_name.text().strip() !='' and self.tranus_folder.text().strip()!= ''):
            window = DataWindow(self.layers_group_name, self.tranus_folder.text(), parent = self)
            window.show()
            #result = dialog.exec_()
        else:
            if(self.layers_group_name.text().strip() == ''):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select a DB ZIP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select a DB ZIP file.")
            if(self.tranus_folder.text().strip() ==''):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select workspace path.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("Please select workspace path.")

    def results_dialog(self):
        """
            @summary: Opens results window 
        """
        dialog = ResultsDialog(parent = self)
        dialog.show()
        result = dialog.exec_()

    def run_dialog(self):
        """
            @summary: Opens run window 
        """
        #To Do
        #Call your window here
        pass

    def default_data(self):
        print(" show zonesIdFieldName {} ".format(self.project['zones_id_field_name']))
        indexZonesIdFieldName = self.zones_shape_fields.findText(self.project['zones_id_field_name'], Qt.MatchFixedString)
        self.zones_shape_fields.setCurrentIndex(indexZonesIdFieldName)

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
        
        self.project.load_tranus_folder(self.folder_ws)
        self.reload_scenarios()

        result, zoneShapeFieldNames = self.project.load_project_file_shape_files(self.project['zones_shape'], 'zones')

        if self.project['zones_shape']:
            self.zone_shape.setText(self.project['zones_shape'])
        
        if self.project['centroid_shape_file_path']:
            self.centroid_shape.setText(self.project['centroid_shape_file_path'])

        if self.project['network_links_shape_file_path']:
            self.network_links_shape.setText(self.project['network_links_shape_file_path'])
        
        if self.project['network_nodes_shape_file_path']:
            self.network_nodes_shape.setText(self.project['network_nodes_shape_file_path'])

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
        if self.project.is_valid() or self.project.is_valid_network():
            self.results_btn.setEnabled(True)
            #self.data_btn.setEnabled(True)

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
            self.zones_shape_fields.setEnabled(True)
            self.zones_shape_fields.clear()
            self.zones_shape_fields.addItems(fields)
            print("")
            
    def zones_shape_fields_changed(self):
        """
            @summary: Detects when the zones shape fields combo change
        """
        if self.zones_shape_fields.currentText() != '':
            self.project.zonesIdFieldName = self.zones_shape_fields.currentText()
            self.project['zones_id_field_name'] = self.project.zonesIdFieldName
            print("zones_shape_fields_changed {} ".format(self.project['zones_id_field_name']))
            

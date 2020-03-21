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
                               Luis Yanez           - yanezblancoluis@gmail.com
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

import os, re, webbrowser, shutil


from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QMessageBox
from PyQt5.QtCore import *
from qgis.core import QgsProject

from .zonelayer_dialog import ZoneLayerDialog
from .scenarios_model import ScenariosModel
from .networklayer_dialog import NetworkLayerDialog
from .results_dialog import ResultsDialog
from .run_dialog import RunDialog
from .data_window import DataWindow
from .classes.general.FileManagement import FileManagement
from .classes.general.Helpers import Helpers, ExceptionGeometryType
from .classes.data.DataBase import DataBase
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.CustomExceptions import InputFileSourceError
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.data.DataBaseSqlite import DataBaseSqlite

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qtranus_dialog_base.ui'))

class QTranusDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, qtranus, project, parent=None):
        """Constructor."""
        super(QTranusDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        resolution_dict = Helpers.screenResolution(85)
        self.resize(resolution_dict['width'], 0) # for adjust height to content

        self.project = project
        self.projectInst = QgsProject.instance()
        self.folder_ws = ''
        self.dataBaseSqlite = None
        self.project_file = None
        self.qtranus = qtranus
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.layers_group_name = self.findChild(QtWidgets.QLineEdit, 'layers_group_name')
        self.db_btn = self.findChild(QtWidgets.QToolButton, 'db_btn')
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
        self.save_btn = self.findChild(QtWidgets.QPushButton, 'save_btn')
        self.save_as_btn = self.findChild(QtWidgets.QPushButton, 'save_as_btn')
        self.cancel_btn = self.findChild(QtWidgets.QPushButton, 'cancel_btn')
        self.run_btn = self.findChild(QtWidgets.QCommandLinkButton, 'run')
        self.tranus_folder_btn = self.findChild(QtWidgets.QToolButton, 'tranus_folder_btn')
        self.zones_shape_btn = self.findChild(QtWidgets.QToolButton, 'zones_shape_btn')
        self.network_links_shape_btn = self.findChild(QtWidgets.QToolButton, 'network_links_shape_btn')
        self.network_nodes_shape_btn = self.findChild(QtWidgets.QToolButton, 'network_nodes_shape_btn')
        self.centroid_shape_btn = self.findChild(QtWidgets.QToolButton, 'centroid_shape_btn')
        self.scenarios = self.findChild(QtWidgets.QTreeView, 'scenarios')
        self.zones_shape_fields = self.findChild(QtWidgets.QComboBox, 'cb_zones_shape_fields')
        self.zones_shape_name = self.findChild(QtWidgets.QComboBox, 'cb_zones_shape_name')
        self.links_shape_fields = self.findChild(QtWidgets.QComboBox, 'links_shape_fields')
        self.links_shape_length = self.findChild(QtWidgets.QComboBox, 'links_shape_length')
        self.links_shape_name = self.findChild(QtWidgets.QComboBox, 'links_shape_name')
        self.links_shape_type = self.findChild(QtWidgets.QComboBox, 'links_shape_type')
        self.links_shape_direction = self.findChild(QtWidgets.QComboBox, 'links_shape_direction')
        self.links_shape_capacity = self.findChild(QtWidgets.QComboBox, 'links_shape_capacity')
        self.nodes_shape_fields = self.findChild(QtWidgets.QComboBox, 'nodes_shape_fields')
        self.nodes_shape_name = self.findChild(QtWidgets.QComboBox, 'nodes_shape_name')
        self.nodes_shape_x = self.findChild(QtWidgets.QComboBox, 'nodes_shape_x')
        self.nodes_shape_y = self.findChild(QtWidgets.QComboBox, 'nodes_shape_y')
        self.pg_loading = self.findChild(QtWidgets.QProgressBar, 'pg_loading')
        self.lbl_loading = self.findChild(QtWidgets.QLabel, 'lbl_load')

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.layers_group_name.editingFinished.connect(self.project_name)
        #self.layers_group_name.clicked.connect(self.save_layers_group_name)
        self.db_btn.clicked.connect(self.select_db_file(self.select_db))
        #self.new_db_btn.clicked.connect(self.new_db)
        self.data_btn.clicked.connect(self.data_dialog)
        self.results_btn.clicked.connect(self.results_dialog)
        self.run_btn.clicked.connect(self.run_dialog)
        self.save_btn.clicked.connect(self.__save_base_info)
        self.save_as_btn.clicked.connect(self.save_as_db_file(self.select_db))
        self.cancel_btn.clicked.connect(self.close_event)

        self.tranus_folder_btn.clicked.connect(self.select_tranus_folder)
        self.zones_shape_btn.clicked.connect(self.select_zone_shape_file(self.select_zones_shape))
        self.centroid_shape_btn.clicked.connect(self.select_centroid_shape_file(self.select_centroid_shape))
        self.network_links_shape_btn.clicked.connect(self.select_network_links_shape_file(self.select_network_links_shape))
        self.network_nodes_shape_btn.clicked.connect(self.select_network_nodes_shape_file(self.select_network_nodes_shape))

        self.zones_shape_fields.currentIndexChanged.connect(self.zones_shape_fields_changed)
        # self.zones_shape_fields.currentIndexChanged.connect(self.validate_fields_zones_layer)
        self.zones_shape_name.currentIndexChanged.connect(self.check_configure)
        # self.zones_shape_name.currentIndexChanged.connect(self.validate_fields_zones_layer)
        
        self.links_shape_fields.currentIndexChanged.connect(self.check_configure)
        self.links_shape_length.currentIndexChanged.connect(self.check_configure)
        self.links_shape_name.currentIndexChanged.connect(self.check_configure)
        self.links_shape_type.currentIndexChanged.connect(self.check_configure)
        self.links_shape_direction.currentIndexChanged.connect(self.check_configure)
        self.links_shape_capacity.currentIndexChanged.connect(self.check_configure)

        self.nodes_shape_fields.currentIndexChanged.connect(self.check_configure)
        self.nodes_shape_type.currentIndexChanged.connect(self.check_configure)
        self.nodes_shape_name.currentIndexChanged.connect(self.check_configure)
        self.nodes_shape_x.currentIndexChanged.connect(self.check_configure)
        self.nodes_shape_y.currentIndexChanged.connect(self.check_configure)

        self.pg_loading.setVisible(False)
        self.lbl_loading.setVisible(False)

        #self.run_btn.setEnabled(True)
        #self.data_btn.setEnabled(True)
        # Loads
        if self.project['zones_id_field_name']:
            self.default_data()

        self.projectInst.removeAll.connect(self.deleteObjects)

        #self.parent.addScenariosSection()


    def close_event(self):
        self.accept()


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


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'index.html')
        webbrowser.open_new_tab(filename)


    def select_project_db(self, file_name):
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

    	
    def project_name(self):
        """
            @summary: Saves layer group name
        """
        self.project['project_name'] = self.layers_group_name.text()
        self.check_configure()
        self.__load_base_info()


    def __save_base_info(self):
        if self.tranus_folder.text() != '' and self.layers_group_name.text()!= '':
            self.project_file = f"{self.tranus_folder.text()}/{self.layers_group_name.text()}"
        
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        if self.dataBaseSqlite:
            if self.tranus_folder.text() != '' and self.layers_group_name.text() != '' and self.zone_shape.text() != '' and self.network_links_shape.text() != '' and self.network_nodes_shape.text() != '':
                self.dataBaseSqlite.insertBaseParameters(self.zone_shape.text(), self.cb_zones_shape_fields.currentText(), self.network_links_shape.text(), self.links_shape_fields.currentText(), self.network_nodes_shape.text(), self.nodes_shape_fields.currentText())

        self.accept()
        return False

    def __save_as_base_info(self):
        
        return False

    def __load_base_info(self):
        if self.tranus_folder.text() != '' and self.layers_group_name.text()!= '':
            self.project_file = f"{self.tranus_folder.text()}/{self.layers_group_name.text()}"
        
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        if self.dataBaseSqlite:
            self.__load_scenarios()

        result_qry = self.dataBaseSqlite.selectAll(" project_files ", columns=" zone_shape_file, zone_shape_file_id, link_shape_file, link_shape_file_id, node_shape_file, node_shape_file_id ")
        
        if result_qry:
            self.zone_shape.setText(result_qry[0][0])   
            self.network_links_shape.setText(result_qry[0][2])
            self.network_nodes_shape.setText(result_qry[0][4])
            
            result_zones, zoneShapeFieldNames = self.project.load_zones_shape(result_qry[0][0]) 

            if result_zones:
                self.load_zone_shape_fields(zoneShapeFieldNames)

            result_network, networkShapeFields = self.project.load_network_links_shape_file(result_qry[0][2])
            if result_network:
                self.load_network_shape_fields(networkShapeFields)

            result_nodes, nodesShapeFields = self.project.load_network_nodes_shape_file(result_qry[0][4])
            if result_nodes:
                self.load_nodes_shape_fields(nodesShapeFields)


    def __load_scenarios(self):
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.scenarios_model = ScenariosModelSqlite(self.project_file)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenarios.setSelectionModel(modelSelection)


    def __validate_string(self, input):
        """
            @summary: Validates invalid characters
            @param input: Input string
            @type input: String object
        """
        pattern = re.compile('[\\+\/+\:+\*+\?+\"+\<+\>+\|+\.+]')
        
        if re.match(pattern, input) is None:
            return True
        else:
            return False


    def new_db(self):
        if(self.project['tranus_folder'] is None or self.project['tranus_folder'].strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select workspace path.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Please select workspace path.")
        else:
            newDB = DataBase()
            if(newDB.create_new_data_base(self.project['tranus_folder'], self.layers_group_name.text().strip())):
                self.project.load_db_file(self.project['tranus_folder'] + "\\" + self.layers_group_name.text().strip() + ".zip")
                #self.data_btn.setEnabled(True)
            

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
        except ExceptionGeometryType:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Wrong Geometry Type.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while reading files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            self.check_configure()


        
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
        # TODO: Descomentar esto al final de la labor
        try:
            result, networkShapeFields = self.project.load_network_links_shape_file(file_name)
        
            if result:
                self.network_links_shape.setText(file_name[0])
                self.load_network_shape_fields(networkShapeFields)
            else:
                self.network_links_shape.setText('')

        except ExceptionGeometryType:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Wrong Geometry Type.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while reading files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            self.check_configure()

            
    def select_network_nodes_shape(self, file_name):
        try:
            result, nodesShapeFields = self.project.load_network_nodes_shape_file(file_name[0])
        
            if result:
                self.network_nodes_shape.setText(file_name[0])
                self.load_nodes_shape_fields(nodesShapeFields)
            else:
                self.network_nodes_shape.setText('')

        except ExceptionGeometryType:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Wrong Geometry Type.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while reading files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            self.check_configure()


    def select_db(self, file_name):
        self.layers_group_name.setText(file_name)
        if self.tranus_folder.text() and self.layers_group_name.text():
            self.__load_scenarios()
            self.qtranus.addScenariosSection()


    def select_tranus_folder(self):
        """
            @summary: Sets selected Tranus workspace
        """
        self.folder_ws = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory")
        if self.folder_ws:
            self.tranus_folder.setText(self.folder_ws)
            self.project['tranus_folder'] = self.folder_ws
        

    def select_database(self, callback):
        """
            @summary: Opens selected zone shape file
        """
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select zones shape file", directory=str(self.folder_ws), filter="*.*, *.db")
            if file_name:
                callback(file_name)

        return select_file

    def select_zone_shape_file(self, callback):
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
    

    def select_db_file(self, callback):
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Select DB file', directory='', filter='*.*, *.db')
            if file_name:
                file_name = file_name[0].split('/')
                file_name = file_name[len(file_name)-1]
                self.project['project_name'] = file_name
            callback(file_name)
        
        return select_file


    def save_as_db_file(self, callback):

        def select_file():
            old_name = self.layers_group_name.text()
            
            if self.tranus_folder.text() != '':
                defaultFolder = f"{self.tranus_folder.text()}/{self.layers_group_name.text()}"
                self.saveAsfileDialog = QtWidgets.QFileDialog(self)
                self.saveAsfileDialog.setDefaultSuffix("db")
                new_name = self.saveAsfileDialog.getSaveFileName(caption='Select DB file', directory=defaultFolder, filter='*.db')
                if new_name:
                    new_name = new_name[0].split('/')
                    new_name = new_name[len(new_name)-1]
                    shutil.copy(f"{self.project['tranus_folder']}/{old_name}", f"{self.project['tranus_folder']}/{new_name}")
            callback(new_name)
            
        return select_file

    def validate_fields_zones_layer(self):
        zoneIdTxt = self.zones_shape_fields.currentText()
        zoneNameTxt = self.zones_shape_name.currentText()
        layerName = 'Zones'
        if self.zones_shape_fields.count() > 1 and self.zones_shape_name.count() > 1:
            if not self.validate_field(layerName, zoneIdTxt, 'Integer64'):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"Wrong data type field {zoneIdTxt}", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
            if not self.validate_field(layerName, zoneNameTxt, 'String'):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"Wrong data type field {zoneNameTxt}", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()


    def validate_field(self, layerName, fieldName, typeName):
        # try:
        layers = self.projectInst.mapLayersByName(layerName)
        if layers:
            layer = layers[0]
            listFields = layer.fields()
            if listFields.indexFromName(fieldName) != -1:
                field = listFields.field(listFields.indexFromName(fieldName))

                if (field.typeName() == typeName):
                    return True
                else:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"Layer {layerName} field {fieldName} type wrong", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    return False
        """except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"Layer {layerName} not found", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False"""



    def data_dialog(self):
        """
            @summary: Opens data window
        """
        if(self.layers_group_name.text().strip() !='' and self.tranus_folder.text().strip()!= ''):
            project_file = f"{self.tranus_folder.text()}/{self.layers_group_name.text()}"
            window = DataWindow(project_file, parent = self)
            window.show()
            #result = dialog.exec_()
        else:
            if(self.layers_group_name.text().strip() == ''):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select a DB ZIP file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                
            if(self.tranus_folder.text().strip() ==''):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select workspace path.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                

    def results_dialog(self):
        """
            @summary: Opens results window 
        """
        if self.tranus_folder.text().strip() =='':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select workspace path.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        
        dialog = ResultsDialog(self.tranus_folder.text(), parent = self)
        dialog.show()
        result = dialog.exec_()

    def run_dialog(self):
        """
            @summary: Opens run window 
        """
        project_file = f"{self.tranus_folder.text()}/{self.layers_group_name.text()}"
        dialog = RunDialog(project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        pass

    def default_data(self):
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

        if self.project['tranus_folder'] and self.project['project_name']:
            self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
            self.__load_scenarios()


        if  self.project['zones_shape']:
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


    def check_fields_zone_shape(self):
        if self.cb_zones_shape_fields.currentText() != 'Select' and self.cb_zones_shape_fields.currentText() != self.cb_zones_shape_name.currentText():
            return True
        else:
            return False


    def check_fields_link_shape(self):
        if (self.links_shape_fields.currentText() != 'Select' and self.links_shape_length.currentText() != 'Select' and self.links_shape_direction.currentText() != 'Select') and (self.links_shape_fields.currentText() != '' and self.links_shape_length.currentText() != '' and self.links_shape_direction.currentText() != ''):
            return True
        else:
            return False


    def check_fields_node_shape(self):
        if (self.nodes_shape_fields.currentText() != 'Select' and self.nodes_shape_type.currentText() != 'Select' and self.nodes_shape_x.currentText() != 'Select' and self.nodes_shape_y.currentText() != 'Select') and (self.nodes_shape_fields.currentText() != '' and self.nodes_shape_type.currentText() != '' and self.nodes_shape_x.currentText() != '' and self.nodes_shape_y.currentText() != ''):
            return True
        else:
            return False



    def check_configure(self):
        """
            @summary: Validates configuration
        """
        if self.layers_group_name.text() and self.tranus_folder.text() and self.zone_shape.text() and self.network_nodes_shape.text() and self.network_links_shape.text() and self.check_fields_zone_shape() and self.check_fields_link_shape() and self.check_fields_node_shape():
            self.results_btn.setEnabled(True)
            self.run_btn.setEnabled(True)
            self.data_btn.setEnabled(True)
        else:
            self.results_btn.setEnabled(False)
            self.run_btn.setEnabled(False)
            self.data_btn.setEnabled(False)
        #self.validate_fields_zones_layer()

    def load_zone_shape_fields(self, fields):
        """
            @summary: Loads zone shape fields combo
            @param fields: Zone shape fields
            @type fields: List object
        """
        if fields is None:
            QMessageBox.warning(None, "Zone Shape Fields", "There are no fields to load.")
        else:
            fields.insert(0,'Select')
            self.zones_shape_fields.setEnabled(True)
            self.zones_shape_fields.clear()
            self.zones_shape_fields.addItems(fields)
            zoneIdTxt = self.zones_shape_fields.findText('id', Qt.MatchContains)
            self.zones_shape_fields.setCurrentIndex(zoneIdTxt)

            self.zones_shape_name.setEnabled(True)
            self.zones_shape_name.clear()
            self.zones_shape_name.addItems(fields)
            zoneNameTxt = self.zones_shape_name.findText('name', Qt.MatchContains)
            self.zones_shape_name.setCurrentIndex(zoneNameTxt)



    def load_network_shape_fields(self, fields):
        """
            @summary: Loads zone shape fields combo
            @param fields: Zone shape fields
            @type fields: List object
        """
        
        if fields is None:
            QMessageBox.warning(None, "Zone Shape Fields", "There are no fields to load.")
            print ("There are no fields to load.")
        else:
            fields.insert(0,'Select')
            self.links_shape_fields.setEnabled(True)
            self.links_shape_fields.clear()
            self.links_shape_fields.addItems(fields)
            linkIdTxt = self.links_shape_fields.findText('id', Qt.MatchContains) if self.links_shape_fields.findText('id', Qt.MatchContains) != -1 else 0
            self.links_shape_fields.setCurrentIndex(linkIdTxt)

            self.links_shape_length.setEnabled(True)
            self.links_shape_length.clear()
            self.links_shape_length.addItems(fields)
            linkLengthTxt = self.links_shape_length.findText('length', Qt.MatchContains) if self.links_shape_length.findText('id', Qt.MatchContains) != -1 else 0
            self.links_shape_length.setCurrentIndex(linkLengthTxt)

            self.links_shape_name.setEnabled(True)
            self.links_shape_name.clear()
            self.links_shape_name.addItems(fields)
            linkNameTxt = self.links_shape_name.findText('name', Qt.MatchContains) if self.links_shape_name.findText('name', Qt.MatchContains) != -1 else 0
            self.links_shape_name.setCurrentIndex(linkNameTxt)

            self.links_shape_type.setEnabled(True)
            self.links_shape_type.clear()
            self.links_shape_type.addItems(fields)
            linkTypeTxt = self.links_shape_type.findText('type', Qt.MatchContains) if self.links_shape_type.findText('type', Qt.MatchContains) != -1 else 0
            self.links_shape_type.setCurrentIndex(linkTypeTxt)

            self.links_shape_direction.setEnabled(True)
            self.links_shape_direction.clear()
            self.links_shape_direction.addItems(fields)
            directionTxt = self.links_shape_direction.findText('direction', Qt.MatchContains) if self.links_shape_direction.findText('direction', Qt.MatchContains) != -1 else 0
            self.links_shape_direction.setCurrentIndex(directionTxt)

            self.links_shape_capacity.setEnabled(True)
            self.links_shape_capacity.clear()
            self.links_shape_capacity.addItems(fields)
            capacityTxt = self.links_shape_capacity.findText('capacity', Qt.MatchContains) if self.links_shape_capacity.findText('capacity', Qt.MatchContains) != -1 else 0
            self.links_shape_capacity.setCurrentIndex(capacityTxt)


    def load_nodes_shape_fields(self, fields):
        """
            @summary: Loads zone shape fields combo
            @param fields: Zone shape fields
            @type fields: List object
        """
        
        if fields is None:
            QMessageBox.warning(None, "Zone Shape Fields", "There are no fields to load.")
            print ("There are no fields to load.")
        else:
            fields.insert(0,'Select')
            self.nodes_shape_fields.setEnabled(True)
            self.nodes_shape_fields.clear()
            self.nodes_shape_fields.addItems(fields)
            xIdTxt = self.nodes_shape_fields.findText('id', Qt.MatchContains) if self.nodes_shape_fields.findText('id', Qt.MatchContains) != -1 else 0
            self.nodes_shape_fields.setCurrentIndex(xIdTxt)
            
            self.nodes_shape_type.setEnabled(True)
            self.nodes_shape_type.clear()
            self.nodes_shape_type.addItems(fields)
            nodeTypeTxt = self.nodes_shape_type.findText('type', Qt.MatchContains) if self.nodes_shape_type.findText('type', Qt.MatchContains) != -1 else 0
            self.nodes_shape_type.setCurrentIndex(nodeTypeTxt)
            
            self.nodes_shape_name.setEnabled(True)
            self.nodes_shape_name.clear()
            self.nodes_shape_name.addItems(fields)
            xNameTxt = self.nodes_shape_name.findText('name', Qt.MatchContains) if self.nodes_shape_name.findText('name', Qt.MatchContains) != -1 else 0
            self.nodes_shape_name.setCurrentIndex(xNameTxt)
            
            self.nodes_shape_x.setEnabled(True)
            self.nodes_shape_x.clear()
            self.nodes_shape_x.addItems(fields)
            xNodeTxt = self.nodes_shape_x.findText('x', Qt.MatchContains) if self.nodes_shape_x.findText('x', Qt.MatchContains) != -1 else 0
            self.nodes_shape_x.setCurrentIndex(xNodeTxt)
            
            self.nodes_shape_y.setEnabled(True)
            self.nodes_shape_y.clear()
            self.nodes_shape_y.addItems(fields)
            yNodeTxt = self.nodes_shape_y.findText('y', Qt.MatchContains) if self.nodes_shape_y.findText('y', Qt.MatchContains) != -1 else 0 
            self.nodes_shape_y.setCurrentIndex(yNodeTxt)

            
    def zones_shape_fields_changed(self):
        """
            @summary: Detects when the zones shape fields combo change
        """
        if self.zones_shape_fields.currentText() != '':
            self.project.zonesIdFieldName = self.zones_shape_fields.currentText()
            self.project['zones_id_field_name'] = self.project.zonesIdFieldName
            

# -*- coding: utf-8 -*-
import os, re, webbrowser
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QAbstractItemView, QStandardItemModel, QStandardItem

from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_dialog import ScenariosDialog
from .classes.data.DataBase import DataBase
from .classes.data.Scenario import Scenario
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.data.DBFiles import DBFiles

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'data.ui'))

class DataDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(DataDialog, self).__init__(parent)
        self.plugin_dir = os.path.dirname(__file__)
        self.setupUi(self)
        self.project = parent.project
        self.dataBase = DataBase()
        self.scenarios =  None
        self.scenariosMatrix = None
        self.scenariosMatrixBackUp = None
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.btn_scenarios = self.findChild(QtWidgets.QPushButton, 'btn_scenarios')
        self.scenario_tree.setRootIsDecorated(False)
        
        self.buttonBox.button(QtWidgets.QDialogButtonBox.SaveAll).setText('Save as...')
        
        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.btn_scenarios.clicked.connect(self.open_scenarios_window)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_db)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.SaveAll).clicked.connect(self.save_db_as)
        
        #Loads
        self.__extract_db_files()

        
    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)
        
    def open_scenarios_window(self):
        """
            @summary: Opens data window
        """
        dialog = ScenariosDialog(parent = self)
        dialog.show()
        result = dialog.exec_()
    
    def __extract_db_files(self):
        if(self.project.db_path is None or self.project.db_path.strip() == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "DB File was not found.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("DB File was not found.")
        else:
            if(self.dataBase.extract_scenarios_file_from_zip(self.project.db_path, self.project['tranus_folder'])):
                self.dataBase.create_backup_file(self.project['tranus_folder'], DBFiles.Scenarios)
                self.__load_scenarios()               
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Scenarios file could not be extracted.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("DB files could not be extracted.")
        
    def __load_scenarios(self):
        if self.scenariosMatrix is None:
            self.scenariosMatrix = self.dataBase.get_scenarios_array(self.project['tranus_folder'])

        self.scenariosMatrixBackUp = self.scenariosMatrix
        self.scenarios = Scenarios()
        self.scenarios.load_data(self.scenariosMatrix)
        
        scenariosModel = ScenariosModel(self)
        self.scenario_tree.setModel(scenariosModel)
        self.scenario_tree.setExpanded(scenariosModel.indexFromItem(scenariosModel.root_item), True)
        
    def load_scenarios(self):
        self.__load_scenarios()
        
    def save_db(self):
        if(self.dataBase.save_db(self.project['tranus_folder'], self.project.db_path, self.project.db_path, DBFiles.Scenarios, self.scenariosMatrix)):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "DB has been saved.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("DB has been saved.")
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "There was a problem trying to save DB, please verify and try again.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("There was a problem trying to save DB, please verify and try again.")
            
        #https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
        
    def save_db_as(self):
        file_name = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Choose a file name to save the DB.', directory=self.project['tranus_folder'], filter='*.*, *.zip')
        print(file_name)
        if file_name.strip() != '':
            if(self.dataBase.save_db(self.project['tranus_folder'], self.project.db_path, file_name, DBFiles.Scenarios, self.scenariosMatrix)):
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "DB has been saved.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("DB has been saved.")
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "There was a problem trying to save DB, please verify and try again.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print("There was a problem trying to save DB, please verify and try again.")
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "There was not selected any file name to save, please verify and try again.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("There was not selected any file name to save, please verify and try again.")
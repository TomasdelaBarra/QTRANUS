# -*- coding: utf-8 -*-
import os, subprocess, re, webbrowser, csv, numpy as np
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from qgis.gui import *
from zipfile import ZipFile as zf


from .classes.general.Helpers import Helpers
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.data.ScenariosFiles import ScenariosFiles
from .classes.data.BatchFiles import BatchFiles
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .scenarios_model_sqlite import ScenariosModelSqlite

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'run.ui'))

class RunDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, project_file, scenarioSelectedIndex=None, parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(RunDialog, self).__init__(parent)
        self.setupUi(self)
        self.project_file = project_file

        self.tranus_folder = self.uriSegmentation(project_file)
        self.project = parent.project
        self.copyAdministratorSelected = None
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        self.file = None
        
        self.plugin_dir = os.path.dirname(__file__)
        self.scenarioSelectedIndex = scenarioSelectedIndex
        self.scenarioCode = '00A'
        self.idScenario = None
        #resolution_dict = Helpers.screenResolution(60)
        self.resize(1180, 500)
        self.header = ['Scenario', 'Description']
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.clicked.connect(self.select_scenario)
        self.programs_list = []
        self.programsListSelected = []

        self.btn_run = self.findChild(QtWidgets.QPushButton, 'btn_run')
        self.btn_close = self.findChild(QtWidgets.QPushButton, 'btn_close')
        self.btn_remove = self.findChild(QtWidgets.QPushButton, 'btn_remove')
        self.btn_add_to_batch = self.findChild(QtWidgets.QPushButton, 'btn_add_to_batch')
        self.btn_save_batch = self.findChild(QtWidgets.QPushButton, 'btn_save_batch')
        self.btn_load_batch = self.findChild(QtWidgets.QPushButton, 'btn_load_batch')
        self.rd_allprograms = self.findChild(QtWidgets.QRadioButton, 'rd_allprograms')
        self.rd_selected_programs = self.findChild(QtWidgets.QRadioButton, 'rd_selected_programs')
        self.chck_path_search = self.findChild(QtWidgets.QCheckBox,'chck_path_search')
        self.chck_initial_assigment = self.findChild(QtWidgets.QCheckBox,'chck_initial_assigment')
        self.chck_location = self.findChild(QtWidgets.QCheckBox,'chck_location')
        self.chck_fixed_transportable = self.findChild(QtWidgets.QCheckBox,'chck_fixed_transportable')
        self.chck_assigment = self.findChild(QtWidgets.QCheckBox,'chck_assigment')
        self.tree_batch = self.findChild(QtWidgets.QTreeView,'tree_batch')
        self.tree_batch.setRootIsDecorated(False)
        self.te_ouput = self.findChild(QtWidgets.QTextEdit,'te_ouput')
        self.tab_run = self.findChild(QtWidgets.QTabWidget,'tab_run')
        self.layout_status_bar = self.findChild(QtWidgets.QVBoxLayout,'layout_status_bar')
        self.fixed_transportable = None
        self.statusBar = QStatusBar(self)
        self.layout_status_bar.addWidget(self.statusBar)

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.scenario_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenario_tree.clicked.connect(self.select_scenario)

        self.btn_close.clicked.connect(self.close_event)
        self.btn_run.clicked.connect(self.run_event)
        self.rd_allprograms.clicked.connect(self.validate_buttons)
        self.rd_selected_programs.clicked.connect(self.validate_buttons)
        self.btn_add_to_batch.clicked.connect(self.add_to_batch)

        self.btn_run.setIcon(QIcon(self.plugin_dir+"/icons/run.png"))
        self.btn_remove.setIcon(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"))
        self.btn_add_to_batch.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        self.btn_save_batch.setIcon(QIcon(self.plugin_dir+"/icons/save.svg"))
        self.btn_load_batch.setIcon(QIcon(self.plugin_dir+"/icons/load-folder.png"))
        
        # IMPORTANT: Unzip Programs folder
        self.extractProgramsZip()

        # Run process
        self.process = QtCore.QProcess(self)
        self.env = QtCore.QProcessEnvironment.systemEnvironment()
        self.programs_dir = self.plugin_dir.replace("\\","/")+"/programs"

        # Set Path Variable for QProcess Instance
        if self.programs_dir not in self.env.value("Path"):
            self.env.insert("Path", self.programs_dir)

        # QProcess emits `readyRead` when there is data to be read
        self.process.setProcessEnvironment(self.env)
        self.process.readyRead.connect(self.dataReady)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it
        # when it finishes
        self.chck_fixed_transportable.clicked.connect(self.validate_fixed_trans)
        self.chck_location.clicked.connect(self.validate_locations)
        self.btn_load_batch.clicked.connect(self.select_file(self.load_batch_file))
        self.btn_save_batch.clicked.connect(self.save_file(self.save_batch_file))
        self.btn_remove.clicked.connect(self.remove_program)
        self.process.started.connect(lambda: self.btn_run.setEnabled(False))
        self.process.finished.connect(self.finish_process)

        self.rd_allprograms.setChecked(True)
        self.btn_save_batch.setEnabled(False)
        #Loads
        self.__get_scenarios_data()

    def extractProgramsZip(self):
        #print(self.plugin_dir)
        #ruta = self.plugin_dir.replace("\\","/")+'/programs.zip'
        #print(ruta)
        file = zf(self.plugin_dir.replace("\\","/")+'/programs.zip')
        file.extractall(self.plugin_dir.replace("\\","/"))


    def uriSegmentation(self, project_file):
        project_file_arr = project_file.split("\\")
        return "/".join(project_file_arr[:len(project_file_arr)-1])


    def validate_fixed_trans(self):
        if self.chck_fixed_transportable.isChecked():
            self.chck_location.setChecked(True)

    def validate_locations(self):
        if not self.chck_location.isChecked():
            self.chck_fixed_transportable.setChecked(False)

    def __validate_links(self):
        sql = f"""select linkid
                from link 
                where id_linktype is null and id_scenario = {self.idScenario}"""
        result = self.dataBaseSqlite.executeSql(sql)

        if result:
            links = ''
            for linkid in result:
                links += f"{linkid[0]} \n"
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"Please select type to the following links \n{links}", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        else:
            return True



    def remove_program(self):
        """
        @summary: Remove program from QTableView
        """
        indexes = self.tree_batch.selectedIndexes()
        if indexes:
            scenarioCode = indexes[0].model().itemFromIndex(indexes[0]).text()
            program = indexes[1].model().itemFromIndex(indexes[1]).text()
            self.programs_list.remove((program))
            self.populate_tableview()



    def select_file(self, callback):
        """
        @summary: Opens selected zone shape file
        """
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select batch file", directory=str(self.tranus_folder), filter="*.*, *.tusbat")
            
            if file_name:
                callback(file_name)

        return select_file

    def save_file(self, callback):
        """
        @summary: Opens selected zone shape file
        """
        def select_file():
            #file_name = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption="Save Batch file", directory=str(self.tranus_folder), filter="*.*, *.tusbat")
            file_name = QtWidgets.QFileDialog.getSaveFileName(self, "Save Batch File","", '*.tusbat')
            print(file_name)
            if file_name:
                callback(file_name)

        return select_file
        

    def load_batch_file(self, file_name):
        """
            @summary: Loads selected zone shape file
            @param file_name: Path and name of the shape file
            @type file_name: String
        """
        try:
            programsDict = {'PATHS':'Path Search', 'TRANS /I':'Initial Assigment', 'LOC':'Location', 'TRANS':'Assigment'}
            self.programListBatch = []
            if file_name[0]:
                for value in [line.split(",") for line in open(file_name[0])]:
                    program = programsDict[value[0].replace('"','')]
                    scenarioCode = value[1].replace('"','').replace('\n','')
                    self.programListBatch.append([scenarioCode, program])
                    
            self.populateTableViewFromBatchFile()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while lading batch files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()


    def save_batch_file(self, file_name):
        """
            @summary: Loads selected zone shape file
            @param file_name: Path and name of the shape file
            @type file_name: String
        """
        try:
            programsDict = {'Path Search':'PATHS', 'Initial Assigment':'TRANS /I', 'Location':'LOC', 'Assigment':'TRANS'}
            self.programListBatch = []

            if file_name[0]:
                fh = open(file_name[0], 'w', encoding="utf8")
                for value in self.programsListSelected:
                    fh.write(f'"{programsDict[value[1]]}","{value[0]}"\n')
                fh.close()
        except:
            fh.close()
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while lading batch files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()


    def dataReady(self):
        try:
            output_data = str(self.process.readAll(), 'utf-8')
            cursor = self.te_ouput.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(output_data)
            self.te_ouput.ensureCursorVisible()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while generating files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()


    def finish_process(self):
        self.btn_run.setEnabled(True)
        #if self.file:
        #    os.remove(f"{self.file}")


    def add_to_batch(self):
        self.programs_list = []
    
        if self.rd_allprograms.isChecked():
            self.programs_list = ['Path Search', 'Initial Assigment', 'Location', 'Assigment'] if self.is_base_scenario(self.scenarioCode) else ['Path Search', 'Location', 'Assigment']
    
        if self.chck_path_search.isChecked():
            self.programs_list.append('Path Search')

        if self.chck_initial_assigment.isChecked():
            self.programs_list.append('Initial Assigment')

        if self.chck_location.isChecked():
            self.programs_list.append('Location')

        if self.chck_assigment.isChecked():
            self.programs_list.append('Assigment')

        if self.chck_fixed_transportable.isChecked():
            self.fixed_transportable = True
        else:
            self.fixed_transportable = False
    
        self.populate_tableview()
        if len(self.programs_list) > 0:
            self.btn_save_batch.setEnabled(True)

        return True

    def populate_tableview(self):

        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenario','Program'])
        self.programsListSelected.clear()
        for index, value in enumerate(self.programs_list):
            model.insertRow(index)
            itemScenario = QtGui.QStandardItem(self.scenarioCode)
            itemScenario.setIcon(QIcon(self.plugin_dir+"/icons/modelistica_logo.png"))
            itemProgram = QtGui.QStandardItem(value)
            itemslist = [itemScenario, itemProgram]
            self.programsListSelected.append((self.scenarioCode, value))
            model.insertRow(index, itemslist)

        self.tree_batch.setModel(model)
        self.tree_batch.setColumnWidth(0, 60)
            
        return True

    def populateTableViewFromBatchFile(self):
        
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Scenario','Program'])
        self.programsListSelected.clear()
        for index, value in enumerate(self.programListBatch):
            model.insertRow(index)
            itemScenario = QtGui.QStandardItem(value[0])
            itemScenario.setIcon(QIcon(self.plugin_dir+"/icons/modelistica_logo.png"))
            itemProgram = QtGui.QStandardItem(value[1])
            itemslist = [itemScenario, itemProgram]
            self.programsListSelected.append((value[0], value[1]))
            model.insertRow(index, itemslist)

        self.tree_batch.setModel(model)
        self.tree_batch.setColumnWidth(0, 60)
            
        return True

    def removeItems():
        indexes = self.administrators_tree.selectedIndexes()
        administratorSelected = indexes[0].model().itemFromIndex(indexes[0]).text()

    def validate_buttons(self):
        
        if self.rd_allprograms.isChecked():
            self.chck_path_search.setEnabled(False)
            self.chck_initial_assigment.setEnabled(False)
            self.chck_location.setEnabled(False)
            self.chck_fixed_transportable.setEnabled(False)
            self.chck_assigment.setEnabled(False)
            self.chck_path_search.setChecked(False)
            self.chck_initial_assigment.setChecked(False)
            self.chck_location.setChecked(False)
            self.chck_fixed_transportable.setChecked(False)
            self.chck_assigment.setChecked(False)
        else:
            self.chck_path_search.setEnabled(True)
            self.chck_location.setEnabled(True)
            self.chck_assigment.setEnabled(True)

            if self.scenarioData[0][3]:
                self.chck_fixed_transportable.setEnabled(False)
                self.chck_initial_assigment.setEnabled(False)
            else:
                self.chck_initial_assigment.setEnabled(True)
                self.chck_fixed_transportable.setEnabled(True)


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        self.scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(self.scenarioCode))
        self.idScenario = self.scenarioData[0][0]
        self.validate_buttons()
        


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'run.html')
        webbrowser.open_new_tab(filename)


    def __get_scenarios_data(self):

        self.scenarios_model = ScenariosModelSqlite(self.project_file)
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.Select)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        self.scenario_tree.setSelectionModel(modelSelection)
        
        self.select_scenario(self.scenario_tree.selectedIndexes()[0])
               
    

    def __find_scenario_data(self, scenarioCode):
        """
            @summary: Find and Set data of the scenario Selected
        """
        scenarioData = self.dataBaseSqlite.selectAll('scenario', " where code = '{}'".format(scenarioCode))
        self.idScenario = scenarioData[0][0]
        
        
    def save_event(self, event):
        if self.btn_nodes.isChecked():
            self.__load_csv_nodes(self.import_file_obj.filePath())
        elif self.btn_links.isChecked():
            self.__load_csv_links(self.import_file_obj.filePath())
        elif self.btn_routes.isChecked():
            self.__load_csv_routes(self.import_file_obj.filePath())
        elif self.btn_opers.isChecked():
            self.__load_csv_opers(self.import_file_obj.filePath())
        elif self.btn_turns.isChecked():
            self.__load_csv_turns(self.import_file_obj.filePath())
        

    def close_event(self, event):
        self.close()

    def run_event(self, event):
        if self.__validate_links():
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.generate_single_scenario(self.idScenario)
            
            self.tab_run.setCurrentIndex(1)
            self.batch_file = BatchFiles(self.project_file, pluginDir=self.plugin_dir, statusBar=self.statusBar, programsListSelected=self.programsListSelected, id_scenario=self.idScenario, fixed_transportable=self.fixed_transportable)
            self.file = self.batch_file.generate_bath_file()

            # If rum Trans Create Assigment PENDIENTE 
            self.batch_file.validate_generate_assigment()

            if self.file:
                os.chdir(self.tranus_folder)
                self.process.start("cmd.exe", {f"/C {self.file}"})
                #os.remove(f"{self.file}")
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Run", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
    
    def is_base_scenario(self, scenario_code):
        
        result = self.dataBaseSqlite.selectAll(" scenario ", where=f" where code = '{scenario_code}' and cod_previous = '' ")

        if len(result) > 0:
            return True
        else:
            return False


# -*- coding: utf-8 -*-
from string import *
import os, csv, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .classes.libraries import xlrd

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'import_csv.ui'))

class ImportCsvData(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent=None, idScenario=None, _type=None, _idCategory=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ImportCsvData, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.tranus_folder = tranus_folder
        self.idScenario = idScenario
        self._type = _type
        self._idCategory = _idCategory
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.filename_path = None

        self.header = self.findChild(QtWidgets.QCheckBox, 'header')
        self.filename = self.findChild(QtWidgets.QLineEdit, 'filename')
        self.ln_sheetname = self.findChild(QtWidgets.QLineEdit, 'ln_sheetname')
        self.filename_btn = self.findChild(QtWidgets.QToolButton, 'filename_btn')
        self.filename_btn.clicked.connect(self.select_file)

        self.progress_bar = self.findChild(QtWidgets.QProgressBar, 'progress_bar')
        self.progress_bar.setVisible(False)
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save)
        #self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close)


    def select_file(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Excel File", directory=str(self.tranus_folder), filter="*.*, *.csv")
        if file_name:
            self.filename_path = file_name[0]
            self.filename.setText(file_name[0])
        else:
            self.filename.setText('')


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def save(self):
        if self.filename_path is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Please Select File.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            if self._type == 'transfers':
                self.import_transfers()
            elif self._type == 'exogenous_trips':
                self.import_exogenous_trips()

            self.close()
            
    def import_transfers(self):
        loc = self.filename_path
        wb = xlrd.open_workbook(loc) 
        sheet_names = wb.sheet_names()
        if self.ln_sheetname.text() in sheet_names:
            sheet = wb.sheet_by_name(self.ln_sheetname.text()) 
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            header = 1 if self.header.isChecked() else 0
            for i in range(header,sheet.nrows): 
                id_origin = str(sheet.row_values(i, 0)[0]).split(' ')[0]
                id_destination = str(sheet.row_values(i, 0)[1]).split(' ')[0]
                tariff = sheet.row_values(i, 0)[2]
                try:
                    id_origin = int(float(id_origin))
                    id_destination = int(float(id_destination))
                    tariff = float(tariff)
                except:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Row (%s) Invalid." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    break

                result_ori = self.dataBaseSqlite.selectAll(' operator ', where = " where id = %s" % id_origin)
                result_dest = self.dataBaseSqlite.selectAll(' operator ', where = " where id = %s" % id_destination)
                if len(result_ori)==0 or len(result_dest)==0:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Invalid Operator in row (%s)." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    break
                else:
                    resultado = self.dataBaseSqlite.addTransferOperator(scenarios, id_origin, id_destination, tariff)
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Invalid Sheet name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

    def import_exogenous_trips(self):
        try:
            path = self.filename_path
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % self.idScenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            iter = 0
            if len(scenarios) == 0:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return True
                self.close() 
            with open(path) as csv_file_read:
                rows_file_read = csv.reader(csv_file_read, delimiter=',')
                tot_rows = len(list(rows_file_read))



            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                id_category = self._idCategory
                self.progress_bar.show()
           
                data_trips = []
                try:
                    for index, row in enumerate(csv_reader):
                        id_from = row[0].strip()
                        id_to = row[1].strip()
                        trips = row[2].strip()
                        iter += 1
                        percent = iter * 100 / tot_rows if tot_rows > 0 else 1
                        self.progress_bar.setValue(percent)
                        data_trips.append((id_from, id_to, id_category, trips))
                    result = self.dataBaseSqlite.bulkLoadExogenousTrips(scenarios, data_trips)
                    self.progress_bar.setValue(percent)
                except:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                finally:
                    self.close()
                    return True  
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Import Files Error.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return True
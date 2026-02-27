# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser
import subprocess
import platform

from PyQt5 import QtCore
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
    os.path.dirname(__file__), 'results_reports.ui'))

class ResultsReportsDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent=None, idScenario=None, _type=None, _idCategory=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(ResultsReportsDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.tranus_folder = tranus_folder
        self.idScenario = idScenario
        self._type = _type
        self._idCategory = _idCategory
        self.plugin_dir = os.path.dirname(__file__)
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.filename_path = None

        self.header = self.findChild(QtWidgets.QCheckBox, 'header')
        self.filename = self.findChild(QtWidgets.QLineEdit, 'filename')
        self.ln_sheetname = self.findChild(QtWidgets.QLineEdit, 'ln_sheetname')
        self.filename_btn = self.findChild(QtWidgets.QToolButton, 'filename_btn')
        self.filename_btn.clicked.connect(self.select_file)

        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save)
        #self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close)

        # Run process
        self.process = QtCore.QProcess(self)
        self.env = QtCore.QProcessEnvironment.systemEnvironment()
        self.programs_dir = self.plugin_dir.replace("\\","/")+"/programs"

        # Set Path Variable for QProcess Instance
        if self.programs_dir not in self.env.value("Path"):
            self.env.insert("Path", self.programs_dir)

        # QProcess emits `readyRead` when there is data to be read
        self.process.setProcessEnvironment(self.env)


    def select_file(self):
        print(str(self.tranus_folder))
        # 1) Si ya tenemos un directorio válido, solo lo mostramos
        if self.filename_path and os.path.isdir(self.filename_path):
            self.filename.setText(self.filename_path)
            return

        # 2) Si no existe, permitimos que el usuario seleccione o cree uno nuevo
        options = QtWidgets.QFileDialog.ShowDirsOnly
        folder = self.clear_name_file(str(self.tranus_folder))
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select or create a directory",
            directory=str(folder),
            options=options
        )

        if directory:
            # Si el usuario eligió un directorio, lo usamos
            if not os.path.isdir(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception:
                    directory = ''

        if directory and os.path.isdir(directory):
            self.filename_path = directory
            self.filename.setText(directory)
        else:
            self.filename_path = None
            self.filename.setText('')


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def save(self):
        # self.run_imptra_indicators()
        print(self.tranus_folder)
        print(self.filename_path)
        self.ejecutar_comando_sistema()
        if self.filename_path is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Reports Data", "Please Select File.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            self.close()


    def run_imptra_indicators(self):
        if not self.idScenario:
            return
        scenario = "25A"
        os.chdir(self.tranus_folder)

        # Ejecuta: imptra <escenario> -J -o transport_indicators_<escenario>.csv
        result = self.process.start("imptra", [scenario, "-P", "-o", f"{self.filename_path}/route_profile_{scenario}.csv"])


    def clear_name_file(self, ruta):
        """
        Busca la última barra invertida y sustituye 
        lo que sigue por un espacio.
        """
        # 1. Encontrar el índice de la última barra invertida '\'
        indice = ruta.rfind('\\')
        
        # 2. Si se encuentra la barra invertida
        if indice != -1:
            # Tomamos la parte anterior a la barra (incluyéndola)
            # y le sumamos un espacio en blanco
            nueva_ruta = ruta[:indice + 1] + " "
            return nueva_ruta
        else:
            # Si no hay '\', devolvemos la ruta original o un mensaje
            return ruta


    def ejecutar_comando_sistema(self):
        # Detectamos el sistema operativo para elegir el comando correcto
        # 'ls' para Linux/Mac, 'dir' para Windows
        os.chdir(self.clear_name_file(self.tranus_folder))
        print(self.filename_path)
        scenario = '25A'
        file_name = f"route_profile_{scenario}.csv"
        print(file_name)
        comando = f"C:\\Users\\USUARIO\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\QTRANUS\\programs\\imptra.exe 25A -S -o {file_name}"

        try:
            # Ejecutamos el comando
            # shell=False es más seguro para evitar inyecciones de código
            resultado = subprocess.run(
                comando, 
                capture_output=True, 
                text=True, 
                check=True
            )

            # Imprimimos lo que el sistema respondió
            print("--- Comando ejecutado con éxito ---")
            print(resultado.stdout)

        except subprocess.CalledProcessError as e:
            # Si el comando falla, capturamos el error
            print(f"Error al ejecutar el comando: {e}")

    
# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser, json, traceback

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *
from PyQt5.Qt import QMessageBox
from qgis.core import Qgis, QgsProject, QgsFeatureRequest, QgsFeature, QgsGeometry
from qgis.utils import iface


from .classes.general.Helpers import Helpers, ExceptionGeometryType
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'prepare_network_dialog.ui'))

class PrepareNetworkDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent = None, project=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(PrepareNetworkDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = project 

        self.links_shape_codscenario = self.findChild(QtWidgets.QComboBox, 'links_shape_codscenario')
        self.links_shape_origin = self.findChild(QtWidgets.QComboBox, 'links_shape_origin')
        self.links_shape_destination = self.findChild(QtWidgets.QComboBox, 'links_shape_destination')
        self.links_shape_fields = self.findChild(QtWidgets.QComboBox, 'links_shape_fields')
        self.links_shape_length = self.findChild(QtWidgets.QComboBox, 'links_shape_length')
        self.links_shape_name = self.findChild(QtWidgets.QComboBox, 'links_shape_name')
        self.links_shape_type = self.findChild(QtWidgets.QComboBox, 'links_shape_type')
        self.links_shape_direction = self.findChild(QtWidgets.QComboBox, 'links_shape_direction')
        self.links_shape_capacity = self.findChild(QtWidgets.QComboBox, 'links_shape_capacity')

        self.network_links_shape = self.findChild(QtWidgets.QLineEdit, 'network_links_shape')
        self.network_links_shape_btn = self.findChild(QtWidgets.QToolButton, 'network_links_shape_btn')
        self.network_process_links_shape_btn = self.findChild(QtWidgets.QPushButton, 'processButton')

        self.network_process_links_shape_btn.clicked.connect(self.prepare_network_layer)
        self.network_links_shape_btn.clicked.connect(self.select_network_links_shape_file(self.select_network_links_shape))
        

    def save_new_network(self):
        id_scenario = self.idScenario
        scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
        scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
        if self.idScenario is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Administrator", "Plese Select Scenario.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.id is None or self.id.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Administrator", "Please write id.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.dataBaseSqlite.validateId('administrator', self.id.text()) is False and self.codeAdministrator is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "New Administrator", "Please write an id valid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.name is None or self.name.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Administrator", "Please write the name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
            
        if self.description is None or self.description.text().strip() == '':
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Administrator", "Please write the description.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if self.codeAdministrator is None:

            newAdministrator = self.dataBaseSqlite.addAdministrator(scenarios, self.id.text(), self.name.text(), self.description.text())
            if not newAdministrator:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Administrator", "Please select other scenario code.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_() 
                return False
        else:
            newAdministrator = self.dataBaseSqlite.updateAdministrator(scenarios, self.id.text(), self.name.text(), self.description.text())

        if newAdministrator is not None:
            self.parent().load_scenarios()
            self.accept()
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Add new Administrator", "Please Verify information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        return True


    def select_network_links_shape_file(self, callback):
        def select_file():
            file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Select network links shape file', directory=str(''), filter='*.*, *.shp')
            if file_name:
                callback(file_name)
        
        return select_file


    def select_network_links_shape(self, file_name):
        try:
            file_name = file_name if isinstance(file_name,str) else file_name[0]
            result, networkShapeFields = self.project.load_prepared_network_links_shape_file(file_name)
        
            if result:
                self.network_links_shape.setText(file_name)
                self.load_network_shape_fields(networkShapeFields)
            else:
                self.network_links_shape.setText('')

        except ExceptionGeometryType:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Wrong Geometry Type.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except Exception as e:
            print('Error while reading files: %s' % str(e))
            print(traceback.format_exc())
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while reading files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            print('finally')
            #self.check_configure()

    
    def prepare_network_layer(self):
        """
            @summary: Prepare network layer to be used in QTranus
            @param fields: Network shape fields
            @type fields: List object
        """
        layer = QgsProject.instance().mapLayer(self.project['network_prepared_links_shape_id'])
        
        # Validar que haya una capa seleccionada y que sea vectorial
        if not layer or layer.type() != layer.VectorLayer:
            print("Por favor, selecciona una capa vectorial activa.")
            return

        # Validar que el campo "DIR" exista en la capa
        if layer.fields().indexFromName("DIR") == -1:
            print("Error: La capa no tiene un campo llamado 'DIR'.")
            return

        # Crear la solicitud (Query) para filtrar los elementos
        # Usamos tanto '0' (texto) como 0 (número) por si el campo es de tipo String o Integer
        expresion = "\"DIR\" = '0' OR \"DIR\" = 0"
        request = QgsFeatureRequest().setFilterExpression(expresion)
        
        # Obtener los elementos que cumplen la condición
        elementos_a_duplicar = list(layer.getFeatures(request))
        
        if not elementos_a_duplicar:
            print("No se encontraron elementos con valor '0' en el campo 'DIR'.")
            return

        # Poner la capa en modo edición
        layer.startEditing()
        nuevos_elementos = []
        
        for feature in elementos_a_duplicar:
            # Crear un nuevo elemento vacío con la estructura de la capa
            """
            nuevo_feature = QgsFeature(layer.fields())
            
            # 1. Copiar la Geometría
            nueva_geometria = QgsGeometry(feature.geometry())
            nueva_geometria.translate(0.0001, 0.0001)  # desplaza +5 en X y 0 en Y

            #nueva_geometria = feature.geometry().offsetCurve(0.2, 8, Qgis.JoinStyle.Round, 2)
            #nuevo_feature.setGeometry(nueva_geometria)
            nuevo_feature.setGeometry(nueva_geometria)
            # 2. Copiar los Atributos
            nuevo_feature.setAttributes(feature.attributes())
            # Añadir a la lista
            nuevos_elementos.append(nuevo_feature)
            """
            nuevo_feature = QgsFeature(layer.fields())
            geom = feature.geometry()
            
            # Generar la curva paralela (offset)
            # Parámetros: distancia, segmentos (curvas), estilo de unión, límite de inglete
            distancia = 0.00006
            geom_paralela = geom.offsetCurve(distancia, 8, Qgis.JoinStyle.Round, 2.0)
            
            # Validar que la generación de la paralela no haya fallado
            if geom_paralela and not geom_paralela.isEmpty():
                nuevo_feature.setGeometry(geom_paralela)
            else:
                # Si falla (por auto-intersecciones extremas), usamos la original
                nuevo_feature.setGeometry(geom)
                
            nuevo_feature.setAttributes(feature.attributes())
            nuevos_elementos.append(nuevo_feature)
            
        # Añadir los nuevos elementos a la capa
        exito = layer.addFeatures(nuevos_elementos)
        
        if exito:
            # Refrescar el mapa
            iface.mapCanvas().refresh()
            print(f"Éxito: Se han duplicado {len(nuevos_elementos)} elemento(s) con DIR = 0.")
        else:
            print("Hubo un error al añadir los elementos a la capa.")
        
        # layer.commitChanges()
        # Opcional: layer.commitChanges() para guardar automáticamente


    def load_network_shape_fields(self, fields):
        """
            @summary: Loads zone shape fields combo
            @param fields: Network shape fields
            @type fields: List object
        """
        
        if fields is None:
            QMessageBox.warning(None, "Network Shape Fields", "There are no fields to load.")
            print ("There are no fields to load.")
        else:
            fields.insert(0,'Select')
            self.links_shape_codscenario.setEnabled(True)
            self.links_shape_codscenario.clear()
            self.links_shape_codscenario.addItems(fields)
            linkScenarioTxt = self.links_shape_codscenario.findText('scenario', Qt.MatchContains) if self.links_shape_codscenario.findText('scenario', Qt.MatchContains) != -1 else 0
            self.links_shape_codscenario.setCurrentIndex(linkScenarioTxt)

            self.links_shape_origin.setEnabled(True)
            self.links_shape_origin.clear()
            self.links_shape_origin.addItems(fields)
            linkOriginTxt = self.links_shape_origin.findText('origin', Qt.MatchContains) if self.links_shape_origin.findText('origin', Qt.MatchContains) != -1 else 0
            self.links_shape_origin.setCurrentIndex(linkOriginTxt)

            self.links_shape_destination.setEnabled(True)
            self.links_shape_destination.clear()
            self.links_shape_destination.addItems(fields)
            linkDestinationTxt = self.links_shape_destination.findText('destination', Qt.MatchContains) if self.links_shape_destination.findText('destination', Qt.MatchContains) != -1 else 0
            self.links_shape_destination.setCurrentIndex(linkDestinationTxt)

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

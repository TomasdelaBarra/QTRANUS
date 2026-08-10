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
from qgis.core import Qgis, QgsProject, QgsFeatureRequest, QgsFeature, QgsGeometry, QgsField
from qgis.utils import iface


from .classes.general.Helpers import Helpers, ExceptionGeometryType
from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'

from .prepare_network_summary_dialog import PrepareNetworkSummaryDialog

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
        self.parent = parent
        self.setupUi(self)
        self.project = project 
        self.prepare_network_summary_dialog = None
        
        self.links_shape_origin = self.findChild(QtWidgets.QComboBox, 'links_shape_origin')
        self.links_shape_destination = self.findChild(QtWidgets.QComboBox, 'links_shape_destination')
        self.links_shape_id = self.findChild(QtWidgets.QComboBox, 'links_shape_id')
        self.links_shape_length = self.findChild(QtWidgets.QComboBox, 'links_shape_length')
        self.links_shape_name = self.findChild(QtWidgets.QComboBox, 'links_shape_name')
        self.links_shape_type = self.findChild(QtWidgets.QComboBox, 'links_shape_type')
        self.links_shape_direction = self.findChild(QtWidgets.QComboBox, 'links_shape_direction')
        self.links_shape_capacity = self.findChild(QtWidgets.QComboBox, 'links_shape_capacity')
        self.links_shape_network_filename = self.findChild(QtWidgets.QLineEdit, 'links_shape_network_filename')
        self.links_shape_load_links = self.findChild(QtWidgets.QPushButton, 'links_shape_load_links')
        self.links_offset = self.findChild(QtWidgets.QDoubleSpinBox, 'links_offset')
        self.links_offset.setValue(0.00006)
        self.links_initial_node_id = self.findChild(QtWidgets.QSpinBox, 'links_initial_node_id')
        self.links_initial_node_id.setValue(1)

        self.links_shape_origin.currentIndexChanged.connect(self.validate_form_fields)
        self.links_shape_destination.currentIndexChanged.connect(self.validate_form_fields)
        self.links_shape_id.currentIndexChanged.connect(self.validate_form_fields)
        self.links_shape_length.currentIndexChanged.connect(self.validate_form_fields)
        self.links_shape_name.currentIndexChanged.connect(self.validate_form_fields)
        self.links_shape_type.currentIndexChanged.connect(self.validate_form_fields)
        self.links_shape_direction.currentIndexChanged.connect(self.validate_form_fields)
        self.links_offset.valueChanged.connect(self.validate_form_fields)

        self.network_links_shape = self.findChild(QtWidgets.QLineEdit, 'network_links_shape')
        self.network_links_shape_btn = self.findChild(QtWidgets.QToolButton, 'network_links_shape_btn')
        self.network_process_links_shape_btn = self.findChild(QtWidgets.QPushButton, 'processButton')
        self.progress_bar = self.findChild(QtWidgets.QProgressBar, 'progressBar')

        self.links_shape_load_links.clicked.connect(self.select_network_links_shape)
        self.network_process_links_shape_btn.clicked.connect(self.confirm_network_layer)
        self.network_links_shape_btn.clicked.connect(self.select_network_links_shape_file(self.process_file_names))
        
        self.network_process_links_shape_btn.setEnabled(False)
        self.links_shape_load_links.setEnabled(False)
        self.progress_bar.setVisible(False)



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


    def select_network_links_shape(self):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            base_name = self.network_links_shape.text()
            copy_name = self.links_shape_network_filename.text()
            directory, file = os.path.split(base_name)
            copy_name = os.path.join(directory, copy_name)
            self.project.copy_network_shape_file(base_name, copy_name)

            result, networkShapeFields = self.project.load_prepared_network_links_shape_file(copy_name)
            if result:
                self.load_network_shape_fields(networkShapeFields)
                iface.messageBar().pushSuccess("Success", "Layer was created successfully.")
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "There is a issue.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
        except ExceptionGeometryType:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Wrong Geometry Type.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except Exception as e:
            print('Error while reading files: %s' % str(e))
            print(traceback.format_exc())
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Error while reading files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            QApplication.restoreOverrideCursor()
            print('finally')
            #self.check_configure()


    def process_file_names(self, file_name):
        """
            @summary: Process the selected file name to extract the directory, file name, and extension
            @param file_name: The full path of the selected file
            @type file_name: str
        """
        file_name = file_name if isinstance(file_name,str) else file_name[0]
        directory, file = os.path.split(file_name)
        name_without_ext, extension = os.path.splitext(file)

        self.network_links_shape.setText(file_name)
        self.links_shape_network_filename.setText(f"{name_without_ext}_copy{extension}")
        self.validate_base_network_shape_file()
        
        
    def validate_base_network_shape_file(self):
        """
            @summary: Validate the base network shape file before processing
            @return: True if the base network shape file is valid, False otherwise
            @rtype: bool
        """
        base_name = self.network_links_shape.text()
        if not base_name:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Please select a base network shape file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        if not os.path.isfile(base_name):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "The selected base network shape file does not exist.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        
        self.links_shape_load_links.setEnabled(True) 

        return True


    def validate_if_network_nodes_exist(self):
        """
            @summary: Validate whether Prepared_Nodes and Prepared_Network exist in the QTRANUS group.
            @return: True if both layers exist inside the QTRANUS group, False otherwise.
            @rtype: bool
        """
        layers_group = QgsProject.instance().layerTreeRoot().findGroup('QTRANUS')
        if layers_group is None:
            return False

        layer_names = {
            layer_node.layer().name()
            for layer_node in layers_group.findLayers()
            if layer_node.layer() is not None
        }
        # return 'Prepared_Nodes' in layer_names and 'Prepared_Network' in layer_names
        return 'Prepared_Nodes' in layer_names

    def prepare_network_layer(self):
        """
            @summary: Prepare network layer to be used in QTranus
            @param fields: Network shape fields
            @type fields: List object
        """
        try:
            # Wating time
            self.progress_bar.show()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setFormat('Preparing network layer...')
            self.progress_bar.setValue(0)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            QApplication.processEvents()
            # Wating time

            initial_node_id = self.links_initial_node_id.value()
            direction_field = self.links_shape_direction.currentText()
            link_id_source_field = self.links_shape_id.currentText()
            layer_id = self.project['network_prepared_links_shape_id']
            layer = QgsProject.instance().mapLayer(layer_id)       

            base_name = self.network_links_shape.text()
            copy_name = self.links_shape_network_filename.text()
            directory, file = os.path.split(base_name)
            copy_name = os.path.join(directory, "Nodes_generated.shp") 
                
            origin_field = self.links_shape_origin.currentText() if self.links_shape_origin.currentText() != 'Select' else None
            destination_field = self.links_shape_destination.currentText() if self.links_shape_destination.currentText() != 'Select' else None
            length_field = self.links_shape_length.currentText() if self.links_shape_length.currentText() != 'Select' else None
            capacity_field = self.links_shape_capacity.currentText() if self.links_shape_capacity.currentText() != 'Select' else None
            type_field = self.links_shape_type.currentText() if self.links_shape_type.currentText() != 'Select' else None
            name_field = self.links_shape_name.currentText() if self.links_shape_name.currentText() != 'Select' else None
            id_field = self.links_shape_id.currentText() if self.links_shape_id.currentText() != 'Select' else None
            direction_field = self.links_shape_direction.currentText() if self.links_shape_direction.currentText() != 'Select' else None

            if not layer or layer.type() != layer.VectorLayer:
                print("Please select an active vector layer.")
                self.progress_bar.setVisible(False)
                return

            canonical_direction_field = 'Direction'

            """
            if layer.fields().indexFromName(direction_field) == -1:
                print(f"Error: The layer does not have a field named '{direction_field}'.")
                self.progress_bar.setVisible(False)
                return
            """
            if not self.validate_if_network_nodes_exist():
                self.progress_bar.setFormat('Generating nodes from Network layer...')
                QApplication.processEvents()
                generated_nodes_result = self.project.generate_nodes_from_lines(
                    layer,
                    path=copy_name,
                    start_node_id=initial_node_id,
                    progress_bar_obj=self.progress_bar
                )

                if not generated_nodes_result:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", "Nodes could not be generated from the selected network layer.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    self.progress_bar.setVisible(False)
                    QApplication.restoreOverrideCursor()
                    return

                nodes_layer_id, added_nodes = generated_nodes_result
                self.progress_bar.setFormat(f"{added_nodes} nodes generated.")
                QApplication.processEvents()

                layer.startEditing()

                # Update the network layer attributes to match the expected schema.
                self.update_network_layer_attributes(layer, id_field, direction_field, origin_field, destination_field, length_field, capacity_field, type_field, name_field)

                if not self.layer_has_field(layer, canonical_direction_field):
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"The layer does not have the attribute '{canonical_direction_field}'.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    layer.rollBack()
                    self.progress_bar.setVisible(False)
                    return

                expression = f'"{canonical_direction_field}" IS NULL OR to_int("{canonical_direction_field}") IN (0, 2)'
                request = QgsFeatureRequest().setFilterExpression(expression)

                features_to_duplicate = list(layer.getFeatures(request))

                if not features_to_duplicate:
                    print(f"No features were found with values 0, 2 or NULL in '{canonical_direction_field}'.")
                    self.progress_bar.setVisible(False)
                    return

                # if not self.validate_if_network_nodes_exist():
                new_features = []

                # Wating time
                total_features = len(features_to_duplicate)
                progress_step = max(1, total_features // 100)
                # Wating time

                self.progress_bar.setFormat('Editing network links...')

                for index, feature in enumerate(features_to_duplicate, start=1):
                    geometry = feature.geometry()
                    new_feature = QgsFeature(layer.fields())

                    offset_distance = self.links_offset.value() 
                    offset_geometry = geometry.offsetCurve((offset_distance * -1), 8, Qgis.JoinStyle.Round, 2.0)

                    if offset_geometry and not offset_geometry.isEmpty():
                        duplicated_geometry = offset_geometry
                    else:
                        duplicated_geometry = geometry

                    if duplicated_geometry.isMultipart():
                        reversed_geometry = QgsGeometry.fromMultiPolylineXY([
                            list(reversed(line)) for line in duplicated_geometry.asMultiPolyline()
                        ])
                    else:
                        reversed_geometry = QgsGeometry.fromPolylineXY(
                            list(reversed(duplicated_geometry.asPolyline()))
                        )

                    if reversed_geometry and not reversed_geometry.isEmpty():
                        new_feature.setGeometry(reversed_geometry)
                    else:
                        new_feature.setGeometry(duplicated_geometry)

                    new_feature.setAttributes(feature.attributes())

                    link_id_value = new_feature.attribute('LinkID')
                    if not (isinstance(link_id_value, QVariant) and link_id_value.isNull()) and link_id_value is not None:
                        link_id_text = str(link_id_value)
                        if '-' in link_id_text:
                            origin_node_id, destination_node_id = link_id_text.split('-', 1)
                            new_feature.setAttribute('LinkID', f"{destination_node_id}-{origin_node_id}")

                    new_features.append(new_feature)

                    # Wating time
                    if index % progress_step == 0 or index == total_features:
                        progress_value = min(100, int((index * 100) / total_features))
                        self.progress_bar.setValue(progress_value)
                        QApplication.processEvents()
                    # Wating time

                success = layer.addFeatures(new_features)
                
                if success:
                    layer.commitChanges()
                    iface.mapCanvas().refresh()
                    self.progress_bar.setVisible(False)
                    added_links_count = len(new_features)
                    removed_links_count = 0  # Assuming no links are removed in this process
                    final_links_count = len(list(layer.getFeatures()))
                    self.accept()

                    if self.prepare_network_summary_dialog is None:
                        self.prepare_network_summary_dialog = PrepareNetworkSummaryDialog(
                            parent=self.parent,
                            added_links=added_links_count,
                            removed_links=removed_links_count,
                            final_links=final_links_count,
                            added_nodes=added_nodes
                        )
                    
                    # Show summary Dialog
                    self.prepare_network_summary_dialog.show()
                    self.prepare_network_summary_dialog.raise_()
                    self.prepare_network_summary_dialog.activateWindow()

                else:
                    layer.rollBack()
                    self.progress_bar.setVisible(False)
        
            else:
                if not self.layer_has_field(layer, canonical_direction_field):
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", f"The layer does not have the attribute '{canonical_direction_field}'.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    self.progress_bar.setVisible(False)
                    return

                expression = f'"{canonical_direction_field}" IS NULL OR to_int("{canonical_direction_field}") IN (0, 2)'
                request = QgsFeatureRequest().setFilterExpression(expression)

                features_to_duplicate = list(layer.getFeatures(request))

                layer = self.get_layer_by_name('Prepared_Network')
                self.update_offset_parallel(features_to_duplicate, layer, self.links_offset.value())
        
        except Exception as e:
            print(f"An error occurred: {e}")
            print(traceback.format_exc())
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "QTranus", str(e), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            self.progress_bar.setVisible(False)
            QApplication.restoreOverrideCursor()

    
    def update_network_layer_attributes(self, layer, id_field, direction_field, origin_field, destination_field, length_field, capacity_field, type_field, name_field):
        """
            @summary: Update the attributes of the network layer to match the expected schema.
            @param layer: The network layer to update
            @type layer: QgsVectorLayer
            @param id_field: The name of the link id field in the layer
            @type id_field: str
            @param direction_field: The name of the direction field in the layer
            @type direction_field: str  
            @param origin_field: The name of the origin field in the layer
            @type origin_field: str
            @param destination_field: The name of the destination field in the layer
            @type destination_field: str
            @param length_field: The name of the length field in the layer
            @type length_field: str
            @param capacity_field: The name of the capacity field in the layer
            @type capacity_field: str
            @param type_field: The name of the type field in the layer
            @type type_field: str
            @param name_field: The name of the name field in the layer
            @type name_field: str
        """

        # Scenario Code
        scenario_code_index = layer.fields().indexFromName('SceCode')
        if scenario_code_index == -1:
            if not layer.dataProvider().addAttributes([QgsField('SceCode', QVariant.String)]):
                print("Error: The field 'ScenarioCode' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()
            scenario_code_index = layer.fields().indexFromName('SceCode')

        # Link ID
        """
        id_index = layer.fields().indexOf(id_field) if id_field else -1
        if id_index != -1:
            if layer.dataProvider().renameAttributes({id_index: 'LinkID'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('LinkID', QVariant.String)]):
                print("Error: The field 'LinkID' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()
        """
        
        # Direction
        direction_index = layer.fields().indexOf(direction_field) if direction_field else -1
        if direction_index != -1:
            if layer.dataProvider().renameAttributes({direction_index: 'Direction'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Direction', QVariant.Int)]):
                print("Error: The field 'Direction' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()


        # Origin 
        origin_index = layer.fields().indexOf(origin_field) if origin_field else -1
        if origin_index != -1:
            if layer.dataProvider().renameAttributes({origin_index: 'Origin'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Origin', QVariant.Int)]):
                print("Error: The field 'Origin' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()

        # Destination
        destination_index = layer.fields().indexOf(destination_field) if destination_field else -1
        if destination_index != -1:
            if layer.dataProvider().renameAttributes({destination_index: 'Dest'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Dest', QVariant.Int)]):
                print("Error: The field 'Destination' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()

        # Length
        length_index = layer.fields().indexOf(length_field) if length_field else -1
        if length_index != -1:
            if layer.dataProvider().renameAttributes({length_index: 'Length'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Length', QVariant.Double)]):
                print("Error: The field 'Length' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()

        # Capacity
        capacity_index = layer.fields().indexOf(capacity_field) if capacity_field else -1
        if capacity_index != -1:
            if layer.dataProvider().renameAttributes({capacity_index: 'Capacity'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Capacity', QVariant.Double)]):
                print("Error: The field 'Capacity' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()

        # Type
        type_index = layer.fields().indexOf(type_field) if type_field else -1
        if type_index != -1:
            if layer.dataProvider().renameAttributes({type_index: 'Type'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Type', QVariant.String)]):
                print("Error: The field 'Type' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()

        # Name
        name_index = layer.fields().indexOf(name_field) if name_field else -1
        if name_index != -1:
            if layer.dataProvider().renameAttributes({name_index: 'Name'}):
                layer.updateFields()
        else:
            if not layer.dataProvider().addAttributes([QgsField('Name', QVariant.String)]):
                print("Error: The field 'Name' could not be added to the layer.")
                layer.rollBack()
                return
            layer.updateFields()



    def get_layer_by_name(self, layer_name):
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if not layers:
            print(f"Layer '{layer_name}' not found.")
            return None

        return layers[0]


    def layer_has_field(self, layer, field_name):
        if layer is None or not field_name:
            return False

        return layer.fields().indexFromName(field_name) != -1


    def update_offset_parallel(self, features, layer, new_offset):
        """
        Update the offset for a list of line features in the provided layer.

        :param features: List of QgsFeature objects to update.
        :param layer: QgsVectorLayer containing the features to modify.
        :param new_offset: New numeric separation value, positive or negative.
        :return: True if at least one feature was updated, False otherwise.
        """
        if not features or layer is None:
            return False

        has_changes = False

        if not layer.isEditable():
            layer.startEditing()

        for feature in features:
            geometry = feature.geometry()
            if geometry is None or geometry.isEmpty():
                continue

            updated_geometry = geometry.offsetCurve(
                (new_offset * -1),
                8,
                Qgis.JoinStyle.Round,
                2.0
            )

            if updated_geometry is None or updated_geometry.isEmpty():
                continue

            if layer.changeGeometry(feature.id(), updated_geometry):
                has_changes = True

        if has_changes:
            layer.commitChanges()
            return True

        layer.rollBack()
        return False


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

            self.links_shape_id.setEnabled(True)
            self.links_shape_id.clear()
            self.links_shape_id.addItems(fields)
            linkIdTxt = self.links_shape_id.findText('id', Qt.MatchContains) if self.links_shape_id.findText('id', Qt.MatchContains) != -1 else 0
            self.links_shape_id.setCurrentIndex(linkIdTxt)

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

            self.validate_form_fields()


    def validate_form_fields(self):
        """
            @summary: Validate required combo values in the form.
            @return: True when all required fields are different from Select.
            @rtype: bool
        """
        required_fields = [
            self.links_shape_direction
        ]

        has_valid_fields = all(field.currentText().strip() != 'Select' for field in required_fields)
        has_valid_offset = self.links_offset.value() != 0.0
        is_valid = has_valid_fields and has_valid_offset
        self.network_process_links_shape_btn.setEnabled(is_valid)
        return is_valid


    def confirm_network_layer(self, message):
        """
            @summary: Show a warning message box with the provided message.
            @param message: The message to display in the warning box.
            @type message: str
        """
        results = QMessageBox.question(
            self,
            "Alert",
            "Caution: This operation will modify the features of the active layer and permanently update the source shapefile (.shp). This action cannot be undone. Do you wish to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Este es el botón seleccionado por defecto
        )

        # Evaluar la respuesta del usuario
        if results == QMessageBox.StandardButton.Yes:
            self.prepare_network_layer()
                    
    # -*- coding: utf-8 -*-
import os, re, webbrowser
from string import *
import threading

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QAbstractItemView, QStandardItemModel, QStandardItem, QMainWindow, QToolBar, QHBoxLayout
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtCore import *

from qgis.core import QgsVectorLayer

from .classes.general.Helpers import *
from .classes.libraries.tabulate import tabulate
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.data.DBFiles import DBFiles
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.DataBase import DataBase
from .classes.data.Scenario import Scenario
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .classes.data.ScenariosFiles import ScenariosFiles
from .scenarios_dialog import ScenariosDialog
from .sectors_dialog import SectorsDialog
from .intersectors_dialog import IntersectorsDialog
from .zonaldata_dialog import ZonalDataDialog
from .categories_dialog import CategoriesDialog
from .configuration_dialog import ConfigurationDialog
from .modes_dialog import ModesDialog
from .operators_dialog import OperatorsDialog
from .transfers_dialog import TransfersDialog
from .zones_dialog import ZonesDialog
from .routes_dialog import RoutesDialog
from .link_type_dialog import LinkTypeDialog
from .links_dialog import LinksDialog
from .nodes_dialog import NodesDialog
from .databaseerror_dialog import DatabaseErrorsDialog
from .exogenous_trips_dialog import ExogeousTripsDialog
from .administrators_dialog import AdministratorsDialog
from .scenarios_select_dialog import ScenariosSelectDialog
from .add_excel_data_dialog import AddExcelDataDialog
from .imports_network_dialog import ImportsNetworkDialog
from .scenarios_model_sqlite import ScenariosModelSqlite


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'data.ui'))

class DataWindow(QMainWindow, FORM_CLASS):
    
    def __init__(self, project_file,  parent = None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(DataWindow, self).__init__(parent)
        self.plugin_dir = os.path.dirname(__file__)
        self.setupUi(self)
        resolution_dict = Helpers.screenResolution(60)
        self.resize(resolution_dict['width'], 0)
        self.project = parent.project
        self.zone_shape = parent.zone_shape
        self.zones_shape_id = parent.zones_shape_fields
        self.zones_shape_name = parent.zones_shape_name
        self.network_links_shape = parent.network_links_shape
        self.links_shape_codscenario = parent.links_shape_codscenario
        self.links_shape_origin = parent.links_shape_origin
        self.links_shape_destination = parent.links_shape_destination
        self.links_shape_fields = parent.links_shape_fields
        self.links_shape_name = parent.links_shape_name
        self.links_shape_type = parent.links_shape_type
        self.links_shape_length = parent.links_shape_length
        self.links_shape_direction = parent.links_shape_direction
        self.links_shape_capacity = parent.links_shape_capacity
        self.network_nodes_shape = parent.network_nodes_shape
        self.nodes_shape_fields = parent.nodes_shape_fields
        self.nodes_shape_name = parent.nodes_shape_name
        self.nodes_shape_type = parent.nodes_shape_type
        self.nodes_shape_x = parent.nodes_shape_x
        self.nodes_shape_y = parent.nodes_shape_y
        self.project_file = project_file
        self.dataBase = DataBase()
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        self.scenarios =  None
        self.scenariosMatrix = None
        self.scenariosMatrixBackUp = None
        self.scenarioSelectedIndex = None
        self.scenarioCode = None
        self.linktypesList = []

        self.mainWindow = QMainWindow()
        self.myToolBar = QToolBar()
        self.mainWindow.addToolBar(self.myToolBar)

        self.layout = QHBoxLayout();
        self.layout.addWidget(self.mainWindow)
        self.setLayout(self.layout)
        
        # Linking objects with controls
        self.help = self.findChild(QtWidgets.QPushButton, 'btn_help')
        #self.progressBar = self.findChild(QtWidgets.QProgressBar, 'progressBar')
        self.statusBar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
        self.scenario_tree = self.findChild(QtWidgets.QTreeView, 'scenarios_tree')
        self.scenario_tree.setRootIsDecorated(False)
        self.btn_options = self.findChild(QtWidgets.QPushButton, 'btn_options')
        self.btn_scenarios = self.findChild(QtWidgets.QPushButton, 'btn_scenarios')
        self.btn_zones = self.findChild(QtWidgets.QPushButton, 'btn_zones')
        self.btn_sectors = self.findChild(QtWidgets.QPushButton, 'btn_sectors')
        self.btn_intersectors = self.findChild(QtWidgets.QPushButton, 'btn_intersectors')
        self.btn_categories = self.findChild(QtWidgets.QPushButton, 'btn_categories')
        self.btn_links = self.findChild(QtWidgets.QPushButton, 'btn_links')
        self.btn_nodes = self.findChild(QtWidgets.QPushButton, 'btn_nodes')
        self.btn_modes = self.findChild(QtWidgets.QPushButton, 'btn_modes')
        self.btn_operators = self.findChild(QtWidgets.QPushButton, 'btn_operators')
        self.btn_transfers = self.findChild(QtWidgets.QPushButton, 'btn_transfers')
        self.btn_routes = self.findChild(QtWidgets.QPushButton, 'btn_routes')
        self.btn_administrators = self.findChild(QtWidgets.QPushButton, 'btn_administrators')
        self.btn_zonal_data = self.findChild(QtWidgets.QPushButton, 'btn_zonal_data')
        self.btn_exogenous_trips = self.findChild(QtWidgets.QPushButton, 'btn_exogenous_trips')
        
        """
        self.actn_scenarios = self.findChild(QtWidgets.QAction, 'actionScenarios')
        self.actn_options = self.findChild(QtWidgets.QAction, 'actionOptions')
        self.actn_zones = self.findChild(QtWidgets.QAction, 'actionZones')
        """
        self.actn_imp_network = self.findChild(QtWidgets.QAction, 'actionImportNetwork')
        self.actn_overwrite_zones = self.findChild(QtWidgets.QAction, 'actionOverwriteZones')
        self.actn_overwrite_nodes = self.findChild(QtWidgets.QAction, 'actionOverwriteNodes')
        self.actn_overwrite_links = self.findChild(QtWidgets.QAction, 'actionOverwriteLinks')
        self.actn_generate_input_files = self.findChild(QtWidgets.QAction, 'actionGenerate_Input_Files')
        self.actn_generate_single_scenario = self.findChild(QtWidgets.QAction, 'actionGenerate_Single_Scenario')
        self.actn_ctl_scenario_definitions = self.findChild(QtWidgets.QAction, 'actionCTL_Scenario_Definitions')
        self.actn_z1e_zone_definitions = self.findChild(QtWidgets.QAction, 'actionZ1E_Zone_Definitions')
        self.actn_p0e_transport_parameters = self.findChild(QtWidgets.QAction, 'actionP0E_Transport_Parameters')
        self.actn_p1e_network = self.findChild(QtWidgets.QAction, 'actionP1E_Network')
        self.actn_t1e_assignment_parameters = self.findChild(QtWidgets.QAction, 'actionT1E_Assignment_Parameters')
        self.actn_f1e_flow_defenitions = self.findChild(QtWidgets.QAction, 'actionF1E_Flow_Defenitions')
        self.actn_l0e_base_year_activity = self.findChild(QtWidgets.QAction, 'actionL0E_Base_Year_Activity')
        self.actn_l1e_economic_sector_definitions = self.findChild(QtWidgets.QAction, 'actionL1E_Economic_Sector_Definitions')
        self.actn_l2e_activity_increments = self.findChild(QtWidgets.QAction, 'actionL2E_Activity_Increments')
        self.actn_l3e_activity_increments_and_decrements = self.findChild(QtWidgets.QAction, 'actionL3E_Activity_Increments_and_Decrements')
        
        #self.buttonBox.button(QtWidgets.QDialogButtonBox.SaveAll).setText('Save as...')

        # Control Actions
        self.help.clicked.connect(self.open_help)
        self.btn_options.clicked.connect(self.open_configuration_window)
        self.btn_scenarios.clicked.connect(self.open_scenarios_window)
        self.btn_zones.clicked.connect(self.open_zones_window)
        self.btn_sectors.clicked.connect(self.open_sectors_window)
        self.btn_intersectors.clicked.connect(self.open_intersectors_window)
        self.btn_zonal_data.clicked.connect(self.open_zonaldata_window)
        self.btn_categories.clicked.connect(self.open_categories_window)
        self.btn_modes.clicked.connect(self.open_modes_window)
        self.btn_operators.clicked.connect(self.open_operators_window)
        self.btn_transfers.clicked.connect(self.open_transfers_window)
        self.btn_routes.clicked.connect(self.open_routes_window)
        self.btn_administrators.clicked.connect(self.open_administrators_window)
        self.btn_link_types.clicked.connect(self.open_linktype_window)
        self.btn_links.clicked.connect(self.open_links_window)
        self.btn_nodes.clicked.connect(self.open_nodes_window)
        self.btn_exogenous_trips.clicked.connect(self.open_exgogenoustrips_window)
        """
        self.actn_scenarios.triggered.connect(self.open_scenarios_window)
        self.actn_options.triggered.connect(self.open_configuration_window)
        self.actn_zones.triggered.connect(self.open_zones_window)"""

        self.actn_imp_network.triggered.connect(self.open_import_network)
        self.actn_overwrite_zones.triggered.connect(self.open_overwrite_zones)
        self.actn_overwrite_nodes.triggered.connect(self.open_overwrite_nodes)
        self.actn_overwrite_links.triggered.connect(self.open_overwrite_links)
        self.actn_generate_input_files.triggered.connect(self.generate_input_files)
        self.actn_generate_single_scenario.triggered.connect(self.generate_single_scenario)
        self.actn_ctl_scenario_definitions.triggered.connect(self.generate_ctl_file)
        self.actn_z1e_zone_definitions.triggered.connect(self.generate_z1e_file)
        self.actn_l0e_base_year_activity.triggered.connect(self.generate_l0e_file)
        self.actn_l1e_economic_sector_definitions.triggered.connect(self.generate_l1e_file)
        self.actn_l2e_activity_increments.triggered.connect(self.generate_l2e_file)
        self.actn_l3e_activity_increments_and_decrements.triggered.connect(self.generate_l3e_file)
        self.actn_f1e_flow_defenitions.triggered.connect(self.generate_f1e_file)
        self.actn_p0e_transport_parameters.triggered.connect(self.generate_p0e_file)
        self.actn_p1e_network.triggered.connect(self.generate_p1e_file)
        self.actn_t1e_assignment_parameters.triggered.connect(self.generate_t1e_file)

        self.scenario_tree.clicked.connect(self.select_scenario)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)

        if self.project_file[-13:]=="""\W_TRANUS.CTL""":
            self.project_file = self.project_file.replace('\W_TRANUS.CTL','')
        
        # TODO: validate sequence events
        #Loads
        #self.__extract_db_files()
        self.__connect_database_sqlite()
        self.__load_scenarios()
        # self.load_data()

        # Thread to load information
        load_data_thread = threading.Thread(target=self.load_data, name='load_data')
        load_data_thread.start()

        self.__validate_buttons()
        self.validate_database()
        

    def network_data_fields(self):
        links_shape_codscenario = self.links_shape_codscenario.currentText()
        links_shape_origin = self.links_shape_origin.currentText()
        links_shape_destination = self.links_shape_destination.currentText()
        link_shape_id = self.links_shape_fields.currentText()
        links_shape_name = self.links_shape_name.currentText()
        links_shape_type = self.links_shape_type.currentText() 
        links_shape_length = self.links_shape_length.currentText()
        links_shape_direction = self.links_shape_direction.currentText()
        links_shape_capacity = self.links_shape_capacity.currentText()
        return dict(scenario=links_shape_codscenario, origin=links_shape_origin, destination=links_shape_destination, id=link_shape_id, name=links_shape_name, type=links_shape_type, 
                    length=links_shape_length, direction=links_shape_direction, capacity=links_shape_capacity)

    def node_data_fields(self):
        nodes_shape_fields = self.nodes_shape_fields.currentText()
        nodes_shape_name = self.nodes_shape_name.currentText()
        nodes_shape_type = self.nodes_shape_type.currentText()
        nodes_shape_x = self.nodes_shape_x.currentText()
        nodes_shape_y = self.nodes_shape_y.currentText()
        return dict(id=nodes_shape_fields, name=nodes_shape_name, typeNode=nodes_shape_type, x=nodes_shape_x, y=nodes_shape_y)


    def generate_input_files(self):
        result = self.dataBaseSqlite.selectAll(' scenario ')
        self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)

        self.scenarios_files.generate_ctl_file()
        self.scenarios_files.generate_l0e_file()
        self.scenarios_files.generate_z1e_file()
        for valor in result:
            id_scenario = valor[0]
            self.scenarios_files.write_f1e_file(id_scenario)
            self.scenarios_files.write_l1e_file(id_scenario)
            self.scenarios_files.write_l2e_file(id_scenario)
            self.scenarios_files.write_l3e_file(id_scenario)
            self.scenarios_files.write_p0e_file(id_scenario)
            self.scenarios_files.write_p1e_file(id_scenario)
            self.scenarios_files.write_t1e_file(id_scenario)


    def generate_single_scenario(self):
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.generate_single_scenario(id_scenario)

    def generate_ctl_file(self):
        """
            @summary: Set Scenario selected
        """
        self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
        self.scenarios_files.generate_ctl_file()


    def generate_z1e_file(self):
        """
            @summary: Set Scenario selected
        """
        self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
        self.scenarios_files.generate_z1e_file()


    def generate_l0e_file(self):
        """
            @summary: Set Scenario selected
        """
        self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
        self.scenarios_files.generate_l0e_file()


    def generate_f1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_f1e_file(id_scenario)


    def generate_l1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_l1e_file(id_scenario)


    def generate_l2e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_l2e_file(id_scenario)

    
    def generate_l3e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_l3e_file(id_scenario)
            

    
    def generate_p0e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_p0e_file(id_scenario)
            

    def generate_p1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_p1e_file(id_scenario)
            


    def generate_t1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.project_file, statusBar=self.statusBar)
            self.scenarios_files.write_t1e_file(id_scenario)


    def select_scenario(self, selectedIndex):
        """
            @summary: Set Scenario selected
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'data.html')
        webbrowser.open_new_tab(filename)
        
        
    def open_scenarios_window(self):
        """
            @summary: Opens data window
        """
        dialog = ScenariosDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()


    def open_import_network(self):
        """
            @summary: Opens data window
        """
        dialog = ImportsNetworkDialog(self.project_file, self.scenarioCode, parent = self,  networkShapeFields=self.network_data_fields())
        dialog.show()
        result = dialog.exec_()


    def open_overwrite_nodes(self):
        """
            @summary: Opens data window
        """
        self.statusBar.clearMessage()
        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Do you want overwrite nodes data?", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        selected = messagebox.exec_()

        if selected == QtWidgets.QMessageBox.Yes:    
            QApplication.setOverrideCursor(Qt.WaitCursor)

            self.__load_nodes_data("REPLACE")
            QApplication.restoreOverrideCursor()
            
            self.statusbar.showMessage("Success: Nodes data has been overwritten", 4000)

    def open_overwrite_zones(self):
        """
            @summary: Opens data window
        """
        self.statusBar.clearMessage()
        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Do you want overwrite zones data?", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        selected = messagebox.exec_()
        message = QtWidgets.QLabel()

        if selected == QtWidgets.QMessageBox.Yes:    
            QApplication.setOverrideCursor(Qt.WaitCursor)

            self.__load_zones_data("REPLACE")
            QApplication.restoreOverrideCursor()
            
            self.statusbar.showMessage("Success: Zones data has been overwritten", 4000)

        

    def open_overwrite_links(self):
        """
            @summary: Opens data window
        """
        
        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Do you want overwrite links data?", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        selected = messagebox.exec_()
        message = QtWidgets.QLabel()

        if selected == QtWidgets.QMessageBox.Yes:    
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            self.__load_network_data("REPLACE")
            QApplication.restoreOverrideCursor()

            self.statusbar.showMessage("Success: Links data has been overwritten", 4000)


    def open_links_window(self):
        """
            @summary: Opens data window
        """
        dialog = LinksDialog(self.project_file, self.scenarioCode, parent = self, networkShapeFields=self.network_data_fields())
        dialog.show()
        result = dialog.exec_()

    def open_nodes_window(self):
        """
            @summary: Opens data window
        """
        dialog = NodesDialog(self.project_file, self.scenarioCode, parent = self, nodeShapeFields=self.node_data_fields())
        dialog.show()
        result = dialog.exec_()
    
    def open_exgogenoustrips_window(self):
        """
        @summary: Opens data window
        """
        dialog = ExogeousTripsDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()
    

    def open_zones_window(self):
        """
            @summary: Opens data window
        """
        dialog = ZonesDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()

    def open_sectors_window(self):
        """
            @summary: Opens data window
        """
        dialog = SectorsDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_intersectors_window(self):
        """
            @summary: Opens intersectors window
        """
        dialog = IntersectorsDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_zonaldata_window(self):
        """
            @summary: Opens intersectors window
        """
        dialog = ZonalDataDialog(self.project_file,  self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()

    def open_categories_window(self):
        """
            @summary: Opens categories window
        """
        dialog = CategoriesDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_modes_window(self):
        """
            @summary: Opens modes window
        """
        dialog = ModesDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_operators_window(self):
        """
            @summary: Opens modes window
        """
        dialog = OperatorsDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()

    def open_transfers_window(self):
        """
            @summary: Opens modes window
        """    
        dialog = TransfersDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()
        
    def open_routes_window(self):
        """
            @summary: Opens modes window
        """
        dialog = RoutesDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()

    def open_administrators_window(self):
        """
            @summary: Opens administrators window
        """
        #print(self.scenarioSelectedIndex)
        dialog = AdministratorsDialog(self.project_file, self.scenarioCode, self.scenarioSelectedIndex, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_linktype_window(self):
        """
            @summary: Opens administrators window
        """
        dialog = LinkTypeDialog(self.project_file, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()


    def open_configuration_window(self):
        """
            @summary: Opens data window
        """
        dialog = ConfigurationDialog(self.project_file, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()
        

    def __connect_database_sqlite(self):
        if  not self.dataBaseSqlite.validateConnection():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Database conection unsatisfactory.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("DB File was not found.")
        else:
            print("DataBase Connection Successfully")
        

    def __validate_buttons(self):
        result_sector = self.dataBaseSqlite.selectAll(' sector ')
        result_category = self.dataBaseSqlite.selectAll(' category ')
        result_operator = self.dataBaseSqlite.selectAll(' operator ')
        result_administrator = self.dataBaseSqlite.selectAll(' administrator ')
        result_zone = self.dataBaseSqlite.selectAll(' zone ')
        result_node = self.dataBaseSqlite.selectAll(' node ')
        result_mode = self.dataBaseSqlite.selectAll(' mode ')

        if len(result_sector) > 0:
            self.btn_intersectors.setEnabled(True)
        else:
            self.btn_intersectors.setEnabled(False)

        if (len(result_sector) > 0) and (len(result_zone) > 0):
            self.btn_zonal_data.setEnabled(True)
        else:
            self.btn_zonal_data.setEnabled(False)

        if len(result_category) > 0:
            self.btn_operators.setEnabled(True)
        else:
            self.btn_operators.setEnabled(False)
            
        if len(result_operator) > 0:
            self.btn_transfers.setEnabled(True)
            self.btn_routes.setEnabled(True)
        else:
            self.btn_transfers.setEnabled(False)
            self.btn_routes.setEnabled(False)

        if len(result_operator) > 0 and len(result_administrator) > 0: 
            self.btn_link_types.setEnabled(True)
        else:
            self.btn_link_types.setEnabled(False)
            
        if (len(result_operator) > 0) and (len(result_node) > 0):
            self.btn_links.setEnabled(True)
        else:
            self.btn_links.setEnabled(False)

        if len(result_zone) > 0 and len(result_category) > 0 and len(result_mode) > 0:
            self.btn_exogenous_trips.setEnabled(True)
        else:
            self.btn_exogenous_trips.setEnabled(False)


    def __load_scenarios(self):
        self.scenarios_model = ScenariosModelSqlite(self.project_file)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenario_tree.setSelectionModel(modelSelection)

        
    def load_data(self):
        if self.zone_shape.text() != '':
            self.btn_zones.setEnabled(False)
            self.btn_zones.setText("Zones loading...")
            result_zones = self.__load_zones_data()
            self.btn_zones.setText("Zones")
            self.btn_zones.setEnabled(True)
        else:
            return False

        if result_zones != False and self.network_nodes_shape.text() != '':
            self.btn_nodes.setText("Nodes loading...")
            self.btn_nodes.setEnabled(False)
            result_nodes = self.__load_nodes_data()
            self.btn_nodes.setText("Nodes")
            self.btn_nodes.setEnabled(True)
        else:
            return False

        if  result_zones != False and result_nodes != False and self.network_links_shape.text() != '':
            self.btn_links.setEnabled(False)
            self.btn_links.setText("Links loading...")
            self.__load_network_data()
            self.btn_links.setText("Links")
            self.btn_links.setEnabled(True)
        else:   
            return False
        


    def __load_zones_data(self, typeSql="IGNORE"):
        shape = self.zone_shape.text()
        layer = QgsVectorLayer(shape, 'Zonas', 'ogr')
        
        try:
            if not layer.isValid():
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Zone is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
            else:
                zones_shape_fields = [field.name() for field in layer.fields()]
                features = layer.getFeatures()
                result_a = self.dataBaseSqlite.selectAll('zone', " where id = 0")
                if len(result_a)==0:
                    self.dataBaseSqlite.addZone(0, 'Global Increments')
                data_list = []

                zoneIdField = self.zones_shape_id.currentText()
                zoneNameField = self.zones_shape_name.currentText()
                for feature in features:
                    zoneId = feature.attribute(zoneIdField)
                    zoneName = feature.attribute(zoneNameField)[0:25] if feature.attribute(zoneNameField) else None
                    zoneName = re.sub(r'[^A-Za-z0-9 .]', '', zoneName)
                    result = self.dataBaseSqlite.selectAll('zone', " where id = {}".format(zoneId))
                    if typeSql == 'IGNORE':
                        if not (isinstance(zoneId, QVariant) and zoneId.isNull()):
                            if re.findall(r'\d+',str(zoneId)):
                                if len(result) == 0:
                                    data_list.append((zoneId, zoneName))
                            else:
                                raise ExceptionFormatID(zoneId, typeFile='Import error in Zone shape file')
                    elif typeSql == 'REPLACE':
                        if re.findall(r'\d+',str(zoneId)):
                            data_list.append((zoneId, zoneName))
                        #else:
                        #    raise ExceptionFormatID(zoneId, typeFile='Import error in Zone shape file')                     
                self.dataBaseSqlite.addZoneFFShape(data_list, typeSql=typeSql)

                return True
        except Exception as e:
            print(f"Error: {e}")
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Import error in zone Shape File.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False



    def __load_network_data(self, typeSql='IGNORE'):
        shape = self.network_links_shape.text()
        layer = QgsVectorLayer(shape, 'Network_Links', 'ogr')
        result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
        scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])

        try:
            if not layer.isValid():
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Network is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
            else:
                network_shape_fields = [field.name() for field in layer.fields()]
                features = layer.getFeatures()
                parent = self.parent()
                data_list = []
                for feature in layer.getFeatures():
                    scenarioField = self.links_shape_codscenario.currentText()
                    linkIdField = self.links_shape_fields.currentText()
                    linkNameField = self.links_shape_name.currentText()
                    typeField = self.links_shape_type.currentText()
                    lengthField = self.links_shape_length.currentText()
                    directionField = self.links_shape_direction.currentText()
                    capacityField = self.links_shape_capacity.currentText()
                    
                    linkId = feature.attribute(linkIdField) if linkIdField != 'Select' else '0-0'
                    # print(linkId.typeName())
                    if not (isinstance(linkId, QVariant) and linkId.isNull()): 
                        if re.findall(r'\d+-\d+',linkId):
                            
                            Or_node = linkId.split('-')[0]
                            Des_node = linkId.split('-')[1]
                            name = feature.attribute(linkNameField) if linkNameField != 'Select' else None
                            codScenario = feature.attribute(scenarioField) if scenarioField != 'Select' else None
                            idType = feature.attribute(typeField) if typeField != 'Select' else None
                            #two_way = 1 if (feature.attribute(directionField) if directionField != 'Select' else None)  == 0 else None
                            two_way = feature.attribute(directionField) if directionField != 'Select' else None 
                            length = feature.attribute(lengthField) if lengthField != 'Select' else None
                            capacity = feature.attribute(capacityField) if capacityField != 'Select' else None

                            # Optional parameter
                            codScenario = None if isinstance(codScenario, QVariant) else codScenario
                            name = None if isinstance(name, QVariant) and name.isNull() else name
                            resultOrNode = self.dataBaseSqlite.selectAll(" node ", where=f" where id = {Or_node}")
                            resultDesNode = self.dataBaseSqlite.selectAll(" node ", where=f" where id = {Des_node}")
                            name = None if isinstance(name, QVariant) else name
                            idType = None if isinstance(idType, QVariant) else idType
                            length = None if isinstance(length, QVariant) else length
                            two_way = None if isinstance(two_way, QVariant) else two_way
                            capacity = None if isinstance(capacity, QVariant) else capacity
                            if resultOrNode and resultDesNode:
                                data_list.append((codScenario, f"{Or_node}-{Des_node}", Or_node, Des_node, idType, length, two_way, capacity, name))
                                if two_way != None:
                                    data_list.append((codScenario, f"{Des_node}-{Or_node}", Des_node, Or_node, idType, length, two_way, capacity, name))
                            
                        else:
                            raise ExceptionFormatID(linkId, typeFile='Import error in Network shape file')             
                qry = """select 
                        distinct b.code, linkid, node_from, node_to, id_linktype, length, two_way, capacity, a.name
                        from link a
                        join scenario b on (a.id_scenario = b.id)"""

                result = self.dataBaseSqlite.executeSql(qry)
        
                """
                TODO: evaluate delete this section
                if len(data_list) >= len(result):
                    resultList = list(set(data_list) - set(result))
                else:
                    resultList = list(set(result) - set(data_list))
                """
                # result: database data
                # data_list: network shape file data
                resultList = Helpers.union_elements_by_column(result, data_list)

                if typeSql=='REPLACE':
                    # self.dataBaseSqlite.executeDML('delete from link')
                    resultList = data_list

                self.dataBaseSqlite.addLinkFFShape(scenarios_arr, resultList, typeSql=typeSql)

                return True
        except ExceptionFormatID as e:
            print("Error ExceptionFormatID: ", e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", str(e), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        except Exception as e:
            print("Error: ", e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Import error in network Shape File.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False


    def __load_nodes_data(self, typeSql="IGNORE"):
        shape = self.network_nodes_shape.text()
        layer = QgsVectorLayer(shape, 'Network_Nodes', 'ogr')
        result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
        try:
            if result:
                scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])
                if not layer.isValid():
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Layers is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    return False
                else:
                    network_shape_fields = [field.name() for field in layer.fields()]
                    features = layer.getFeatures()
                    idNode = self.nodes_shape_fields.currentText() if self.nodes_shape_fields.currentText() != 'Select' else None
                    typeNode = self.nodes_shape_type.currentText()  if self.nodes_shape_type.currentText() != 'Select' else None
                    nameNode = self.nodes_shape_name.currentText()  if self.nodes_shape_name.currentText() != 'Select' else None
                    xNode = self.nodes_shape_x.currentText()  if self.nodes_shape_x.currentText() != 'Select' else None
                    yNode = self.nodes_shape_y.currentText()  if self.nodes_shape_y.currentText() != 'Select' else None

                    data_list = []
                    for feature in features:
                        _id = feature.attribute(idNode) if idNode else None
                        if not (isinstance(_id, QVariant) and _id.isNull()): 
                            if re.findall(r'\d+',str(_id)):
                                id_type = feature.attribute(typeNode) if typeNode else None
                                name = feature.attribute(nameNode) if nameNode else None
                                name = None if str(name) == 'NULL' else name
                                description = None
                                x = feature.attribute(xNode) if xNode else None
                                y = feature.attribute(yNode) if yNode else None
                                x = None if str(x) == 'NULL' else x
                                y = None if str(y) == 'NULL' else y
                                print(f'x {x}')
                                print(f'y {y}')
                                
                                if not isinstance(_id, int):
                                    raise ExceptionWrongDataType(_id=_id, _field=idNode)
                                
                                if not isinstance(id_type, int):
                                    raise ExceptionWrongDataType(_id=_id, _field=typeNode)
                                
                                if x == None:
                                    raise ExceptionNullValue(_id=_id, _field=xNode)

                                if y == None:
                                    raise ExceptionNullValue(_id=_id, _field=yNode)
                                
                                data_list.append((_id, x, y, name, description, id_type))
                                
                            else:
                                raise ExceptionFormatID(_id, typeFile='Import error in Nodes shape file')
                    self.dataBaseSqlite.addNodeFShape(scenarios_arr, data_list, typeSql=typeSql)

                    return True   
        except ExceptionNullValue as e:
            print(f"Error ExceptionNullValue: {e}")
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Loading Nodes Error \n"+str(e), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False 
        except ExceptionWrongDataType as e:
            print(f"Error ExceptionWrongDataType: {e}")
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Loading Nodes Error \n"+str(e), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False                                                                                   
        except ExceptionWrongDataType as e:
            print(f"Error ExceptionWrongDataType: {e}")
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Loading Nodes Error \n"+str(e), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        except ExceptionFormatID as e:
            print(f"Error ExceptionFormatID: {e}")
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", str(e), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        except Exception as e:
            print(f"Error: {e}")
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error importing node shape file.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False

        
    def load_scenarios(self):
        self.__load_scenarios()
        

    def save_db(self):
        if(self.dataBase.save_db(self.project['project_file'], self.project.db_path, self.project.db_path, DBFiles.Scenarios, self.scenariosMatrix)):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "DB has been saved.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("DB has been saved.")
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "There was a problem trying to save DB, please verify and try again.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("There was a problem trying to save DB, please verify and try again.")


    def save_db_as(self):
        file_name = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Choose a file name to save the DB.', directory=self.project['project_file'], filter='*.*, *.zip')
        
        if file_name.strip() != '':
            if(self.dataBase.save_db(self.project['project_file'], self.project.db_path, file_name, DBFiles.Scenarios, self.scenariosMatrix)):
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


    def close_event(self, event):
        self.close()

    def linktypeWithoutDefinitions(self):
        sql = """
            select distinct a.id_linktype
            from link a
            left join link_type  b on (a.id_linktype = b.id)
            where b.id is null or b.id = ''
            order by 1
            """
        result = self.dataBaseSqlite.executeSql(sql)
        
        self.linktypesList = []
        for value in result:
            self.linktypesList.append(str(value[0]))

        return result

        
    def validate_database(self):
        result = self.linktypeWithoutDefinitions()

        if result:
            buttonDetail = QtWidgets.QPushButton("Info...")
            buttonDetail.clicked.connect(self.open_database_errors)
            mensaje = QtWidgets.QLabel()
            mensaje.setText( "<b>Warning:</b> Inconsistencies in database" )
            mensaje.setStyleSheet( "color : #D68910;" )
            
            self.statusbar.addWidget(mensaje)
            self.statusbar.addWidget(buttonDetail)
            

    def open_database_errors(self):
        """
            @summary: Scenario Errors Window
        """
        self.linktypeWithoutDefinitions()

        dialog = DatabaseErrorsDialog(self.project_file, self.linktypesList, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
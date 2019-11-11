    # -*- coding: utf-8 -*-
import os, re, webbrowser
from string import *

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QAbstractItemView, QStandardItemModel, QStandardItem, QMainWindow, QToolBar, QHBoxLayout
from PyQt5.QtCore import *

from qgis.core import QgsVectorLayer

from .classes.general.Helpers import Helpers
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
from .exogenous_trips_dialog import ExogeousTripsDialog
from .administrators_dialog import AdministratorsDialog
from .scenarios_select_dialog import ScenariosSelectDialog
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_excel_data_dialog import AddExcelDataDialog
from .imports_network_dialog import ImportsNetworkDialog
from .scenarios_model_sqlite import ScenariosModelSqlite


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'data.ui'))

class DataWindow(QMainWindow, FORM_CLASS):
    
    def __init__(self, layers_group_name, tranus_folder, parent = None):
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
        self.network_links_shape = parent.network_links_shape
        self.network_nodes_shape = parent.network_nodes_shape
        self.layers_group_name = layers_group_name
        self.tranus_folder = tranus_folder
        self.dataBase = DataBase()
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.scenarios =  None
        self.scenariosMatrix = None
        self.scenariosMatrixBackUp = None
        self.scenarioSelectedIndex = None
        self.scenarioCode = None
        
        
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
        
        """self.actn_scenarios = self.findChild(QtWidgets.QAction, 'actionScenarios')
        self.actn_options = self.findChild(QtWidgets.QAction, 'actionOptions')
        self.actn_zones = self.findChild(QtWidgets.QAction, 'actionZones')"""
        self.actn_imp_network = self.findChild(QtWidgets.QAction, 'actionImportNetwork')
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
        #self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_db)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close_event)

        #self.scenario_tree.selectionChanged(item)
        if self.tranus_folder[-13:]=="""\W_TRANUS.CTL""":
            self.tranus_folder = self.tranus_folder.replace('\W_TRANUS.CTL','')

        #Loads
        #self.__extract_db_files()
        self.__connect_database_sqlite()
        self.__load_scenarios()
        self.load_data()
        self.__validate_buttons()


    def generate_input_files(self):
        result = self.dataBaseSqlite.selectAll(' scenario ')
        self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)

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
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.generate_single_scenario(id_scenario)

    def generate_ctl_file(self):
        """
            @summary: Set Scenario selected
        """
        self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
        self.scenarios_files.generate_ctl_file()


    def generate_z1e_file(self):
        """
            @summary: Set Scenario selected
        """
        self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
        self.scenarios_files.generate_z1e_file()


    def generate_l0e_file(self):
        """
            @summary: Set Scenario selected
        """
        self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
        self.scenarios_files.generate_l0e_file()


    def generate_f1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.write_f1e_file(id_scenario)


    def generate_l1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.write_l1e_file(id_scenario)


    def generate_l2e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.write_l2e_file(id_scenario)

    
    def generate_l3e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.write_l3e_file(id_scenario)
            

    
    def generate_p0e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.write_p0e_file(id_scenario)
            

    def generate_p1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
            self.scenarios_files.write_p1e_file(id_scenario)
            


    def generate_t1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.scenarios_files = ScenariosFiles(self.tranus_folder, statusBar=self.statusBar)
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
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)
        
        
    def open_scenarios_window(self):
        """
            @summary: Opens data window
        """
        dialog = ScenariosDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()


    def open_import_network(self):
        """
            @summary: Opens data window
        """
        dialog = ImportsNetworkDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()


    def open_links_window(self):
        """
            @summary: Opens data window
        """
        dialog = LinksDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()

    def open_nodes_window(self):
        """
            @summary: Opens data window
        """
        dialog = NodesDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
    
    def open_exgogenoustrips_window(self):
        """
        @summary: Opens data window
        """
        dialog = ExogeousTripsDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()
    

    def open_zones_window(self):
        """
            @summary: Opens data window
        """
        dialog = ZonesDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()

    def open_sectors_window(self):
        """
            @summary: Opens data window
        """
        dialog = SectorsDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_intersectors_window(self):
        """
            @summary: Opens intersectors window
        """
        dialog = IntersectorsDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_zonaldata_window(self):
        """
            @summary: Opens intersectors window
        """
        dialog = ZonalDataDialog(self.tranus_folder,  self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()

    def open_categories_window(self):
        """
            @summary: Opens categories window
        """
        dialog = CategoriesDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_modes_window(self):
        """
            @summary: Opens modes window
        """
        dialog = ModesDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_operators_window(self):
        """
            @summary: Opens modes window
        """
        dialog = OperatorsDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()

    def open_transfers_window(self):
        """
            @summary: Opens modes window
        """    
        dialog = TransfersDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()
        
    def open_routes_window(self):
        """
            @summary: Opens modes window
        """
        dialog = RoutesDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()

    def open_administrators_window(self):
        """
            @summary: Opens administrators window
        """
        #print(self.scenarioSelectedIndex)
        dialog = AdministratorsDialog(self.tranus_folder, self.scenarioCode, self.scenarioSelectedIndex, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_linktype_window(self):
        """
            @summary: Opens administrators window
        """
        dialog = LinkTypeDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
        self.__validate_buttons()


    def open_configuration_window(self):
        """
            @summary: Opens data window
        """
        dialog = ConfigurationDialog(self.tranus_folder, parent = self)
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
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenario_tree.setSelectionModel(modelSelection)

        

    def load_data(self):
        
        if self.zone_shape.text() != '':
            self.__load_zones_data()
        else:
            return False

        if self.network_nodes_shape.text() != '':
            self.__load_nodes_data()
        else:
            return False

        if self.network_links_shape.text() != '':
            self.__load_network_data() 
        else:   
            return False
            


    def __load_zones_data(self):
        shape = self.zone_shape.text()
        layer = QgsVectorLayer(shape, 'Zonas', 'ogr')

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

            for feature in features:
                zoneId = feature.attribute('zoneID')
                zoneName = feature.attribute('zoneName')
                result = self.dataBaseSqlite.selectAll('zone', " where id = {}".format(zoneId))
                if len(result) == 0:
                    data_list.append((zoneId, zoneName))
            self.dataBaseSqlite.addZoneFFShape(data_list)

            return True

    def __load_network_data(self):
        shape = self.network_links_shape.text()
        layer = QgsVectorLayer(shape, 'Network_Links', 'ogr')
        result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
        scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])

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
                linkId = feature.attribute('LinkId')
                Or_node = feature.attribute('Or_node')
                Des_node = feature.attribute('Des_node')
            
                resultOrNode = self.dataBaseSqlite.selectAll(" node ", where=f" where id = {Or_node}")
                resultDesNode = self.dataBaseSqlite.selectAll(" node ", where=f" where id = {Des_node}")
                if resultOrNode and resultDesNode:
                    data_list.append((f"{Or_node}-{Des_node}", Or_node, Des_node))
            
            self.dataBaseSqlite.addLinkFFShape(scenarios_arr, data_list)

            return True

    def __load_nodes_data(self):
        shape = self.network_nodes_shape.text()
        layer = QgsVectorLayer(shape, 'Network_Nodes', 'ogr')
        result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
        if result:
            scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])
            if not layer.isValid():
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Layers is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                return False
            else:
                network_shape_fields = [field.name() for field in layer.fields()]
                features = layer.getFeatures()
                
                data_list = []
                for feature in features:
                    _id = feature.attribute('Id')
                    id_type = feature.attribute('Zone') if feature.attribute('Zone') else None
                    name = feature.attribute('name') if feature.attribute('name') else None
                    description = feature.attribute('descriptio') if feature.attribute('descriptio') else None
                    x = feature.attribute('X') if feature.attribute('X') else None
                    y = feature.attribute('Y') if feature.attribute('Y') else None
                    
                    data_list.append((_id, x, y, id_type, name, description))

                self.dataBaseSqlite.addNodeFShape(scenarios_arr, data_list)

                return True
        
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


    def close_event(self, event):
        self.close()
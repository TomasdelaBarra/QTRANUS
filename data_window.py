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
        
        self.actn_scenarios = self.findChild(QtWidgets.QAction, 'actionScenarios')
        self.actn_options = self.findChild(QtWidgets.QAction, 'actionOptions')
        self.actn_zones = self.findChild(QtWidgets.QAction, 'actionZones')
        #self.actn_import_transfers = self.findChild(QtWidgets.QAction, 'actionImport_Transfers')
        #self.actn_import_exogenous_trips = self.findChild(QtWidgets.QAction, 'actionImport_Exogenous_Trips')
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

        self.actn_scenarios.triggered.connect(self.open_scenarios_window)
        self.actn_zones.triggered.connect(self.open_zones_window)
        #self.actn_import_transfers.triggered.connect(self.open_import_transfers)
        #self.actn_import_exogenous_trips.triggered.connect(self.open_import_exogenous_trips)
        self.actn_options.triggered.connect(self.open_configuration_window)
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
        self.__validate_buttons()
        self.load_data()


    def generate_input_files(self):
        result = self.dataBaseSqlite.selectAll(' scenario ')
        self.generate_ctl_file()
        self.generate_l0e_file()
        self.generate_z1e_file()
        for valor in result:
            id_scenario = valor[0]
            self.write_f1e_file(id_scenario)
            self.write_l1e_file(id_scenario)
            self.write_l2e_file(id_scenario)
            self.write_l3e_file(id_scenario)
            self.write_p0e_file(id_scenario)
            self.write_p1e_file(id_scenario)
            self.write_t1e_file(id_scenario)


    def generate_single_scenario(self):
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_f1e_file(id_scenario)
            self.write_l1e_file(id_scenario)
            self.write_l2e_file(id_scenario)
            self.write_l3e_file(id_scenario)
            self.write_p0e_file(id_scenario)
            self.write_p1e_file(id_scenario)
            self.write_t1e_file(id_scenario)


    def generate_ctl_file(self):
        """
            @summary: Set Scenario selected
        """
        tabulate.PRESERVE_WHITESPACE = True
        header = self.dataBaseSqlite.selectAll(" project ")
        #scenarios = self.dataBaseSqlite.selectAll(" scenario ")
        scenarios = self.dataBaseSqlite.executeSql("select code, name, CASE cod_previous WHEN '' then ' ' else cod_previous end cod_previous from scenario")
        scenarios_header = ["'Code'", "'Name'", "'Prev'"]
        scenarios_data = [["'"+str(valor[0])+"'","'"+valor[1]+"'","'"+valor[2]+"'"] for valor in scenarios]

        # Study Area 
        study_header = ["'Code'","'Name'"]
        study_data = [["'"+str(header[0][1])+"'","'"+header[0][2]+"'"]]
        
        filename = "W_TRANUS.CTL"
        fh = None
        
        try:
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf8")
            fh.write("STUDY and SCENARIO DEFINITION -- File W_TRANUS.CTL \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("1.0 STUDY AREA IDENTIFICATION \n")
            fh.write(tabulate(study_data, tablefmt='plain', headers=study_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 SCENARIOS \n")
            fh.write(tabulate(scenarios_data, tablefmt='plain', headers=scenarios_header)+"\n")            
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 Model \n")
            fh.write("3.1 TRANS Use Logit model instead of Powit\n")
            fh.write("    1\n")
            fh.write("3.2 LOC Use Logit model instead of Powit \n")
            fh.write("    1\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def generate_z1e_file(self):
        """
            @summary: Set Scenario selected
        """
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}.Z1E".format(header[0][1])
        fh = None
        zones_first = self.dataBaseSqlite.selectAll(" zone ", columns=" id, name ", where=" where id > 0 and external is NULL", orderby=" order by 1 asc ")
        zones_external = self.dataBaseSqlite.selectAll(" zone ", columns=" id, name ", where=" where id > 0 and external == 1", orderby=" order by 1 asc ")
        zones_header = ["Zone", "'Name'"]
        zones_data = [[valor[0],"'"+str(valor[1])+"'"] for valor in zones_first]
        zones_data_ext = [[valor[0],"'"+str(valor[1])+"'"] for valor in zones_external]
        
        try:
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf8")
            fh.write("ZONE DEFINITION - File Z1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 FIRST LEVEL ZONES \n")
            fh.write(tabulate(zones_data, tablefmt='plain', headers=zones_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 SECOND LEVEL ZONES \n")
            fh.write("        Zone  SubZone 'Name'           SubZone 'Name'           SubZone 'Name'          ->/\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 EXTERNAL ZONES \n")
            fh.write(tabulate(zones_data_ext, tablefmt='plain', headers=zones_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def generate_l0e_file(self):
        """
            @summary: Set Scenario selected
        """
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}.L0E".format(header[0][1])
        zone_internal_header = ["Sector","Zone","ExogProd","InducedPro","ExogDemand","Price","ValueAdded","Attractor"]
        zone_export_header = ["Sector","Zone","Exports"]
        zone_import_header = ["Sector","Zone","Min Imp.","Max Imp.","Price","Attractor"]
        zone_prod_header = ["Sector","Zone","Min","Max"]
        fh = None
        qry_internal = """select 
                    id_sector, id_zone, coalesce(exogenous_production, 0), coalesce(induced_production, 0), 
                    coalesce(exogenous_demand, 0), coalesce(base_price, 0), coalesce(value_added, 0), coalesce(attractor, 0)
                    from 
                    zonal_data a 
                    join zone b on a.id_zone = b.id
                    where external is null and id_zone > 0"""

        result_internal = self.dataBaseSqlite.executeSql(qry_internal) 
        internal_data =[[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6],valor[7]] for valor in result_internal]

        qry_exports = """select 
                        id_sector, id_zone, coalesce(exports,0)
                        from 
                        zonal_data a 
                        join zone b on a.id_zone = b.id
                        where b.external = 1 and id_zone > 0"""

        result_export = self.dataBaseSqlite.executeSql(qry_exports) 
        export_data =[[valor[0],valor[1],valor[2]] for valor in result_export]

        qry_imports = """select 
                        id_sector, id_zone, coalesce(min_imports, 0), coalesce(max_imports, 0), 
                        coalesce(base_price, 0), coalesce(attractor, 0)
                        from 
                        zonal_data a 
                        join zone b on a.id_zone = b.id
                        where b.external = 1 and id_zone > 0"""

        result_imports = self.dataBaseSqlite.executeSql(qry_imports) 
        import_data =[[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5]] for valor in result_imports]

        qry_prod = """select 
                    id_sector, id_zone, coalesce(min_production, 0), coalesce(max_production, 0)
                    from 
                    zonal_data a 
                    join zone b on a.id_zone = b.id
                    where b.external is null and id_zone > 0"""

        result_prod = self.dataBaseSqlite.executeSql(qry_prod) 
        prod_data =[[valor[0],valor[1],valor[2],valor[3]] for valor in result_prod]
        try:
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf8")
            fh.write("LOCALIZATION DATA - File L0E  (QTRANUS v2019.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1. Base Year Data for Calibration \n")
            fh.write(" 1.1 Observed Data per Internal Zone \n")
            fh.write(tabulate(internal_data, tablefmt='plain', headers=zone_internal_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2. RELATIONSHIPS WITH EXTERNAL ZONES \n")
            fh.write(" 2.1 Exports \n")
            fh.write(tabulate(export_data, tablefmt='plain', headers=zone_export_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write(" 2.2 Imports \n")
            fh.write(tabulate(import_data, tablefmt='plain', headers=zone_import_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3. RESTRICTIONS TO PRODUCTION \n")
            fh.write(tabulate(prod_data, tablefmt='plain', headers=zone_prod_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()
    
    def write_f1e_file(self, id_scenario):

        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]

        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.F1E".format(header[0][1], codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        # 1.0 CATEGORY FORMATION FROM SOCIO-ECONOMIC SECTORS
        int_trans_cat =["Cat","Sector","Type","TimeF","VolumeF","Cons>Pro","Pro>Cons"]
        qry_trans_cat = """select id_category, id_sector, type, time_factor, 
                            volume_factor, flow_to_product, flow_to_consumer
                            from inter_sector_transport_cat
                            where id_scenario = {}""".format(id_scenario)
        result_trans_cat = self.dataBaseSqlite.executeSql(qry_trans_cat) 
        trans_cat_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_trans_cat] 
        
        # 2.0  INTRAZONAL COST PARAMETERS (ONLY FOR PROGRAM COST)
        int_zone_cost =["Zone","First Leve","Second Lev"]
        qry_trans_cat = """select id zone, internal_cost_factor
                        from zone 
                        where internal_cost_factor is not null"""
        result_zone_cost = self.dataBaseSqlite.executeSql(qry_trans_cat) 
        zone_cost_data = [[valor[0],valor[1],"/"] for valor in result_zone_cost] 

        #3.0  EXOGENOUS TRIPS
        #  3.1 Exogenous trips by transport category
        exogenous_trips_cat =["Cat","Orig","Dest","Trips", "Factor"]
        exogenous_cat = """select id_category, id_zone_from, id_zone_to, 
                        coalesce(trip,0) trip, coalesce(factor,0) factor 
                        from exogenous_trips
                        where id_scenario = {}""".format(id_scenario)
        result_exogenous_cat = self.dataBaseSqlite.executeSql(exogenous_cat) 
        exogenous_cat_data = [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_exogenous_cat] 
        
        #  3.0 Exogenous trips by transport category
        exogenous_trips_cat_mode =["Cat","Orig","Dest","Mode","Trips", "Factor"]
        exogenous_cat_mode = """select id_category, id_zone_from, id_zone_to, id_mode, 
                            coalesce(trip,0) trip, coalesce(factor,0) factor 
                            from exogenous_trips 
                            where id_scenario = {}""".format(id_scenario)
        result_exogenous_cat_mode = self.dataBaseSqlite.executeSql(exogenous_cat_mode) 
        exogenous_cat_mode_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5]] for valor in result_exogenous_cat_mode] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("LAND USE - TRANSPORT INTERFACE - File F1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 CATEGORY FORMATION FROM SOCIO-ECONOMIC SECTORS \n")
            fh.write(tabulate(trans_cat_data, tablefmt='plain', headers=int_trans_cat)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0  INTRAZONAL COST PARAMETERS (ONLY FOR PROGRAM COST) \n")
            fh.write(tabulate(zone_cost_data, tablefmt='plain', headers=int_zone_cost)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0  EXOGENOUS TRIPS \n")
            fh.write("     3.1 Exogenous trips by transport category \n")
            fh.write(tabulate(exogenous_cat_data, tablefmt='plain', headers=exogenous_trips_cat)+"\n")
            fh.write("     3.2 Exogenous trips by transport category and mode \n")
            fh.write(tabulate(exogenous_cat_mode_data, tablefmt='plain', headers=exogenous_trips_cat_mode)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def generate_f1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_f1e_file(id_scenario)


    def generate_l1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_l1e_file(id_scenario)


    def generate_l2e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_l2e_file(id_scenario)

    
    def generate_l3e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_l3e_file(id_scenario)

    
    def generate_p0e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_p0e_file(id_scenario)

    def generate_p1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_p1e_file(id_scenario)


    def generate_t1e_file(self):
        """
            @summary: Set Scenario selected
        """
        dialog = ScenariosSelectDialog(self.tranus_folder, parent = self)
        dialog.show()
        result = dialog.exec_()
        if dialog.idScenario != None:
            id_scenario = dialog.idScenario
            self.write_t1e_file(id_scenario)


    def write_l1e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]

        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.L1E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        
        sector_header = ["\nSector","\nName", "Utility\nLev1","\nLev2","Price\nLev1","\nLev2","Logit\nScale","Atrac\nFactor","Price-Cost\nRatio","Sector\nType","Target\nSector"]
        qry_sectors = """select id sector, name, coalesce(location_choice_elasticity,0) utility_lvl1, 
                    coalesce(location_choice_elasticity,0) as utility_lvl2, 1 as price_lvl1, 
                    0  as price_lvl2, 1 as logic_scale , coalesce(atractor_factor,0), 0 price_cost_ratio, 0 sector_type, '' target_sector 
                    from 
                    sector""" 

        result_sector = self.dataBaseSqlite.executeSql(qry_sectors) 
        sector_data =[[valor[0],"'"+valor[1]+"'",valor[2],valor[3],valor[4],valor[5],valor[6],valor[7],valor[8],valor[9], "/"] for valor in result_sector]

        demand_func_para = ["Sector","Input","MinCons","MaxCons","Elast"]
        qry_demand_func = """
                    select  id_sector sector, id_input_sector input, coalesce(min_demand,0) mincons, coalesce(max_demand,0) maxcons, coalesce(elasticity,0) elast
                    from inter_sector_inputs
                    where id_scenario = {}""".format(id_scenario)
        result_demand_func = self.dataBaseSqlite.executeSql(qry_demand_func) 
        demand_func_data =[[valor[0],valor[1],valor[2],valor[3],str(valor[4])+" /"] for valor in result_demand_func]
 
        demand_subs = ["Sector","SustElast","LogitSc","Subst","Penal .../"]
        qry_demand_subs = """
                    select id_sector sector, coalesce(substitute,0) subselast, 1 logicsc, id_sector sector, 1 penal 
                    from inter_sector_inputs 
                    where id_scenario = {}""".format(id_scenario)
        result_demand_subs = self.dataBaseSqlite.executeSql(qry_demand_subs) 
        demand_subs_data =[[valor[0],valor[1],valor[2],valor[3], '/'] for valor in result_demand_subs]

        attrac_exog =["Sect","AttracSe","Lev1","Lev2","ProdFac","PriceFac","CapFac"]
        qry_attractors_exog = """select id_sector sector, id_sector attrac_sector, 0 lvl1, 0 lvl2, coalesce(exog_prod_attractors,0) prodfact,
                            0 pricefactor, 0 capfact
                            from inter_sector_inputs 
                            where id_scenario = {}""".format(id_scenario)
        result_attra_exog = self.dataBaseSqlite.executeSql(qry_attractors_exog) 
        attractors_exog_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_attra_exog]  

        attrac_ind =["Sector","Var","Lev1","Lev2"]
        qry_attra_ind = """select id_sector sector, id_sector var, 
                            coalesce(ind_prod_attractors,0) lvl1, 0 lvl2
                            from inter_sector_inputs 
                            where id_scenario = {}""".format(id_scenario)
        result_attra_ind = self.dataBaseSqlite.executeSql(qry_attra_ind) 
        attractors_ind_data = [[valor[0],valor[1],valor[2],valor[3]] for valor in result_attra_ind] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("ACTIVITY LOCATION PARAMETERS - File L1E  (QTRANUS v2019.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0  GLOBAL PARAMETERS \n")
            fh.write("      Iterations     Convergenc\n")
            fh.write("              {}             {}      /\n".format(result[0][2] or 0, result[0][3]))
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 SOCIOECONOMIC SECTORS \n")
            fh.write("  2.1 Locational Utility Function Parameters \n")
            fh.write(tabulate(sector_data, tablefmt='plain', headers=sector_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("  2.2 Demand Function Parameters \n")
            fh.write(tabulate(demand_func_data, tablefmt='plain', headers=demand_func_para)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("  2.3 Demand Substitutions \n")
            fh.write(tabulate(demand_subs_data, tablefmt='plain', headers=demand_subs)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 ATRACTION VARIABLES AND PARAMETERS \n")
            fh.write("   3.1 Atractors for Increments in Exogenous Variables \n")
            fh.write(tabulate(attractors_exog_data, tablefmt='plain', headers=attrac_exog)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("   3.2 Atractors for Induced Production \n")
            fh.write(tabulate(attractors_ind_data, tablefmt='plain', headers=attrac_ind)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def write_l2e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.L2E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")

        #1.1 
        global_increments_head = ["Sector","Production","Demand","MinRest","MaxRest"]
        qry_global_incre = """select 
                                   id_sector sector, coalesce(induced_production,0) induced_production,
                                   coalesce(exogenous_demand, 0) exogenous_demand, 
                                   coalesce(min_production,0) min_production, 
                                   coalesce(max_production,0) max_production
                                from 
                                 zonal_data a
                                where a.id_zone = 0 and id_scenario = {} order by 1 asc""".format(id_scenario)
        result_global_incre = self.dataBaseSqlite.executeSql(qry_global_incre)
        global_data =  [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_global_incre]

        #1.2 
        int_exog_prods_head = ["Sector","Zone","Increment"]
        qry_exog_prod_incre = """select id_sector sector, id_zone zone, 
                            coalesce(exogenous_production,0) exogenous_production
                            from zonal_data a
                            where a.id_zone != 0 and id_scenario = {} order by 2,1""".format(id_scenario)
        result_int_exog_prod = self.dataBaseSqlite.executeSql(qry_exog_prod_incre)
        int_exog_prod_data =  [[valor[0],valor[1],valor[2]] for valor in result_int_exog_prod]

        #1.3 
        int_exog_demand_head = ["Sector","Zone","Increment"]
        qry_exog_demand_incre = """select id_sector sector, id_zone zone, 
                            coalesce(exogenous_demand,0) exogenous_demand
                            from zonal_data a
                            where a.id_zone != 0 and id_scenario = {}  order by 2,1""".format(id_scenario)
        result_int_demand_prod = self.dataBaseSqlite.executeSql(qry_exog_demand_incre)
        int_exog_demand_data =  [[valor[0],valor[1],valor[2]] for valor in result_int_demand_prod]

        #2.1
        int_ext_zone_exp_head = ["Sector","Zone","Increment"]
        qry_ext_zone_exp = """select 
                                    id_sector sector, id_zone zone, 
                                    coalesce(exports, 0) exports
                                from zonal_data a 
                                join zone b on (a.id_zone = b.id)
                                where a.id_zone != 0 and b.external = 1 and id_scenario = {} order by 2,1""".format(id_scenario)
        result_ext_zone_prod = self.dataBaseSqlite.executeSql(qry_ext_zone_exp)
        int_ext_zone_data =  [[valor[0],valor[1],valor[2]] for valor in result_ext_zone_prod]

        #2.2
        int_imp_zone_exp_head = ["Sector","Zone","Min Incr.", "Max Incr.", "Attractor"]
        qry_imp_zone_exp = """select 
                                    id_sector sector, id_zone zone, 
                                    coalesce(min_imports, 0) min_imports, 
                                    coalesce(max_imports, 0) max_imports, 
                                    coalesce(attractor,0) attractor
                                from zonal_data a 
                                join zone b on (a.id_zone = b.id)
                                where b.external = 1 and id_scenario = {}  order by 2,1 """.format(id_scenario)
        result_imp_zone_prod = self.dataBaseSqlite.executeSql(qry_imp_zone_exp)
        int_imp_zone_data =  [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_imp_zone_prod]

        #3.1
        int_endvar_head = ["Sector","Zone","Attractor"]
        qry_endvar = """select 
                                    id_sector sector, id_zone zone, 
                                    coalesce(attractor, 0) attractor
                                from zonal_data a 
                                join zone b on (a.id_zone = b.id) 
                                where a.id_zone != 0 and a.id_scenario = {} order by 2,1""".format(id_scenario)
        result_endvar = self.dataBaseSqlite.executeSql(qry_endvar)
        int_endvar_data =  [[valor[0],valor[1],valor[2]] for valor in result_endvar]

        #3.2
        int_prod_head = ["Sector","Zone","MinRest", "MaxRest"]
        qry_prod = """select 
                        id_sector sector, id_zone zone, 
                        coalesce(min_production,0) min_production, 
                        coalesce(max_production,0) max_production
                    from zonal_data 
                    where id_zone != 0 and id_scenario = {}  order by 2,1""".format(id_scenario)
        result_prod = self.dataBaseSqlite.executeSql(qry_prod)
        int_prod_data =  [[valor[0],valor[1],valor[2],valor[3]] for valor in result_prod]

        #3.3
        int_value_add_head = ["Sector","Zone","ValueAdded"]
        qry_value_add = """select 
                        id_sector sector, id_zone zone, 
                        coalesce(min_production,0) min_production, 
                        coalesce(max_production,0) max_production
                    from zonal_data
                    where id_zone != 0 and id_scenario = {}  order by 2,1""".format(id_scenario)
        result_value_add = self.dataBaseSqlite.executeSql(qry_value_add)
        int_value_add_data =  [[valor[0],valor[1],valor[2]] for valor in result_value_add]

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("LOCALIZATION DATA - File L2E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 INCREMENTS IN EXOGENOUS VARIABLES \n")
            fh.write("    1.1 Global Increments\n")
            fh.write(tabulate(global_data, tablefmt='plain', headers=global_increments_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    1.2 Increments in Exogenous Production per Internal Zone\n")
            fh.write(tabulate(int_exog_prod_data, tablefmt='plain', headers=int_exog_prods_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    1.3 Increments in Exogenous Demand per Internal Zone\n")
            fh.write(tabulate(int_exog_demand_data, tablefmt='plain', headers=int_exog_demand_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 INCREMENTS IN IMPORTS AND EXPORTS \n")
            fh.write("    2.1 Increments in Exports by External Zone\n")
            fh.write(tabulate(int_ext_zone_data, tablefmt='plain', headers=int_ext_zone_exp_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.2 Increments in Imports by External Zone\n")
            fh.write(tabulate(int_imp_zone_data, tablefmt='plain', headers=int_imp_zone_exp_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 INCREMENTS IN ENDOGENOUS VARIABLES \n")
            fh.write("    3.1 Increments in Location Atractors by Sector and Zone (Zone=0 means 'All Zones')\n")
            fh.write(tabulate(int_endvar_data, tablefmt='plain', headers=int_endvar_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    3.2 Increments in Production Restriction per Sector-Zone\n")
            fh.write(tabulate(int_prod_data, tablefmt='plain', headers=int_prod_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    3.3 Increments in Value Added by Sector-Zone (Zone=0 means All Zones)  \n")
            fh.write(tabulate(int_value_add_data, tablefmt='plain', headers=int_value_add_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def write_l3e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.L3E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("ALLOCATION OF CHANGES IN EXOGENOUS VARIABLES - File L3E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 INECREMENTS/DECREMENTS IN EXOGENOUS VARIABLES \n")
            fh.write("      Sector 'Variable'      'Func'               Value   Constant [AttracS 'AttracVar'         Param]  .../ \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()

    def write_p0e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """

        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.P0E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        # 2.1 TRANSPORT DEMAND CATEGORIES
        trans_mode_head =["No.","'Name'","Paths","Overlapp","ASC"]
        qry_trans_mode = """select a.id, name, coalesce(maximum_number_paths,0), 
                            coalesce(path_overlapping_factor,0), 0 asc
                        from mode a"""
        result_trans_mode = self.dataBaseSqlite.executeSql(qry_trans_mode) 
        trans_mode_data = [[valor[0],"'"+valor[1]+"'",valor[2], valor[3], "%s /" % valor[4]  ] for valor in result_trans_mode] 

        # 2.2
        trans_ope_head =["No","'Name'","Mode","Type","OccRate","Penaliz","MinWait","MaxWait","PathASC"]
        qry_ope = """select a.id, a.name, a.id_mode mode, a.type, coalesce(a.basics_occupency,0) occupency, 
                            coalesce(a.basics_modal_constant,0) penaliz, 
                            coalesce(a.basics_fixed_wating_factor,0)  minwait,  0 maxwait, 0 path_asc 
                            from operator a
                            join scenario_operator b on (a.id = b.id_operator)
                            where b.id_scenario = {}""".format(id_scenario)
        result_ope = self.dataBaseSqlite.executeSql(qry_ope) 
        ope_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3],valor[4],valor[5],valor[6],valor[7],str(valor[8])+" /"] for valor in result_ope] 
        
        # 2.3
        trans_route_head =["No","'Name'","Oper","MinFreq","MaxFreq","Tartet Occ","MaxFleet","Scheduled"]
        qry_route = """select a.id, a.name, a.id_operator, a.frequency_from, 
                    a.frequency_to, a.target_occ/100, a.max_fleet, a.follows_schedule
                    from route a
                    join scenario_route b on (a.id = b.id_route)
                    where b.id_scenario = {} and used = 1""".format(id_scenario)
        result_route = self.dataBaseSqlite.executeSql(qry_route) 
        route_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3],valor[4],valor[5],valor[6],str(valor[7])+" /"] for valor in result_route] 

        # 2.4
        trans_adm_head =["No","'Name'"]
        qry_adm = """select a.id, name  
                     from administrator a
                     join scenario_administrator b on (a.id = b.id_administrator)
                     where id_scenario = {} """.format(id_scenario)
        result_adm = self.dataBaseSqlite.executeSql(qry_adm) 
        adm_data = [[valor[0],"'"+str(valor[1])+"'"] for valor in result_adm] 

        # 2.5
        trans_lynkt_head =["No","'Name'","Admin","MinMaintCo"]
        qry_lynkt = """select a.id, name, id_administrator, min_maintenance_cost 
                        from link_type a
                        join scenario_linktype b on (a.id = b.id_linktype)
                        where b.id_scenario = {}""".format(id_scenario)
        result_lynkt = self.dataBaseSqlite.executeSql(qry_lynkt) 
        lynkt_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3]] for valor in result_lynkt] 

        # 3.0
        trans_cat_head =["No","'Name'","VofTrTime","VofWtTime", "Available Modes"]
        qry_cat = """select id, name, volumen_travel_time, value_of_waiting_time, id_mode 
                    from category"""
        result_cat = self.dataBaseSqlite.executeSql(qry_cat) 
        cat_data = [[valor[0],"'"+str(valor[1])+"'",valor[2],valor[3],valor[4]] for valor in result_cat] 

        # 4.1
        cost_ener_head =["Oper", "MinCons", "MaxCons","Slope","EnerCost","CtOpCost","TimeOpCost"]
        qry_cost_ener = """select a.id, coalesce(a.energy_min,0) energy_min, coalesce(a.energy_max,0) energy_max, 
                        coalesce(a.energy_slope,0) energy_slope, coalesce(a.energy_cost,0) energy_cost,
                        coalesce(a.cost_time_operation,0) cost_time_operation, coalesce(a.cost_porc_paid_by_user, 0) cost_porc_paid_by_user
                        from operator a
                        join scenario_operator b on (a.id = b.id_operator)
                        where b.id_scenario = {}""".format(id_scenario)
        result_cost_ener = self.dataBaseSqlite.executeSql(qry_cost_ener) 
        cost_ener_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_cost_ener] 

        # 4.2
        cost_header =["Type", "Oper", "Speed","EqVeh","DistCost","Toll","Maint","Penal"]
        qry_cond = """select 
                        CAST(a.id_linktype as integer) id_linktype, a.id_operator, coalesce(speed,0), coalesce(equiv_vahicules,0), coalesce(distance_cost,0), 
                        coalesce(charges,0) toll, coalesce(margin_maint_cost,0), coalesce(penaliz,0)
                        from link_type_operator a
                        join scenario_operator b on (a.id_operator = b.id_operator)
                        where b.id_scenario = {}
                        order by 1,2 """.format(id_scenario)
        result_cond = self.dataBaseSqlite.executeSql(qry_cond) 
        cost_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6],valor[7]] for valor in result_cond] 
        
        # 4.3
        overlap_head =["Type", "Oper", "Overlap"]
        qry_overlap = """select 
                        CAST(a.id_linktype as integer) id_linktype, a.id_operator, coalesce(overlap_factor,0) overlap_factor
                        from link_type_operator a
                        join scenario_operator b on (a.id_operator = b.id_operator)
                        where b.id_scenario = {}
                        order by 1,2 """.format(id_scenario)
        result_overlap = self.dataBaseSqlite.executeSql(qry_overlap) 
        overlap_data = [[valor[0],valor[1],valor[2]] for valor in result_overlap] 

        # 5.1
        tariff_head =["Oper","MinTarf","TimeTarf","DistTarf.","OperCost"]
        qry_tariff = """select a.id, basics_boarding_tariff, basics_time_tariff,  
                        basics_time_tariff, cost_porc_paid_by_user/100  
                        from operator a
                        join scenario_operator b on (a.id = b.id_operator)
                        where b.id_scenario = {}""".format(id_scenario)
        result_tariff = self.dataBaseSqlite.executeSql(qry_tariff) 
        tariff_data = [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_tariff] 

        # 5.2
        transfer_head =["FromOper","ToOper","Tariff"]
        qry_transfer = """select id_operator_from, id_operator_to, cost
                        from transfer_operator_cost
                        where id_scenario = {} order by 1,2 """.format(id_scenario)
        result_transfer = self.dataBaseSqlite.executeSql(qry_transfer) 
        transfer_data = [[valor[0],valor[1],valor[2]] for valor in result_transfer]

        # 5.3
        cat_cost_head =["Cat","Oper","Penal F.","Tariff F..","ASC"]
        qry_cat_cost = """select id_category, id_operator, tariff_factor, penal_factor, 0 asc
                        from operator_category"""
        result_cat_cost = self.dataBaseSqlite.executeSql(qry_cat_cost) 
        cat_cost_data = [[valor[0],valor[1],valor[2],valor[3],str(valor[4])+" /"] for valor in result_cat_cost] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("TRANSPORT PARAMETERS - File P0E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 GLOBAL PARAMETERS \n")
            fh.write("    For TRANUS Internal Use \n")
            fh.write("    60 \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 TRANSPORT DEMAND CATEGORIES\n")
            fh.write("    2.1 Transport Modes \n")
            fh.write(tabulate(trans_mode_data, tablefmt='plain', headers=trans_mode_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.2 Transport Operators (Type: 1=Free 2=Public 3=Routes 4=Walking)\n")
            fh.write(tabulate(ope_data, tablefmt='plain', headers=trans_ope_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.3 Public Transit Routes\n")
            fh.write(tabulate(route_data, tablefmt='plain', headers=trans_route_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.4 Administrators\n")
            fh.write(tabulate(adm_data, tablefmt='plain', headers=trans_adm_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.5 Link Types\n")
            fh.write(tabulate(lynkt_data, tablefmt='plain', headers=trans_lynkt_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 TRANSPORT DEMAND CATEGORIES\n")
            fh.write(tabulate(cat_data, tablefmt='plain', headers=trans_cat_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("4.0 COSTS AND OPERATING CONDITIONS \n")
            fh.write("    4.1 Energy and other operating costs per vehicle \n")
            fh.write(tabulate(cost_ener_data, tablefmt='plain', headers=cost_ener_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    4.2 Operating costs and conditions by link type \n")
            fh.write(tabulate(cost_data, tablefmt='plain', headers=cost_header)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    4.3 Path overlap factor by Link-Type & Operator \n")
            fh.write(tabulate(overlap_data, tablefmt='plain', headers=overlap_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("5.0 USER TARIFFS \n")
            fh.write("    5.1 Linear tariffs by operator \n")
            fh.write(tabulate(tariff_data, tablefmt='plain', headers=tariff_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    5.2 Integrated tarifs between operators (-1 if no transfers) \n")
            fh.write(tabulate(transfer_data, tablefmt='plain', headers=transfer_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    5.3 Tariff Factors by Category/Operator \n")
            fh.write(tabulate(cat_cost_data, tablefmt='plain', headers=cat_cost_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")

            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


    def write_p1e_file(self,id_scenario):
        """
            @summary: Set Scenario selected
        """
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.P1E".format(header[0][1],codeScenario)
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")
        
        net_head =["Src","Dest","GISId","Type","Dist.","Capac.","Delay Routes..","0 Restricted Turns..../"]
        qry_net = """select  node_from, node_to, id, coalesce(id_linktype,1), coalesce(distance,0), 
                        coalesce(capacity,0), coalesce(delay,0), '' restricted
                        from network order by 1"""
        result_net = self.dataBaseSqlite.executeSql(qry_net) 
        net_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6],str(valor[7])+" /"] for valor in result_net] 

        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("TRANSPORT NETWORK DEFINITION - File P1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("2.0 DELETED LINKS \n")
            fh.write("    For TRANUS Internal Use \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 MODIFIED LINKS \n")
            fh.write("         Src     Dest    GISId     Type      Dist.     Capac.      Delay Routes..  0 Restricted Turns.... / \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("3.0 NEW LINKS \n")
            fh.write(tabulate(net_data, tablefmt='plain', headers=net_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("4.0 INTERSECTION DELAYS \n")
            fh.write("         Src      Dst     Node      Delay \n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()

    def write_t1e_file(self, id_scenario):
        """
            @summary: Set Scenario selected
        """
        
        codeScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(id_scenario))
        codeScenario = codeScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        filename = "W_{}{}.T1E".format(header[0][1],codeScenario)
        fh = None
        result = self.dataBaseSqlite.selectAll(" config_model ", " where type = 'transport'")

        # 1.0
        global_head =["Iterations","Convergenc"]
        qry_global = """select iterations, convergence 
                        from config_model
                        where type='transport'"""

        result_global = self.dataBaseSqlite.executeSql(qry_global) 
        global_data = [[valor[0],valor[1]] for valor in result_global]

        # 2.1
        ope_simu_head =["Oper","TimeFactor","ConsolPar"]
        qry_ope_simu = """select a.id, basics_time_factor, -1 cosolpar
                        from operator a
                        join scenario_operator b on (a.id = b.id_operator)
                        where b.id_scenario = {}""".format(id_scenario)
                    
        result_ope_simu = self.dataBaseSqlite.executeSql(qry_ope_simu) 
        ope_simu_data = [[valor[0],valor[1],valor[2]] for valor in result_ope_simu]

        # 2.2
        restr_head =["Link\nType","% Reduct\nat V/C=1","% Reduct\nMax", "V/C for\nMin Vel","Capacity\nFactor"]
        qry_restr = """select a.id, perc_speed_reduction_vc/100, perc_max_speed_reduction/100, 
                        vc_max_reduction/100, capacity_factor/100 
                        from link_type a
                        join scenario_route b on (a.id = b.id_route)
                        where b.id_scenario = {}""".format(id_scenario)
        result_restr = self.dataBaseSqlite.executeSql(qry_restr) 
        restr_data = [[valor[0],valor[1],valor[2],valor[3],valor[4]] for valor in result_restr]

        # 2.3
        trip_gen_head =["Cat","MinGen","MaxGen", "GenElast","ModeElast","Logit Sc","CarAvail"]
        qry_trip_gen = """select id, min_trip_gener, max_trip_gener, 
                    elasticity_trip_gener, 1 modeelast, 1 logitsc, 1 caravail 
                    from category"""
        result_trip_gen = self.dataBaseSqlite.executeSql(qry_trip_gen) 
        trip_gen_data = [[valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6]] for valor in result_trip_gen]
        
        # 2.4
        path_head =["Cat","PathChElas","Logit Sc"]
        qry_path = """select id, choice_elasticity, 1 logitsc 
                        from category"""
        result_path = self.dataBaseSqlite.executeSql(qry_path) 
        path_data = [[valor[0],valor[1],valor[2]] for valor in result_path]
        
        try:
            if not os.path.exists("{}/{}".format(self.tranus_folder, codeScenario)):
                    os.mkdir("{}/{}".format(self.tranus_folder, codeScenario))
            fh = open("{}/{}/{}".format(self.tranus_folder, codeScenario, filename), "w", encoding="utf8")
            fh.write("TRANSPORT ASSIGNMENT PARAMETERS - File T1E  (QTRANUS v19.04.15 )\n"
                    "Study: {} {} \n".format(header[0][1], header[0][2]))
            fh.write("------------------------------------------------------------------------- /\n")
            fh.write("1.0 GLOBAL PARAMETERS \n")
            fh.write("    Iterations Convergenc \n")
            fh.write(tabulate(global_data, tablefmt='plain', headers=global_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("2.0 Simulation Parameters \n")
            fh.write("    2.1 Operator Parameters \n")
            fh.write(tabulate(ope_simu_data, tablefmt='plain', headers=ope_simu_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.2 Capacity Restriction Parameters \n")
            fh.write(tabulate(restr_data, tablefmt='plain', headers=restr_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.3 Trip generation and modal split \n")
            fh.write(tabulate(trip_gen_data, tablefmt='plain', headers=trip_gen_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            fh.write("    2.4 Path Choice Parameters \n")
            fh.write(tabulate(path_data, tablefmt='plain', headers=path_head)+"\n")
            fh.write("*------------------------------------------------------------------------- /\n")
            
            self.statusBar.showMessage("File: {}/{}/{}".format(self.tranus_folder, codeScenario, filename))

        except Exception as e:
            print(e)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Error while generate input files.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        finally:
            fh.close()


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
    
    """def open_import_transfers(self):
        dialog = AddExcelDataDialog(self.tranus_folder, parent = self, _type='transfers')
        dialog.show()
        result = dialog.exec_()
    
    def open_import_exogenous_trips(self):
        dialog = AddExcelDataDialog(self.tranus_folder, parent = self, _type='exogenous_trips')
        dialog.show()
        result = dialog.exec_()"""
        
        
    def open_scenarios_window(self):
        """
            @summary: Opens data window
        """
        dialog = ScenariosDialog(self.tranus_folder, parent = self)
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
        dialog = SectorsDialog(self.tranus_folder, self.scenarioSelectedIndex, parent = self)
        dialog.show()
        result = dialog.exec_()
        self.__validate_buttons()

    def open_intersectors_window(self):
        """
            @summary: Opens intersectors window
        """
        dialog = IntersectorsDialog(self.tranus_folder, self.scenarioCode, parent = self)
        dialog.show()
        #result = dialog.exec_()
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
        dialog = CategoriesDialog(self.tranus_folder, parent = self)
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
        
    """def __extract_db_files(self):
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
                print("DB files could not be extracted.")"""
    
    def __validate_buttons(self):
        result = self.dataBaseSqlite.selectAll(' sector ')
        if len(result)>=1:
            self.btn_intersectors.setEnabled(True)
        else:
            self.btn_intersectors.setEnabled(False)

    def __load_scenarios(self):
        self.scenarios_model = ScenariosModelSqlite(self.tranus_folder)
        self.scenario_tree.setModel(self.scenarios_model)
        self.scenario_tree.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenario_tree.setSelectionModel(modelSelection)

        

    def load_data(self):
        if self.__load_zones_data():
            self.btn_zonal_data.setEnabled(True)
        else:
            self.btn_zonal_data.setEnabled(False)

        if self.__load_network_data():
            self.btn_link_types.setEnabled(True)
        else:
            self.btn_link_types.setEnabled(False)

        if self.__load_nodes_data():
            self.btn_link_types.setEnabled(True)
        else:
            self.btn_link_types.setEnabled(False)


    def __load_zones_data(self):
        shape = self.zone_shape.text()
        layer = QgsVectorLayer(shape, 'Zonas', 'ogr')
        if not layer.isValid():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Layers is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        else:
            zones_shape_fields = [field.name() for field in layer.fields()]
            features = layer.getFeatures()
            result_a = self.dataBaseSqlite.selectAll('zone', " where id = 0")
            if len(result_a)==0:
                self.dataBaseSqlite.addZone(0, 'Global Increments')
                
            for feature in features:
                zoneId = feature.attribute('zoneID')
                zoneName = feature.attribute('zoneName')
                result = self.dataBaseSqlite.selectAll('zone', " where id = {}".format(zoneId))
                if len(result) == 0:
                    self.dataBaseSqlite.addZone(zoneId, zoneName)

            return True

    def __load_network_data(self):
        shape = self.network_links_shape.text()
        layer = QgsVectorLayer(shape, 'Network_Links', 'ogr')
        result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
        scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])

        if not layer.isValid():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Layers is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        else:
            network_shape_fields = [field.name() for field in layer.fields()]
            features = layer.getFeatures()
            result = self.dataBaseSqlite.executeSql("select count(*) from link")
            parent = self.parent()
            parent.pg_loading.setVisible(True)
            parent.pg_loading.setEnabled(True)
            parent.lbl_loading.setEnabled(True)
            pg_increment = 0
            total_link = len([feature for feature in features])
            pg_increment = 100/total_link
            print(f"Result LINK {result[0][0]}, total {total_link}, increment {pg_increment}")
            parent.pg_loading.setValue(pg_increment)
            if result[0][0] != 0:
                parent.lbl_loading.setText("Varifing Network")
                parent.pg_loading.setValue(pg_increment)
                print("Dentro del IF")
                for feature in layer.getFeatures():
                    linkId = feature.attribute('LinkId')
                    Or_node = feature.attribute('Or_node')
                    Des_node = feature.attribute('Des_node')

                    result = self.dataBaseSqlite.selectAll(' link ', " where linkid = '{}'".format(linkId))
                    if len(result) == 0:
                        self.dataBaseSqlite.addLink(scenarios_arr, linkId, Or_node, Des_node)
                    pg_increment+=pg_increment
                    if (int(pg_increment) % 5) == 0:
                        parent.pg_loading.setValue(pg_increment)
            else:
                parent.lbl_loading.setText("Loading Network")
                
                for feature in layer.getFeatures():
                    linkId = feature.attribute('LinkId')
                    Or_node = feature.attribute('Or_node')
                    Des_node = feature.attribute('Des_node')
                    
                    self.dataBaseSqlite.addLink(scenarios_arr, linkId, Or_node, Des_node)
                    pg_increment+=pg_increment

                    if (int(pg_increment) % 5) == 0:
                        parent.pg_loading.setValue(pg_increment)

            parent.pg_loading.setVisible(False)
            parent.lbl_loading.setVisible(False)

            return True


    def __load_nodes_data(self):
        shape = self.network_nodes_shape.text()
        layer = QgsVectorLayer(shape, 'Network_Nodes', 'ogr')
        if not layer.isValid():
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Data", "Shape Layers is Invalid.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            return False
        else:
            network_shape_fields = [field.name() for field in layer.fields()]
            features = layer.getFeatures()
            #print(features)
            
            for feature in features:
                _id = feature.attribute('Id')
                id_type = feature.attribute('Zone') if feature.attribute('Zone') else None
                name = feature.attribute('name') if feature.attribute('name') else None
                description = feature.attribute('descriptio') if feature.attribute('descriptio') else None
                x = feature.attribute('X') if feature.attribute('X') else None
                y = feature.attribute('Y') if feature.attribute('Y') else None
                result = self.dataBaseSqlite.selectAll(' node ', " where id = {}".format(_id))
                if len(result) == 0:
                    self.dataBaseSqlite.addNode(_id, id_type, name, description, x, y)

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
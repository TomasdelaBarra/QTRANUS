# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QTranus
                                 A QGIS plugin
 qtranus
                              -------------------
        begin                : 2015-07-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by qtranus
        Collaborators        : Tomas de la Barra    - delabarra@gmail.com
                               Omar Valladolid      - omar.valladolidg@gmail.com
                               Pedro Buron          - pedroburonv@gmail.com
                               Luis Yanez           - yanezblancoluis@gmail.com
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
import os, sys, os.path, re, json, datetime
from PyQt5.QtGui import  QIcon
from PyQt5 import QtWidgets
from PyQt5 import QtGui, uic, QtCore
from PyQt5.QtCore import QSettings, QVariant, QTranslator, qVersion, QCoreApplication, QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QAction, QLineEdit, QDockWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QMenu

from qgis.core import QgsProject, QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsSymbol, QgsLineSymbol, QgsSymbolLayer, QgsSimpleLineSymbolLayer, QgsMarkerLineSymbolLayer, QgsArrowSymbolLayer, QgsSimpleLineSymbolLayer, QgsMarkerLineSymbolLayer

# Initialize Qt resources from file resources.py
from . import resources_rc 
# Import the code for the dialog

import qgis
from qgis import *
from qgis.core import  QgsMessageLog, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo, QgsLineSymbolLayer, QgsSimpleLineSymbolLayer, QgsMapUnitScale, QgsSimpleLineSymbolLayer, QgsLineSymbol, QgsMarkerLineSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsWkbTypes, QgsPoint, QgsFeatureRequest, QgsSymbolLayer, QgsProperty
from qgis.gui import QgsQueryBuilder

from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.libraries.tabulate import tabulate
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .qtranus_project import QTranusProject
from .qtranus_dialog import QTranusDialog
from .scenarios_model_sqlite import ScenariosModelSqlite
from .add_route_dialog import AddRouteDialog
from .add_linktype_dialog import AddLinkTypeDialog
from .reasign_linktype import ReasignLintype
from .classes.Paths import Paths


class QTranus:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """ Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize elements of scenarios selector widget 
        self.main_window = self.iface.mainWindow()
        self.canvas = None

        # Load layput dock Scenarios
        # Routes tab
        self.scenarios_dockwidget = uic.loadUi(os.path.join(os.path.dirname(__file__), 'scenarios_selector.ui'))
        self.scenarios_tree = self.scenarios_dockwidget.findChild(QtWidgets.QTreeView, 'scenarios')            
        self.scenarios_tree.clicked.connect(self.update_layers)
        self.btn_add_route = self.scenarios_dockwidget.findChild(QtWidgets.QPushButton, 'btn_add_route')
        self.routes_tree = self.scenarios_dockwidget.findChild(QtWidgets.QTreeView, 'routes_tree')                 
        self.routes_tree.setRootIsDecorated(False)
        self.routes_tree.clicked.connect(self.update_routes)
        self.routes_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.routes_tree.customContextMenuRequested.connect(self.open_menu_routes)
        self.routes_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        
        # Link types tab
        self.btn_add_linktype = self.scenarios_dockwidget.findChild(QtWidgets.QPushButton, 'btn_add_linktype')
        self.linktypes_tree = self.scenarios_dockwidget.findChild(QtWidgets.QTreeView, 'linktypes_tree')            
        self.linktypes_tree.setRootIsDecorated(False)
        self.linktypes_tree.clicked.connect(self.update_linktypes)
        self.linktypes_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.linktypes_tree.customContextMenuRequested.connect(self.open_menu_linktypes)
        self.linktypes_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.linktypes_tree.header().setStretchLastSection(True)
        self.btn_add_route.clicked.connect(self.open_add_route_window)
        self.btn_add_route.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        self.btn_add_linktype.clicked.connect(self.open_add_linktype_window)
        self.btn_add_linktype.setIcon(QIcon(self.plugin_dir+"/icons/add-scenario.svg"))
        
        # Results - Path tab
        self.tab_widget_main = self.scenarios_dockwidget.findChild(QtWidgets.QTabWidget , 'tabWidget') 
        self.cb_origin = self.scenarios_dockwidget.findChild(QtWidgets.QComboBox, 'cb_origin')
        self.cb_destination = self.scenarios_dockwidget.findChild(QtWidgets.QComboBox, 'cb_destination')
        self.cb_mode = self.scenarios_dockwidget.findChild(QtWidgets.QComboBox, 'cb_mode')
        self.cb_path = self.scenarios_dockwidget.findChild(QtWidgets.QComboBox, 'cb_path')
        self.pathlink_tree = self.scenarios_dockwidget.findChild(QtWidgets.QTreeView, 'paths_links_tree')            
        self.tbl_desutilities = self.scenarios_dockwidget.findChild(QtWidgets.QTableWidget, 'tbl_desutilities')            
        self.lbl_scenario_code = self.scenarios_dockwidget.findChild(QtWidgets.QLabel, 'lbl_scenario_code')            
        self.lbl_total_paths = self.scenarios_dockwidget.findChild(QtWidgets.QLabel, 'lbl_total_paths')                
        self.pathlink_tree.setRootIsDecorated(False)
        self.pathlink_tree.header().setStretchLastSection(True)
        self.tab_widget_main.setTabEnabled(3, False);

        self.cb_origin.currentIndexChanged.connect(self.load_paths_combobox)
        self.cb_destination.currentIndexChanged.connect(self.load_paths_combobox)
        self.cb_mode.currentIndexChanged.connect(self.load_paths_combobox)
        self.cb_path.currentIndexChanged.connect(self.path_fields_changed)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QTranus_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.project = QTranusProject(QgsProject.instance(), iface)
        # Create the dialog (after translation) and keep reference
        self.dlg = QTranusDialog(self, project=self.project)
    
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&qtranus')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'QTranus')
        self.toolbar.setObjectName(u'QTranus')

        # TODO: delete when the load scenario process is finished
        # self.addScenariosSection()

        
    def open_add_route_window(self):
        """
            @summary: Opens add scenario window
        """
        index_scenario = self.scenarios_tree.selectedIndexes()
        scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        id_scenario = self.dataBaseSqlite.selectAll( 'scenario', where=f" where code = '{scenario_cod_selected}'")

        dialog = AddRouteDialog(self.project_file,  idScenario=id_scenario[0][0])
        dialog.show()
        result = dialog.exec_()
        self.load_routes()


    def open_add_linktype_window(self):
        """
            @summary: Opens add scenario window
        """
        index_scenario = self.scenarios_tree.selectedIndexes()
        scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        id_scenario = self.dataBaseSqlite.selectAll( 'scenario', where=f" where code = '{scenario_cod_selected}'")

        dialog = AddRouteDialog(self.project_file,  idScenario=id_scenario[0][0])
        dialog.show()
        result = dialog.exec_()
        self.load_routes()


    def open_edit_route_window(self, id_route_selected=None):
        """
            @summary: Opens add scenario window
        """
        index_scenario = self.scenarios_tree.selectedIndexes()
        scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        id_scenario = self.dataBaseSqlite.selectAll( 'scenario', where=f" where code = '{scenario_cod_selected}'")

        dialog = AddRouteDialog(self.project_file,  idScenario=id_scenario[0][0], codeRoute=id_route_selected)
        dialog.show()
        result = dialog.exec_()
        self.load_routes()


    def open_edit_linktypes_window(self, id_lintype_selected=None):
        """
            @summary: Open linktypes 
        """
        index_scenario = self.scenarios_tree.selectedIndexes()
        scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        id_scenario = self.dataBaseSqlite.selectAll( 'scenario', where=f" where code = '{scenario_cod_selected}'")

        dialog = AddLinkTypeDialog(self.project_file,  idScenario=id_scenario[0][0], linkTypeSelected=id_lintype_selected)
        dialog.show()
        result = dialog.exec_()
        self.load_linktypes()


    def open_menu_routes(self, position):
        menu = QMenu()
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)

        indexes = self.routes_tree.selectedIndexes()
        if indexes:
            id_route_selected = indexes[1].model().itemFromIndex(indexes[1]).text()

            # Get last id route selected 
            if len(indexes) > 3:
                id_route_selected = indexes[len(indexes)-2].model().itemFromIndex(indexes[len(indexes)-2]).text()
            print("ID selected  " ,id_route_selected)
            index_scenario = self.scenarios_tree.selectedIndexes()
            scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
            
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_cod_selected)
            
            assign = menu.addAction(QIcon(self.plugin_dir+"/icons/action_capture_line.svg"),'Assign Link')
            remove_assign = menu.addAction(QIcon(self.plugin_dir+"/icons/action_remove_line.svg"),'Remove Link')
            edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Route')
            remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Delete Route')

            opt = menu.exec_(self.routes_tree.viewport().mapToGlobal(position))
            
            if opt == remove:
                self.delete_route(scenarios, id_route_selected)
            if opt == edit:
                self.open_edit_route_window(id_route_selected)
            if opt == assign:
                self.assing_remove_route_link(id_route_selected, scenarios, action='assign')
            if opt == remove_assign:
                self.assing_remove_route_link(id_route_selected, scenarios, action='remove')
    

    def open_menu_linktypes(self, position):
        menu = QMenu()
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)

        indexes = self.linktypes_tree.selectedIndexes()
        if indexes:
            id_linktype_selected = indexes[1].model().itemFromIndex(indexes[1]).text()

            # Get last id route selected 
            if len(indexes) > 3:
                id_linktype_selected = indexes[len(indexes)-2].model().itemFromIndex(indexes[len(indexes)-2]).text()
            
            index_scenario = self.scenarios_tree.selectedIndexes()
            scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
            
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_cod_selected)
            
            assign = menu.addAction(QIcon(self.plugin_dir+"/icons/action_capture_line.svg"),'Assign Link type')
            remove_assign = menu.addAction(QIcon(self.plugin_dir+"/icons/action_remove_line.svg"),'Re asign Link type')
            edit = menu.addAction(QIcon(self.plugin_dir+"/icons/edit-layer.svg"),'Edit Link type')
            remove = menu.addAction(QIcon(self.plugin_dir+"/icons/remove-scenario.svg"),'Delete Link type')

            opt = menu.exec_(self.routes_tree.viewport().mapToGlobal(position))
            
            if opt == remove:
                self.delete_linktype(scenarios, id_linktype_selected)
            if opt == edit:
                self.open_edit_linktypes_window(id_linktype_selected)
            if opt == assign:
                self.assing_remove_linktype_link(id_linktype_selected, scenarios, action='assign')
            if opt == remove_assign:
                self.assing_remove_linktype_link(id_linktype_selected, scenarios, action='remove')
        
    
    def delete_route(self, scenarios, id_route_selected):
        scenarios_str = [str(value[0]) for value in scenarios]
        scenarios_str = ','.join(scenarios_str)
        validation, routes = self.dataBaseSqlite.validateRemoveRoutes(id_route_selected, scenarios_str)
        
        messagebox = QTranusMessageBox.set_new_message_box_confirm(QtWidgets.QMessageBox.Warning, "Routes", "Are you sure?", ":/plugins/QTranus/icon.png")
        messagebox.exec_()
        if messagebox.clickedButton() == messagebox.button(QtWidgets.QMessageBox.Yes):
            if validation == False:
                routes = tabulate(routes, headers=["Scenario Code", "Link Id"])  if routes else ''
                messagebox = QTranusMessageBox.set_new_message_box_base(QtWidgets.QMessageBox.Warning, "Routes", "Can't remove elements \n Please check details.", ":/plugins/QTranus/icon.png", buttons = QtWidgets.QMessageBox.Ok, detailedText=f"Dependents Elements \n {routes}")
                messagebox.exec_()
            else:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.dataBaseSqlite.removeRoute(scenarios, id_route_selected)
                self.load_routes()
                QApplication.restoreOverrideCursor()

    
    def delete_linktype(self, scenarios, id_linktype_selected):
        scenarios_str = [str(value[0]) for value in scenarios]
        scenarios_str = ','.join(scenarios_str)
        validation, linktypes = self.dataBaseSqlite.validateRemoveLinkType(id_linktype_selected, scenarios_str)
        
        messagebox = QTranusMessageBox.set_new_message_box_confirm(QtWidgets.QMessageBox.Warning, "Link Type", "Are you sure?", ":/plugins/QTranus/icon.png")
        messagebox.exec_()
        if messagebox.clickedButton() == messagebox.button(QtWidgets.QMessageBox.Yes):
            if validation == False:
                linktypes = tabulate(linktypes, headers=["Scenario Code", "Link Id"])  if linktypes else ''
                messagebox = QTranusMessageBox.set_new_message_box_base(QtWidgets.QMessageBox.Warning, "Link Type", "Can't remove elements \n Please check details.", ":/plugins/QTranus/icon.png", buttons = QtWidgets.QMessageBox.Ok, detailedText=f"Dependents Elements \n {linktypes}")
                messagebox.exec_()
            else:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.dataBaseSqlite.removeLinkType(scenarios, id_linktype_selected)
                self.load_linktypes()
                QApplication.restoreOverrideCursor()
                

    def assing_remove_route_link(self, id_route_selected, scenarios, action='assign'):
        """ Capture features of the network layer to assign routes 
        """
        # Messaga info for selection fearutes on Network Layer
        self.iface.messageBar().pushMessage("Info", f"Plase use Ctrl + Click to {action} a route to links", level=0)

        # Enabling selection features mode on QGIS UI 
        self.iface.actionSelect().trigger()

        # Active network layer
        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())
        
        layer = registry.mapLayersByName('Network_routes')[0]
        registry.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        self.iface.setActiveLayer(layer)
        
        self.canvas = self.iface.mapCanvas()
        if self.canvas.receivers(self.canvas.keyReleased) > 0:
            self.canvas.keyReleased.disconnect()

        if action == 'assign':
            self.canvas.keyReleased.connect(lambda key_released, layer=layer, scenarios=scenarios, id_route_selected=id_route_selected: self.key_ctlr_released_assign(key_released, layer, scenarios, id_route_selected))

        if action == 'remove':
            self.canvas.keyReleased.connect(lambda key_released, layer=layer, scenarios=scenarios, id_route_selected=id_route_selected: self.key_ctlr_released_remove(key_released, layer, scenarios, id_route_selected))
    

    def assing_remove_linktype_link(self, id_linktype_selected, scenarios, action='assign'):
        """ Capture features of the network layer to assign routes 
        """
        # Messaga info for selection fearutes on Network Layer
        self.iface.messageBar().pushMessage("Info", f"Plase use Ctrl + Click to {action} a route to links", level=0)

        # Enabling selection features mode on QGIS UI 
        self.iface.actionSelect().trigger()

        # Active network layer
        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())
        
        layer = registry.mapLayersByName('Network_Linktypes')[0]
        registry.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        self.iface.setActiveLayer(layer)
        
        self.canvas = self.iface.mapCanvas()
        if self.canvas.receivers(self.canvas.keyReleased) > 0:
            self.canvas.keyReleased.disconnect()

        if action == 'assign':
            self.canvas.keyReleased.connect(lambda key_released, layer=layer, scenarios=scenarios, id_linktype_selected=id_linktype_selected: self.key_ctlr_released_assign_lynktype(key_released, layer, scenarios, id_linktype_selected))

        if action == 'remove':
            self.canvas.keyReleased.connect(lambda key_released, layer=layer, scenarios=scenarios, id_linktype_selected=id_linktype_selected: self.key_ctlr_released_remove_lynktype(key_released, layer, scenarios, id_linktype_selected))
    

    def key_ctlr_released_assign(self, key_released, layer, scenarios, id_route_selected):
        """ Action trigger to save links
        """
        try:
            project = QgsProject.instance()
            # Change UI Cursor loading...
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
            self.dataBaseSqlite = DataBaseSqlite(self.project_file)

            links_routes = []
            if key_released.key() == Qt.Key_Control:
                # List of features selected
                features_ids = [ feature.id() for feature in layer.selectedFeatures() ]
                # Save database routes added
                attributes_link_id = [value.attribute('link_id') for value in layer.selectedFeatures()]
                for link_id in attributes_link_id:
                    links_routes.append((link_id, id_route_selected, 2))

                self.dataBaseSqlite.add_route_link(scenarios, links_routes)

                self.update_routes()
                
                QApplication.restoreOverrideCursor()
                self.iface.messageBar().pushMessage("Success", f"Route #{id_route_selected} has been added successful", level=3)
        except Exception as e:
            print("Error: ", e)
            QApplication.restoreOverrideCursor()
        

    def key_ctlr_released_assign_lynktype(self, key_released, layer, scenarios, id_lynktype_selected):
        """ Action trigger to save linkstypes  """
        try:
            project = QgsProject.instance()
            # Change UI Cursor loading...
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
            self.dataBaseSqlite = DataBaseSqlite(self.project_file)
            links_linktypes = []
            if key_released.key() == Qt.Key_Control:
                # List of features selected
                if isinstance(layer, QgsVectorLayer):
                    features_ids = [ feature.id() for feature in layer.selectedFeatures() ]
                    # Save database routes added
                    attributes_link_id = [value.attribute('link_id') for value in layer.selectedFeatures()]
                    for link_id in attributes_link_id:
                        links_linktypes.append((link_id, id_lynktype_selected))

                    self.dataBaseSqlite.add_linktype_link(scenarios, links_linktypes)

                    self.update_linktypes()
                    
                    QApplication.restoreOverrideCursor()
                    self.iface.messageBar().pushMessage("Success", f"Link Type #{id_lynktype_selected} has been added successful", level=3)
        except Exception as e:
            print(e)                
            QApplication.restoreOverrideCursor()


    def key_ctlr_released_remove(self, key_released, layer, scenarios, id_route_selected):
        """ Action trigger to save links
        """
        
        try:
            project = QgsProject.instance()

            # Change UI Cursor loading...
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
            self.dataBaseSqlite = DataBaseSqlite(self.project_file)

            links_routes = []

            if key_released.key() == Qt.Key_Control:
                # List of features selected
                features_ids = [ feature.id() for feature in layer.selectedFeatures() ]
                # Save database routes added
                attributes_link_id = [value.attribute("link_id") for value in layer.selectedFeatures()]                
                for link_id in attributes_link_id:
                    links_routes.append((link_id, id_route_selected, 1))
                self.dataBaseSqlite.remove_route_link(scenarios, links_routes)

                QApplication.restoreOverrideCursor()
                # Messagebar success
                self.update_routes()
                self.iface.messageBar().pushMessage("Success", f"Route #{id_route_selected} has been removed successful", level=3)
        except:
            QApplication.restoreOverrideCursor()


    def key_ctlr_released_remove_lynktype(self, key_released, layer, scenarios, id_linktype_selected):
        """ Action trigger to save links
        """
        index_scenario = self.scenarios_tree.selectedIndexes()
        scenario_cod_selected = index_scenario[0].model().itemFromIndex(index_scenario[0]).text()[:3]
        id_scenario = self.dataBaseSqlite.selectAll( 'scenario', where=f" where code = '{scenario_cod_selected}'")

        dialog = ReasignLintype(self.project_file, id_scenario[0][0])
        dialog.show()
        result = dialog.exec_()

        id_lynktype_selected = dialog.cb_linktype.currentText().split()[0]
        if dialog.response_buttons:
            self.key_ctlr_released_assign_lynktype(key_released, layer, scenarios, id_lynktype_selected)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """ Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QTranus', message)


    def update_layers(self, selectedIndex):
        """
            @summary: Update Layers after scenario selection
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]

        self.load_path_base_info()
        
        # "LinkId"  in ('1-101', '101-1')
        layerIds = [layer.id() for layer in QgsProject.instance().mapLayers().values()]
        networkLayerId = [ value for value in layerIds if re.match('Network_Links',value)]

        if networkLayerId and self.project_file:
            # Selecciono un layer
            dataBaseSqlite = DataBaseSqlite(self.project_file)

            qry = f"""select a.linkid 
                from link a
                join scenario b on a.id_scenario = b.id
                where b.code = '{self.scenarioCode}'"""

            result = dataBaseSqlite.executeSql(qry)
            
            linksIds = ",".join([f"'{value[0]}'" for value in result])

            layer = QgsProject.instance().mapLayer(networkLayerId[0])
            qry = QgsQueryBuilder(layer)
            qry.setSql( f"\"{self.project['links_shape_field_id']}\" IN ({linksIds}) ")
            qry.accept()

    
    def update_routes(self):
        # UI cursor loading 
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            # Routes tree index
            id_routes_selected = []
            indexes = self.routes_tree.selectedIndexes()
            
            for i, index in enumerate(indexes):
                if index.column() == 1:
                    id_routes_selected.append(index.model().itemFromIndex(index).text())

            # Scenario tree index
            scenario_selected_index = self.scenarios_tree.selectedIndexes()
            scenario_code = scenario_selected_index[0].model().itemFromIndex(scenario_selected_index[0]).text().split(" - ")[0]

            registry = QgsProject.instance()
            layersCount = len(registry.mapLayers())
            layer_network = registry.mapLayersByName('Network_Links')[0]
            epsg = layer_network.crs().postgisSrid()
            
            root = registry.layerTreeRoot()
            layer_group = root.findGroup("QTRANUS")
            layers_name = [lyr.name() for lyr in registry.mapLayers().values()]

            id_routes = ", ".join(id_routes_selected)

            sql =  f"""select 
                    a.id_link, a.id_route, c.color
                    from link_route a
                    join scenario b on (a.id_scenario = b.id)
                    join route c on (a.id_route = c.id and c.id_scenario = a.id_scenario)
                    where b.code = '{scenario_code}'
                    and id_route in  ({id_routes})"""

            data_links_routes = self.dataBaseSqlite.executeSql(sql)
            links_routes ="','".join( [ link[0] for link in data_links_routes ] ) 
            
            memory_route_lyr = QgsVectorLayer(f"LineString?crs=epsg:{epsg}", "Network_routes", "memory")

            memory_data = memory_route_lyr.dataProvider()
            memory_data.addAttributes([QgsField("route_id",  QVariant.Int), QgsField("link_id",  QVariant.String)])

            # Get features of the base layer
            qry = f"""select a.linkid 
                from link a
                join scenario b on a.id_scenario = b.id
                where b.code = '{scenario_code}'"""

            result = self.dataBaseSqlite.executeSql(qry)
            links_ids = ",".join([f"'{value[0]}'" for value in result])
            features_network = [feat for feat in layer_network.getFeatures(QgsFeatureRequest().setFilterExpression( f"\"{self.project['links_shape_field_id']}\" IN ({links_ids}) "))]

            feat_arr = []
            
            links_x_route = []
            for route in id_routes_selected:
                sql =  f"""select 
                    a.id_link, a.id_route, c.color
                    from link_route a
                    join scenario b on (a.id_scenario = b.id)
                    join route c on (a.id_route = c.id and c.id_scenario = a.id_scenario)
                    where b.code = '{scenario_code}'
                    and id_route = {int(route)}"""
                    
                link_list = self.dataBaseSqlite.executeSql(sql)
                link_list = [ f"'{value[0]}'"  for value in link_list]
                links_x_route.append(( int(route) , link_list))

            # Group routes
            sql_test = f"""select 
                a.id_link, a.id_route
                from link_route a
                join scenario b on (a.id_scenario = b.id)
                join route c on (a.id_route = c.id and c.id_scenario = a.id_scenario)
                where b.code = '{scenario_code}'
                and id_route in ({",".join(id_routes_selected)}) order by 1"""
            
            routes_x_link_arr = self.dataBaseSqlite.executeSql(sql_test)
            
            # Dictionary to buil offset expression
            routes_links_new = {}
            for linkid_new, routes_new in routes_x_link_arr:
                if linkid_new not in routes_links_new.keys():
                    routes_links_new[linkid_new] = [routes_new]
                else:
                    routes_links_new[linkid_new].append(routes_new)

            expression_str = " CASE "
            for link_id, routes_ids in routes_links_new.items():
                offset = 0
                for route_id in routes_ids:
                    expression_str += f"""WHEN "route_id" = {route_id} and "link_id"='{link_id}' THEN {offset} """
                    offset += 0.8
            expression_str += "ELSE 0 \n END"

            result_arr = [] 
            for route_data in links_x_route:
                link_ids = ", ".join(route_data[1])
                features_routes = layer_network.getFeatures(QgsFeatureRequest().setFilterExpression( f""""{self.project['links_shape_field_id']}" in ({link_ids}) """))
                for feature in features_routes:
                    geom = feature.geometry()
                    linkid = feature.attribute(f"{self.project['links_shape_field_id']}")
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    feat.setAttributes([route_data[0], linkid])
                    feat_arr.append(feat)
            
            # Get base network geometries
            for feature in features_network:
                geom = feature.geometry()
                attributte = feature.attribute(f"{self.project['links_shape_field_id']}")
                feat = QgsFeature()
                feat.setGeometry(geom)
                feat.setAttributes(['', attributte])
                feat_arr.append(feat)
                
            memory_route_lyr.startEditing()
            memory_route_lyr.dataProvider().addFeatures(feat_arr)
            memory_route_lyr.commitChanges()
            # Get unique route_id and color_id of data_links_routes
            temp_colors, temp_ids = set(), set()
            routes_colors, routes_ids = [], []
            for link_route in data_links_routes: 
                if not link_route[1] in temp_ids: 
                    temp_ids.add(link_route[1]) 
                    routes_ids.append(link_route[1])
                if not link_route[2] in temp_colors: 
                    temp_colors.add(link_route[2]) 
                    routes_colors.append(link_route[2])

            categories = []
            offset = 0
            # Routes symbols
            for index, link_route in enumerate(routes_ids):
                symbol_layer = QgsSimpleLineSymbolLayer(QColor(routes_colors[index]))

                symbol_layer.setDataDefinedProperty(QgsSymbolLayer.PropertyOffset, QgsProperty.fromExpression(expression_str))
                ## print(symbol_layer.dxfOffset())
                ## line.setOffsetUnit(2)
                symbol_layer.setOffset(offset)
                offset += 0.8 
                ##line.setWidthUnit(2)
                symbol_layer.setWidth(0.6)
                symbol = QgsLineSymbol()
                symbol.changeSymbolLayer(0,symbol_layer)

                """
                symbol = QgsLineSymbol()
                symbol.setColor(QColor(routes_colors[index]))
                symbol.setWidth(0.6)
                """
                categorie = QgsRendererCategory(routes_ids[index], symbol, f"""Route {routes_ids[index]}""")
                categories.append(categorie)

            # Base Network
            # 4291677645 Gray color
            symbol = QgsLineSymbol()
            symbol.setColor(QColor(4291677645))
            symbol.setWidth(0.2)
            cat = QgsRendererCategory('', symbol, f"""Base Network""")
            categories.append(cat)
            
            categorized_renderer = QgsCategorizedSymbolRenderer('route_id', categories)
            
            memory_route_lyr.setRenderer(categorized_renderer)
            msg = 'created'
            if 'Network_routes' in layers_name:
                layer_route = registry.mapLayersByName('Network_routes')
                layer_group.removeLayer(layer_route[0])
                registry.removeMapLayer(layer_route[0].id())
                msg = 'updated'

            registry.addMapLayer(memory_route_lyr, False)
            layer_group.insertLayer(0, memory_route_lyr)

            self.iface.messageBar().pushMessage("Info", f"QTRANUS Layer 'Network_routes' has been {msg}. Route #{id_routes}", level=0)

            # Remove UI Cursor loading...
            QApplication.restoreOverrideCursor()
        except Exception as e:
            # Remove UI Cursor loading...
            print("Error:", e)
            QApplication.restoreOverrideCursor()

    

    def update_linktypes(self):

        # UI cursor loading 
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            # Scenario tree index
            scenario_selected_index = self.scenarios_tree.selectedIndexes()
            scenario_code = scenario_selected_index[0].model().itemFromIndex(scenario_selected_index[0]).text().split(" - ")[0]

            # Get EPSG from layer network
            registry = QgsProject.instance()
            layersCount = len(registry.mapLayers())
            layer_network = registry.mapLayersByName('Network_Links')[0]
            epsg = layer_network.crs().postgisSrid()
            
            root = registry.layerTreeRoot()
            layer_group = root.findGroup("QTRANUS")
            layers_name = [lyr.name() for lyr in registry.mapLayers().values()]
            
            id_linktypes_selected = []
            indexes = self.linktypes_tree.selectedIndexes()
            for i, index in enumerate(indexes):
                if index.column() == 1 and index.model().item(index.row(), 0).data(Qt.DecorationRole):
                    id_linktypes_selected.append(index.model().itemFromIndex(index).text())

            #if len(id_linktypes_selected) > 0:
            id_linktypes = ", ".join(id_linktypes_selected)

            sql =  f"""select distinct id_linktype, linkid, c.symbology
                from link a
                join scenario b on (a.id_scenario = b.id)
                join link_type c on (a.id_linktype = c.id)
                where b.code = '{scenario_code}'
                and a.id_linktype in ({id_linktypes})
                order by 1
                """
            data_links_linktypes = self.dataBaseSqlite.executeSql(sql)
            links_routes ="','".join( [ link[1] for link in data_links_linktypes ] ) 
            links_routes = f"'{links_routes}'"

            memory_route_lyr = QgsVectorLayer(f"LineString?crs=epsg:{epsg}", "Network_Linktypes", "memory")
            memory_data = memory_route_lyr.dataProvider()
            memory_data.addAttributes([QgsField("linktype_id",  QVariant.Int), QgsField("link_id",  QVariant.String)])

            # Get features of the base layer
            qry = f"""select a.linkid 
                from link a
                join scenario b on a.id_scenario = b.id
                where b.code = '{scenario_code}'"""

            result = self.dataBaseSqlite.executeSql(qry)
            links_ids = ",".join([f"'{value[0]}'" for value in result])
            features_network = [feat for feat in layer_network.getFeatures(QgsFeatureRequest().setFilterExpression( f"\"LinkId\" IN ({links_ids}) "))]

            feat_arr = []
            # Attributes 
            for value in data_links_linktypes:
                # Get Feature from layer network
                features_routes = layer_network.getFeatures(QgsFeatureRequest().setFilterExpression( f""""LinkID" = '{value[1]}' """))
                for feature in features_routes:
                    geom = feature.geometry()
                    attributtes = feature.attributes()
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    feat.setAttributes([value[0], value[1]])
                    feat_arr.append(feat)
            
            # Base network
            for feature in features_network:
                geom = feature.geometry()
                attributte = feature.attribute(f"{self.project['links_shape_field_id']}")
                feat = QgsFeature()
                feat.setGeometry(geom)
                feat.setAttributes(['', attributte])
                feat_arr.append(feat)
                
            memory_route_lyr.startEditing()
            memory_route_lyr.dataProvider().addFeatures(feat_arr)
            memory_route_lyr.commitChanges()

            # Get unique id_linktypes and color_id of data_links_linktypes
            linktypes_objs = set()
            for values in data_links_linktypes:
                linktypes_objs.add((values[0], values[2]))
            linktypes_objs = list(linktypes_objs)
            linktypes_objs.sort()

            categories = []
            # Routes symbols
            for values in linktypes_objs:
                symbol = self.get_symbol_object(values[1])
                cat = QgsRendererCategory(values[0], symbol, f"Link type {values[0]}")
                categories.append(cat)

            # Base Network
            # 4291677645 Gray color
            symbol = QgsLineSymbol()
            symbol.setColor(QColor(4291677645))
            symbol.setWidth(0.2)
            cat = QgsRendererCategory('', symbol, f"""Base Network""")
            categories.append(cat)
            
            categorized_renderer = QgsCategorizedSymbolRenderer('linktype_id', categories)
            
            memory_route_lyr.setRenderer(categorized_renderer)
            msg = 'created'
            if 'Network_Linktypes' in layers_name:
                layer_route = registry.mapLayersByName('Network_Linktypes')
                layer_group.removeLayer(layer_route[0])
                registry.removeMapLayer(layer_route[0].id())
                msg = 'updated'

            registry.addMapLayer(memory_route_lyr, False)
            layer_group.insertLayer(0, memory_route_lyr)
            
            if len(id_linktypes) > 0:
                self.iface.messageBar().pushMessage("Info", f"QTRANUS Layer 'Network_Linktypes' has been {msg}. Link type #{id_linktypes}", level=0)

            # Remove UI Cursor loading...
            QApplication.restoreOverrideCursor()
        
        except Exception as e:
            # Remove UI Cursor loading...
            print("Error:", e)
            QApplication.restoreOverrideCursor()


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/QTranus/icon.png'
    
        self.add_action(
            icon_path,
            text=self.tr(u'qtranus'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        self.addScenariosSection()


    def addScenariosSection(self):
        """
        Add Dockwidget to MainWindow
        """
        result = self.main_window.findChild(QtWidgets.QWidget,"dockWidgetContents")
        if not result.isVisible():
            self.main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.scenarios_dockwidget)
            self.scenarios_dockwidget.show()
        self.load_scenarios()
        self.load_routes()
        self.load_linktypes()
        # self.load_paths_file()
        self.load_path_base_info()


    def path_fields_changed(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.load_paths_file()
        QApplication.restoreOverrideCursor()


    def load_path_base_info(self):
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        zones_result = self.dataBaseSqlite.selectAll(' zone ', where=" where id != 0", orderby=" order by 1 asc")
        mode_result = self.dataBaseSqlite.selectAll(' mode ')

        scenario_selected_index = self.scenarios_tree.selectedIndexes()
        scenario_code = scenario_selected_index[0].model().itemFromIndex(scenario_selected_index[0]).text().split(" - ")[0]
        self.validate_scenario_pathsfile(scenario_code)
        self.lbl_scenario_code.setText(scenario_code)
        if zones_result and len(zones_result):
            for value in zones_result:
                self.cb_origin.addItem(f"{value[0]} {value[1]}", value[0])
                self.cb_destination.addItem(f"{value[0]} {value[1]}", value[0])
        # load mode result combo
        if mode_result and len(mode_result):
            for value in mode_result:
                self.cb_mode.addItem(f"{value[0]} {value[1]}", value[0])

    def load_paths_combobox(self, index):
        if index:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            path_count = []
            # load zones result combo
            id_origin = self.cb_origin.currentText().split(" ")[0]
            id_destination = self.cb_destination.currentText().split(" ")[0]
            scenario_selected_index = self.scenarios_tree.selectedIndexes()
            scenario_code = scenario_selected_index[0].model().itemFromIndex(scenario_selected_index[0]).text().split(" - ")[0]

            paths_data = Paths(self.project['tranus_folder'], scenario_code)
            result_file = paths_data.load_paths()

            if result_file and len(result_file) > 0:
                path_data_structure = paths_data.find_paths(id_origin, id_destination, scenario_code)
                if len(path_data_structure) > 0:
                    # load paths
                    for value in path_data_structure:
                        path_count.append(value[0]['path'])
                    self.cb_path.clear()
                    self.cb_path.addItems(path_count)

                    self.lbl_scenario_code.setText(scenario_code)
                    self.lbl_total_paths.setText(str(len(path_count)))
                else:
                    self.cb_path.clear()
                    self.tbl_desutilities.clearContents()
                    self.tbl_desutilities.model().removeRows(0, self.tbl_desutilities.rowCount())
                    self.pathlink_tree.model().removeRows(0, self.pathlink_tree.model().rowCount())
                    self.lbl_total_paths.setText("0")
            else:
                self.cb_path.clear()
                self.lbl_scenario_code.setText("-")
                self.lbl_total_paths.setText("0")

            QApplication.restoreOverrideCursor()

    def load_paths_file(self):
            
        path_count = []
        # load zones result combo
        id_origin = self.cb_origin.currentText().split(" ")[0]
        id_destination = self.cb_destination.currentText().split(" ")[0]
        id_mode = self.cb_mode.currentText().split(" ")[0]
        id_path = self.cb_path.currentText().split(" ")[0]
        scenario_selected_index = self.scenarios_tree.selectedIndexes()
        scenario_code = scenario_selected_index[0].model().itemFromIndex(scenario_selected_index[0]).text().split(" - ")[0]

        paths_data = Paths(self.project['tranus_folder'], scenario_code)
        result_file = paths_data.load_paths()

        if result_file:
            path_data_structure = paths_data.find_paths(id_origin, id_destination, scenario_code)
            self.load_pathlinktree(path_data_structure)
            self.load_desutilitiestable(path_data_structure)
            # Show paths
            self.show_path_layer(result_file, id_origin, id_destination, id_mode, id_path)
        
    
    def load_pathlinktree(self, paths):
        try:   
            id_origin = self.cb_origin.currentText().split(" ")[0]
            id_destination = self.cb_destination.currentText().split(" ")[0]
            id_mode = self.cb_mode.currentText().split(" ")[0]
            id_path = self.cb_path.currentText()
        
            paths_links_list = self.search_path_links(paths, id_origin, id_destination, id_mode, id_path)
            paths_links_list.pop()
            model = QtGui.QStandardItemModel()
            model.setHorizontalHeaderLabels(['Route/Operator','To Node'])
            if paths_links_list:
                for x in range(0, len(paths_links_list)):
                    model.insertRow(x)
                    z=0
                    for y in range(0,2):
                        model.setData(model.index(x, y), paths_links_list[x][z])
                        z+=1
                self.pathlink_tree.setModel(model)
                self.pathlink_tree.setColumnWidth(0, 100)
                self.pathlink_tree.setColumnWidth(1, QtWidgets.QHeaderView.ResizeToContents)
        
        except Exception as e:
            print("Error: paths_links_tree population", e)
            self.iface.messageBar().pushMessage("Error", f"QTRANUS error while updating layer.", level=2)
    

    def load_desutilitiestable(self, paths):
        try:   
            id_origin = self.cb_origin.currentText().split(" ")[0]
            id_destination = self.cb_destination.currentText().split(" ")[0]
            id_mode = self.cb_mode.currentText().split(" ")[0]
            id_path = int(self.cb_path.currentText())
            vertical_header = ['GenC','VehCharg','UserCharg','Dist','Time','Wait','MonC']
            horizontal_header = [ str(value) for value in range(1, len(paths)+1)]
            self.tbl_desutilities.setRowCount(len(vertical_header))
            self.tbl_desutilities.setColumnCount(len(horizontal_header))
            self.tbl_desutilities.setHorizontalHeaderLabels(horizontal_header) # Headers of columns table
            self.tbl_desutilities.horizontalHeader().setStretchLastSection(True)
            self.tbl_desutilities.setVerticalHeaderLabels(vertical_header)
            
            i = 0
            for value in paths:
                if int(value[0]['orig']) == int(id_origin) and int(value[0]['dest']) == int(id_destination) \
                    and int(value[0]['mode']) == int(id_mode):
                    self.tbl_desutilities.setItem(0,  i, QTableWidgetItem(str(value[0]['gencost'])))
                    self.tbl_desutilities.setItem(1,  i, QTableWidgetItem(str(value[0]['chargs'])))
                    self.tbl_desutilities.setItem(2,  i, QTableWidgetItem(str(value[0]['uchrgs'])))
                    self.tbl_desutilities.setItem(3,  i, QTableWidgetItem(str(value[0]['dist'])))
                    self.tbl_desutilities.setItem(4,  i, QTableWidgetItem(str(datetime.timedelta(float(value[0]['lnktme'])))))
                    self.tbl_desutilities.setItem(5,  i, QTableWidgetItem(str(datetime.timedelta(float(value[0]['waittme'])))))
                    self.tbl_desutilities.setItem(6,  i, QTableWidgetItem(str(value[0]['moncos'])))
                    i += 1
            
        except Exception as e:
            print("Error: tbl_desutilities population", e)


    def search_path_links(self, paths, id_origin, id_destination, id_mode, id_path):
        for value in paths:
            if int(value[0]['orig']) == int(id_origin) \
                and int(value[0]['dest']) == int(id_destination) \
                and int(value[0]['mode']) == int(id_mode) \
                and int(value[0]['path'].strip()) == int(id_path.strip()):
                for path in value[1]:
                    if path[0].strip():
                        if  int(path[0]) < 0:
                            table = ' operator '
                            mult = -1
                        else:
                            table = ' route '
                            mult = 1
                        id = int(path[0])*mult
                        result = self.dataBaseSqlite.selectAll(f"{table}", where=f" where id = {id}", columns=' name ')
                        path[0] = f"{id} {result[0][0]}" 
                        path[1] = path[1].strip()
                return value[1]
        return False

    
    def show_path_layer(self, paths, id_origin, id_destination, id_mode, id_path):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # create data structure
            ori_dest_mode_result = self.get_find_list(id_origin, id_destination, id_mode, id_path, paths)
            data_structure_links = self.get_linksid_elements_paths(ori_dest_mode_result, id_origin, id_destination)
            
            # Example data structure
            # data_structure_links = [(301, '84-6201'), (-1, '6101-6201'), (-2, '3101-6101'), (-3,'2302-3101'), (-4,'5704-5701'), (-4,'2302-5704')]

            # Find layer
            registry = QgsProject.instance()
            layersCount = len(registry.mapLayers())
            layer_network = registry.mapLayersByName('Network_Links')[0]
            epsg = layer_network.crs().postgisSrid()
            
            root = registry.layerTreeRoot()
            layer_group = root.findGroup("QTRANUS")
            layers_name = [lyr.name() for lyr in registry.mapLayers().values()]

            # Create new layer
            memory_route_lyr = QgsVectorLayer(f"LineString?crs=epsg:{epsg}", "Network_Pahts", "memory")
            memory_data = memory_route_lyr.dataProvider()
            memory_data.addAttributes([QgsField("operator_route",  QVariant.Int), QgsField("link_id",  QVariant.String)])
            #print(data_structure_links)
            features_attributes = []
            for value in data_structure_links:
                features_network = layer_network.getFeatures(QgsFeatureRequest().setFilterExpression( f"\"linkID\" = '{value[1]}' "))
                for feature_net in features_network:
                    features_attributes.append((feature_net, value))
            
            feat_arr = []
            for feature_attr in features_attributes:
                feat = feature_attr[0]
                #print([feature_attr[1][0], feature_attr[1][1]])
                feat.setAttributes([feature_attr[1][0], feature_attr[1][1]])
                feat_arr.append(feat)
            
            memory_route_lyr.startEditing()
            memory_route_lyr.dataProvider().addFeatures(feat_arr)
            memory_route_lyr.commitChanges()
                
            _ids = []
            categories = []
            for value in data_structure_links:
                if value[0] < 0:
                    _id = value[0]*-1
                    table = ' operator '
                    type = self.dataBaseSqlite.selectAll(table, where=f' where id = {_id} ', columns=' type ')
                    symbol_json_str = self.operators_symbols_lst(int(type[0][0]))
                    symbol = self.get_symbol_object(symbol_json_str)
                else:
                    symbol = QgsLineSymbol()
                    _id = value[0]    
                    table = ' route '
                operator_route = self.dataBaseSqlite.selectAll(table, where=f' where id = {_id} ', columns=' color, name ')
                name = operator_route[0][1]
                color = operator_route[0][0]
                symbol.setColor(QColor(color))
                symbol.setWidth(0.6)
                cat = QgsRendererCategory(value[0], symbol, f"""{table} {_id} {name}""")
                if value[0] not in _ids:
                    categories.append(cat)
                    _ids.append(value[0])

            categorized_renderer = QgsCategorizedSymbolRenderer('operator_route', categories)
            
            memory_route_lyr.setRenderer(categorized_renderer)
            msg = 'created'
            if 'Network_Pahts' in layers_name:
                layer_route = registry.mapLayersByName('Network_Pahts')
                layer_group.removeLayer(layer_route[0])
                registry.removeMapLayer(layer_route[0].id())
                msg = 'updated'

            registry.addMapLayer(memory_route_lyr, False)
            layer_group.insertLayer(0, memory_route_lyr)

            self.iface.messageBar().pushMessage("Info", f"QTRANUS Layer 'Network_paths' has been created.", level=0)

            # Remove UI Cursor loading...
            QApplication.restoreOverrideCursor()
        
        except Exception as e:
            # Remove UI Cursor loading...
            print("Error:", e)
            QApplication.restoreOverrideCursor()
        

    def get_find_list(self, id_origin, id_destination, id_mode, id_path, paths):
        for value in paths:
            if int(value[0]['orig']) == int(id_origin) and int(value[0]['dest']) == int(id_destination) \
                and int(value[0]['mode']) == int(id_mode) and int(value[0]['path']) == int(id_path):
                return value[1]
        return False


    def get_linksid_elements_paths(self, paths, id_origin, id_destination):
        data = []

        while([""] in paths): 
            paths.remove([""]) 
        
        for index, value in enumerate(paths):
            data.append((int(value[0].strip()),f"{id_origin}-{value[1].strip()}"))
            id_origin = value[1].strip()
        return data

    def load_scenarios(self):
        
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.scenarios_model = ScenariosModelSqlite(self.project_file)
        self.scenarios_tree.setModel(self.scenarios_model)
        self.scenarios_tree.expandAll()
        modelSelection = QItemSelectionModel(self.scenarios_model)
        modelSelection.setCurrentIndex(self.scenarios_model.index(0, 0, QModelIndex()), QItemSelectionModel.SelectCurrent)
        self.scenarios_tree.setSelectionModel(modelSelection)


    def load_routes(self):
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)
        
        scenario_selected_index = self.scenarios_tree.selectedIndexes()
        scenario_code = scenario_selected_index[0].model().itemFromIndex(scenario_selected_index[0]).text().split(" - ")[0]

        if len(scenario_code) <= 3:
            result_scenario_id = self.dataBaseSqlite.selectAll(" scenario ", where=f" where code = '{scenario_code}'")
            result_scenario_id = result_scenario_id[0][0]
            
            qry = f"""select a.color, a.id, a.name
                        from route a
                        where id_scenario = {result_scenario_id} order by 2 asc """
            result = self.dataBaseSqlite.selectAll(' route ', where=f" where id_scenario = '{result_scenario_id}'", columns=' color, id, name ', orderby=' order by 2 asc ')

            model = QtGui.QStandardItemModel()
            model.setHorizontalHeaderLabels(['Color','ID', 'Name'])
            if result:
                for x in range(0, len(result)):
                    model.insertRow(x)
                    z=0
                    for y in range(0,3):
                        if y == 0:
                            if result[x][z]:
                                model.setData(model.index(x, y), QtGui.QBrush(QColor(result[x][z])), Qt.BackgroundRole)
                            else:
                                model.setData(model.index(x, y), QtGui.QBrush(QColor(4294967295)), Qt.BackgroundRole)
                        else:
                            model.setData(model.index(x, y), result[x][z])
                        z+=1

                self.routes_tree.setModel(model)
                self.routes_tree.setColumnWidth(0, 37)
                self.routes_tree.setColumnWidth(1, QtWidgets.QHeaderView.ResizeToContents)

    
    def load_linktypes(self):
        self.project_file = f"{self.project['tranus_folder']}/{self.project['project_name']}"
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)

        # TODO: Importante validar el scenario seleccionado o el por defecto
        qry = """
                select 
                    a.symbology, a.id, a.name
                from link_type a
                where id_scenario = 1 order by 2 asc """
        #result = self.dataBaseSqlite.selectAll('route', columns='id, name, description')
        result = self.dataBaseSqlite.executeSql(qry)
                
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Symbol', 'ID', 'Name'])
        if result:
            for x in range(0, len(result)):
                model.insertRow(x)
                z=0
                for y in range(0,3):
                    if y == 0 and result[x][z]:
                        model.setData(model.index(x, y), self.get_symbol_object(result[x][z]).asImage(QSize(35,10)), Qt.DecorationRole)
                        #model.setData(model.index(x, y), self.get_symbol_object(result[x][z]).asImage(QSize(500,500)), Qt.DecorationRole)
                    else:
                        model.setData(model.index(x, y), result[x][z])
                    z+=1

            self.linktypes_tree.setModel(model)
            self.linktypes_tree.resizeColumnToContents(0)
            self.linktypes_tree.resizeColumnToContents(1)
            #self.routes_tree.setColumnWidth(1, QtWidgets.QHeaderView.ResizeToContents)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&qtranus'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        self.main_window.removeDockWidget(self.scenarios_dockwidget)
        del self.toolbar
        del self.scenarios_dockwidget
        del self.project


    def run(self):
        """Run method that performs all the real work"""
        QgsMessageLog.logMessage("Abriendo", 'QTranus')

        self.dlg.show()

        self.dlg.exec_()

    
    def get_symbol_object(self, symbol_srt):
        """ Return dictionary with objects symbols """
		# TODO: resolver tema de la symbologia correcta
        print(symbol_srt)
        symbol_obj = json.loads(symbol_srt.replace("'",'"'))
        symbol_layers = QgsLineSymbol()

        for layer_symbol in symbol_obj['layers_list']:
            obj_symbol = eval(f"Qgs{layer_symbol['type_layer']}SymbolLayer.create({layer_symbol['properties_layer']})")
            symbol_layers.appendSymbolLayer(obj_symbol)
        symbol_layers.deleteSymbolLayer(0)
        return symbol_layers

    
    def operators_symbols_lst(self, type):
        # Type: 1 Transit
        # Type: 2 Non motorized
        # Type: 3 Transit with routes
        # Type: 4 Normal

        symbol_group_list = [
            """{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'dash', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}""",
            """{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'round', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'round', 'line_color': '0,0,0,255', 'line_style': 'solid', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '-1', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}, {'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'round', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'round', 'line_color': '0,0,0,255', 'line_style': 'solid', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}""",
            """{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'solid', 'line_width': '0.26', 'line_width_unit': 'MM', 'offset': '1.2', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}, {'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'solid', 'line_width': '1.06', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}, {'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'solid', 'line_width': '0.26', 'line_width_unit': 'MM', 'offset': '-1.2', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}""",
            """{'type': 1, 'layers_list': [{'type_layer': 'SimpleLine', 'properties_layer': {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 'joinstyle': 'bevel', 'line_color': '35,35,35,255', 'line_style': 'dot', 'line_width': '0.46', 'line_width_unit': 'MM', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}}]}"""
        ]

        return symbol_group_list[type-1]
    

    def validate_scenario_pathsfile(self, scenario_code):
        """ Validate if exists sceneario file
        """
        paths_file = f"path_{scenario_code}.csv"
        abs_path = os.path.join(self.project['tranus_folder'], scenario_code, paths_file)

        if os.path.exists(abs_path):
            self.tab_widget_main.setTabEnabled(3, True)
        else:
            self.tab_widget_main.setTabEnabled(3, False)


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
import os, sys, os.path, re
from PyQt5.QtGui import  QIcon
from PyQt5 import QtWidgets
from PyQt5 import QtGui, uic, QtCore
from PyQt5.QtCore import QSettings, QVariant, QTranslator, qVersion, QCoreApplication, QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QAction, QLineEdit, QDockWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QDialog
from PyQt5.QtGui import *


# Initialize Qt resources from file resources.py
from . import resources_rc 
# Import the code for the dialog

import qgis
from qgis import *
from qgis.core import  QgsMessageLog, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo, QgsLineSymbolLayer, QgsSimpleLineSymbolLayer, QgsMapUnitScale, QgsSimpleLineSymbolLayer, QgsLineSymbol, QgsMarkerLineSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsWkbTypes, QgsPoint
from qgis.gui import QgsQueryBuilder

from .qtranus_project import QTranusProject
from .qtranus_dialog import QTranusDialog
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.data.DataBaseSqlite import DataBaseSqlite
#from newproject_dialog import QTranusNewProjectDialog


class QTranus:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.

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

        # Load layput dock Scenarios
        self.scenarios_dockwidget = uic.loadUi(os.path.join(os.path.dirname(__file__), 'scenarios_selector.ui'))
        self.scenarios_tree = self.scenarios_dockwidget.findChild(QtWidgets.QTreeView, 'scenarios')            
        self.scenarios_tree.clicked.connect(self.update_leyers)
        self.routes_tree = self.scenarios_dockwidget.findChild(QtWidgets.QTreeView, 'routes_tree')            
        self.routes_tree.setRootIsDecorated(False)
        self.routes_tree.clicked.connect(self.update_routes)

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
        self.addScenariosSection()
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QTranus', message)


    def update_leyers(self, selectedIndex):
        """
            @summary: Update Layers after scenario selection
        """
        self.scenarioSelectedIndex = selectedIndex
        self.scenarioCode = selectedIndex.model().itemFromIndex(selectedIndex).text().split(" - ")[0]
        
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
            qry.setSql( f"\"LinkId\" IN ({linksIds}) ")
            qry.accept()

    
    def update_routes(self):

        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())
        # TODO: Get epsg de la capa de Network
        layer = registry.mapLayersByName('Network_Links')[0]
        epsg = layer.crs().postgisSrid()

        layerRoutes = registry.mapLayersByName('Network_routes')
        if not layerRoutes:
            memoryLayer = QgsVectorLayer(f"LineString?crs=epsg:{epsg}", "Network_routes", "memory")

            memory_data = memoryLayer.dataProvider()
            memory_data.addAttributes([QgsField("route_id",  QVariant.Int)])
            memoryLayer.updateFields()
            registry.addMapLayer(memoryLayer)

            self.iface.messageBar().pushMessage("Info", f"QTRANUS Layer 'Network_routes' has been created", level=0)



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
        print("Load rutas Qtranus ", self.project_file)
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)

        # TODO: Importante validar el scenario seleccionado o el por defecto
        qry = """select a.id, a.name, a.description 
                     from route a
                     where id_scenario = 1 order by 1 asc """
        #result = self.dataBaseSqlite.selectAll('route', columns='id, name, description')
        result = self.dataBaseSqlite.executeSql(qry)

        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Id','Name', 'Description'])
        if result:
            for x in range(0, len(result)):
                model.insertRow(x)
                z=0
                for y in range(0,3):
                    model.setData(model.index(x, y), result[x][z])
                    z+=1

            self.routes_tree.setModel(model)
            self.routes_tree.setColumnWidth(0, QtWidgets.QHeaderView.Stretch)


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

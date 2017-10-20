# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OptionsTRANUS
                                 A QGIS plugin
 This plugin automates the execution of TRANUS programs.
                              -------------------
        begin                : 2017-02-23
        git sha              : $Format:%H$
        copyright            : (C) 2017 by STEEP Inria
        email                : emna.jribi@inria.fr
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources

from qgis.core import QgsProject, QgsMessageLog #Line added
# Import the code for the dialog
from .OptionsTRANUS_project import OptionsTRANUSProject
from .options_tranus_dialog import OptionsTRANUSDialog
import os.path


class OptionsTRANUS:
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
        settings_file = os.path.join(self.plugin_dir ,"config.ini")
        self.settings = QSettings(settings_file,QSettings.IniFormat)
    
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OptionsTRANUS_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
                
       
        #load config settings 
        self.tranus_project = self.settings.value("tranus_project")
        self.tranus_binaries = self.settings.value("tranus_binaries")
        
        #verify settings
        if self.tranus_project != None :
            if not os.path.exists(self.tranus_project):
                self.tranus_project = ""
        if self.tranus_binaries != None :        
            if not os.path.exists(self.tranus_binaries):
                self.tranus_binaries = ""
            if not os.path.isfile(os.path.join(self.tranus_binaries,'lcal.exe')) or not os.path.isfile(os.path.join(self.tranus_binaries,'pasos.exe')) :
                self.tranus_binaries = ""
        
        self.project = OptionsTRANUSProject(QgsProject.instance()) 
        self.dlg = OptionsTRANUSDialog(project = self.project,settings = self.settings,tranus_project = self.tranus_project,tranus_binaries = self.tranus_binaries)
        
        #set config settings 
        self.dlg.tranus_workspace.setText(self.tranus_project)
        self.dlg.tranus_bin_path.setText(self.tranus_binaries)
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Options TRANUS')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'OptionsTRANUS')
        self.toolbar.setObjectName(u'OptionsTRANUS')

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
        return QCoreApplication.translate('OptionsTRANUS', message)


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

        # Create the dialog (after translation) and keep reference
        

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

        icon_path = ':/plugins/OptionsTRANUS/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Options TRANUS'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Options TRANUS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        QgsMessageLog.logMessage("EMNA", 'OptionsTRANUS', QgsMessageLog.INFO) #line added
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.exec_()
       

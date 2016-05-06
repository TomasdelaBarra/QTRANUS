# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QTranusDialog
                                 A QGIS plugin
 qtranus
                             -------------------
        begin                : 2015-07-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by qtranus
        email                : pedroburonv@gmail.com
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

import os

from PyQt4 import QtGui, uic

from .settings_dialog import SettingsDialog
from .scenarios_model import ScenariosModel

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qtranus_dialog_base.ui'))

class ValidStringLength(QtGui.QValidator):
    def __init__(self, min, max, parent):
        QtGui.QValidator.__init__(self, parent)

        self.min = min
        self.max = max

    def validate(self, s, pos):
        if self.max > -1 and len(s) > self.max:
            return QtGui.QValidator.Invalid, s, pos

        if self.min > -1 and len(s) < self.min:
            return QtGui.QValidator.Intermediate, s, pos

        return QtGui.QValidator.Acceptable, s, pos


class QTranusDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, project, parent=None):
        """Constructor."""
        super(QTranusDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.project = project

        self.project_name = self.findChild(QtGui.QLineEdit, 'project_name')
        self.project_name.textEdited.connect(self.save_project_name)
        self.tranus_folder = self.findChild(QtGui.QLineEdit, 'tranus_folder')
        self.zone_shape = self.findChild(QtGui.QLineEdit, 'zone_shape')
        self.net_shape = self.findChild(QtGui.QLineEdit, 'net_shape')
        self.centroid_shape = self.findChild(QtGui.QLineEdit, 'centroid_shape')
        self.button_box = self.findChild(QtGui.QDialogButtonBox, 'button_box')
        self.configure = self.findChild(QtGui.QCommandLinkButton, 'configure')
        self.configure.clicked.connect(self.configure_dialog)
        self.tranus_folder_btn = self.findChild(QtGui.QToolButton, 'tranus_folder_btn')
        self.tranus_folder_btn.clicked.connect(self.select_tranus_folder)
        self.zones_shape_btn = self.findChild(QtGui.QToolButton, 'zones_shape_btn')
        self.zones_shape_btn.clicked.connect(self.select_shape(self.select_zones_shape))
        self.net_shape_btn = self.findChild(QtGui.QToolButton, 'net_shape_btn')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.expression = self.findChild(QtGui.QLineEdit, 'expression')
        self.expression.textEdited.connect(self.expression_changes)
        self.reload_scenarios()
		
    def expression_changes(self):
        self.project['expression'] = self.expression.text()
    
    def save_project_name(self):
        self.project['project_name'] = self.project_name.text()
        self.check_configure()

    def select_zones_shape(self, file_name):
        # expr = self.expression.text()
        if self.project.load_zones_shape(file_name):
            self.zone_shape.setText(file_name)
        else:
            self.zone_shape.setText('')
        self.check_configure()

    def select_tranus_folder(self):
        folder = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.tranus_folder.setText(folder)
            if not self.project.load_tranus_folder(folder):
                self.tranus_folder.setText('')
            self.reload_scenarios()
        self.check_configure()

    def select_shape(self, callback):
        def select_file():
            file_name = QtGui.QFileDialog.getOpenFileName(parent=self, caption="Elija el archivo", filter="*.*, *.shp")
            if file_name:
                callback(file_name)

        return select_file

    def configure_dialog(self):
        settings = SettingsDialog(parent=self, project=self.project)
        settings.show()

        result = settings.exec_()

    def show(self):
        self.project.load()
        if self.project['project_name']:
            self.project_name.setText(self.project['project_name'])
        else:
            self.project_name.setText('QTranus Project')
            self.project_name.selectAll()
        if self.project['zones_shape']:
            self.zone_shape.setText(self.project['zones_shape'])
        if self.project.tranus_project:
            self.tranus_folder.setText(self.project.tranus_project.path)
        self.check_configure()
        super(QTranusDialog, self).show()

    def close(self):
        pass

    def reload_scenarios(self):
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)

    def check_configure(self):
        self.configure.setEnabled(self.project.is_valid())

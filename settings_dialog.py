
import os

from PyQt4 import QtGui, uic, QtCore

from .scenarios_model import ScenariosModel
from .zonelayer_dialog import ZoneLayerDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings.ui'))


class SettingsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, project, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.setupUi(self)

        self.project = project

        self.layer_list = self.findChild(QtGui.QListView, 'layer_list')
        self.layer_list_model = LayerListModel(self)

        self.layer_list.setModel(self.layer_list_model)
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.reload_scenarios()

        self.zone_layer = self.findChild(QtGui.QCommandLinkButton, 'zone_layer')
        self.zone_layer.clicked.connect(self.add_zone_layer)


    def reload_scenarios(self):
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)

    def add_zone_layer(self):
        dialog = ZoneLayerDialog(self)
        dialog.show()
        result = dialog.exec_()
        print (result)


class LayerListModel(QtGui.QStandardItemModel): 
    def __init__(self, parent=None):
        super(LayerListModel, self).__init__(parent)

        item = QtGui.QStandardItem("Capa 1")
        self.setItem(0, 0, item)


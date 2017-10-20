# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import *


class ScenariosModel(QtGui.QStandardItemModel):
    root_item = None

    def __init__(self, parent):
        super(ScenariosModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(['Scenarios'])

        if parent.project.tranus_project:
            self.scenarios = parent.project.tranus_project.scenarios
            root = self.scenarios.root
            self.root_item = self.add_scenario(root)
            self.appendRow(self.root_item)
        else:
            self.root_item = QtGui.QStandardItem("There is no data to load, please select a tranus workspace and click on load scenarios")
            self.root_item.setEditable(False)
            self.appendRow(self.root_item)
            self.scenarios = None

    def add_scenarios(self, root):
        pass

    def add_scenario(self, scenario):
        item = QtGui.QStandardItem(scenario.name + " - " + scenario.code)
        item.setEditable(False)
        item.setCheckable(True)
        item.setSelectable(False)
        for child in scenario.children:
            item.appendRow(self.add_scenario(child))
        self.parent().scenarios.setExpanded(self.indexFromItem(item), True)
        return item

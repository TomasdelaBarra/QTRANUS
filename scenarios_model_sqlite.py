# -*- coding: utf-8 -*-
import os, re, webbrowser, numpy as np

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from .tranus import Scenarios, Scenario
from .classes.data.DataBaseSqlite import DataBaseSqlite

class ScenariosModelSqlite(QtGui.QStandardItemModel):
    root_item = None

    def __init__(self, tranus_folder):
        super(ScenariosModelSqlite, self).__init__()
        self.setHorizontalHeaderLabels(['Scenarios'])
        self.tranus_folder = tranus_folder
        data = DataBaseSqlite(self.tranus_folder).selectAll('scenario')

        self.plugin_dir = os.path.dirname(__file__)

        if data:
            lines = data
            self.scenarios = Scenarios.load_sqlite(lines)
            root = self.scenarios.root
            self.root_item = self.add_scenario(root) 
            self.appendRow(self.root_item)
        else:
            self.root_item = QtGui.QStandardItem("There is no data to load")
            self.root_item.setEditable(False)
            self.appendRow(self.root_item)
            self.scenarios = None

    def add_scenarios(self, root):
        pass

    def add_scenario(self, scenario):
        item = QtGui.QStandardItem(scenario.code + " - " + scenario.name)
        item.setEditable(False)
        #item.setCheckable(False)
        item.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        for child in scenario.children:
            item.appendRow(self.add_scenario(child))
            item.setIcon(QIcon(self.plugin_dir+"/icons/square-gray.png"))
        #self.parent().scenarios.setExpanded(self.indexFromItem(item), True)
        return item

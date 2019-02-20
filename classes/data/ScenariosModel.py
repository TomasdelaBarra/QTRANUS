# -*- coding: utf-8 -*-
from PyQt5 import QtGui
 
 
class ScenariosModel(QtGui.QStandardItemModel):
    root_item = None
 
    def __init__(self, parent):
        super(ScenariosModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(['Scenarios'])
        addElements = False
        if parent.scenarios is not None:
            if parent.scenarios.root is not None:
                addElements = True
            else:
                addElements = False
        else:
            addElements = False
            
        if(addElements):
            self.root_item = self.__add_root_scenario(parent.scenarios.root)
            self.appendRow(self.root_item)
        else:
            self.root_item = QtGui.QStandardItem("There is no data to load")
            self.root_item.setEditable(False)
            self.appendRow(self.root_item)
            self.scenarios = None
            
    def __add_root_scenario(self, rootScenario):
        item = QtGui.QStandardItem(rootScenario.id + " - " + rootScenario.name)
        item.setEditable(False)
        for child in rootScenario.children:
            item.appendRow(self.__add_root_scenario(child))
        self.parent().scenarios_tree.setExpanded(self.indexFromItem(item), True)
        return item
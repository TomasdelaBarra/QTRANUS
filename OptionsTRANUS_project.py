#encoding=UTF-8

from __future__ import unicode_literals
from os import listdir
from os.path import isfile, join


from .tranus import TranusProject

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsField, QgsFeature, QgsRendererRangeV2, QgsStyleV2, QgsGraduatedSymbolRendererV2 , QgsSymbolV2, QgsVectorJoinInfo 

from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor

from qgis.core import QgsMessageLog  # for debugging
from PyQt4.Qt import QMessageBox



import os
import re
import random
import string
from .options_tranus_dialog import OptionsTRANUSDialog

class OptionsTRANUSProject(object):
    def __init__(self, proj):
        """
            @summary: Constructor
        """
        self.proj = proj
        self.tranus_project = None
        self.shape = None
       
        self.load()
        #self.map_data = MapData()
        self.zonesIdFieldName = None
        
    def load(self):
        """
            @summary: Load method
        """
        self.tranus_project = None
        self.load_tranus_folder()
        
        

    
    def load_tranus_folder(self, folder=None):
        """
            @summary: Loads tranus project folder
            @param folder: Folder
            @type folder: String
        """
        folder = folder or self['tranus_folder']
        
        path = os.path.join(folder, 'W_TRANUS.CTL')
        print (path)
        try:
            tranus_project = TranusProject.load_project(path)
        except Exception as e:
            print (e)
            self.tranus_project = None
            return False
        else:
            self.tranus_project = tranus_project
            self['tranus_folder'] = folder
            return True


    def __getitem__(self, key):
        value, _ = self.proj.readEntry('TRANUS OPTIONS', key)
        return value

    def __setitem__(self, key, value):
        self.proj.writeEntry('TRANUS OPTIONS', key, value)

    def is_created(self):
        return not not self['project_name']

    def is_valid(self):
        
        return not not (self['tranus_folder'])

    def get_layers_group(self):
        """
            @summary: Gets layer group
        """
        group_name = self['layers_group_name'] or 'TRANUS OPTIONS'
        layers_group = self.proj.layerTreeRoot().findGroup(group_name)
        if layers_group is None:
            layers_group = self.proj.layerTreeRoot().addGroup(group_name)
        return layers_group

   
    


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
from classes.GeneralObject import GeneralObject
from classes.Indicator import Indicator
from classes.MapData import MapData
from classes.Stack import Stack

import os
import re
import random
import string

def load_map_indicators(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    prog = re.compile('location_indicators_(.*)\..*')
    indicators = Indicator()
    for fn in files:
        result=prog.match(fn)
        if result != None:
            indicators.load_indicator_file(path+"/"+fn)
    return indicators
    
class QTranusProject(object):
    def __init__(self, proj):
        self.proj = proj
        self.tranus_project = None
        self.shape = None
        self.load()
        self.map_data = MapData()
        self.zonesIdFieldName = None

    def load(self):
        self.tranus_project = None
        self.load_tranus_folder()
        self.load_shapes()

        
    def addLayer(self, layerName, scenariosExpression, fieldname, sectorsExpression):
        """
            @summary: Adds new layer to project
            @return: Boolean result of layer addition
        """
        
        if scenariosExpression is None:
            QMessageBox.warning(None, "Scenarios expression", "There is not scenarios information.")
            print  ("There is not scenarios information.")
            return False
        
        if (self.zonesIdFieldName is None) or (self.zonesIdFieldName == ''):
            QMessageBox(None, "Zone Id", "Zone Id Field Name was not specified.")
            print("Zone Id Field Name was not specified.")
            return False
        
        registry = QgsMapLayerRegistry.instance()
        layersCount = len(registry.mapLayers())
        #print ('Number of Layers: {0}'.format(layersCount))
        group = self.get_layers_group()
        layer = QgsVectorLayer(self.shape, layerName, 'ogr') # memory???
        registry.addMapLayer(layer, False)
        if not layer.isValid():
            self['zones_shape'] = ''
            self['zones_shape_id'] = ''
            return False
        
        # Gets shape's file folder
        project = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]
        #print(project)
        
        # Gets field name
        fieldname = fieldname.strip()
        
        #layerName = layerName.encode('UTF-8')
        
        # Creation of CSV file to be used for JOIN operation
        result, minValue, maxValue, rowCounter = self.map_data.create_csv_file(layerName, scenariosExpression, fieldname, project, sectorsExpression)
        if result:
            csvFile_uri = ("file:///" + project + "/" + layerName + ".csv?delimiter=,").encode('utf-8')
            print(csvFile_uri)
            csvFile = QgsVectorLayer(csvFile_uri, layerName, "delimitedtext")
            registry.addMapLayer(csvFile, False)
            shpField = self.zonesIdFieldName
            csvField = 'ZoneId'
            joinObject = QgsVectorJoinInfo()
            joinObject.joinLayerId = csvFile.id()
            joinObject.joinFieldName = csvField
            joinObject.targetFieldName = shpField
            joinObject.memoryCache = True
            layer.addJoin(joinObject)
            
            print(minValue, maxValue, rowCounter)
            
            myStyle = QgsStyleV2().defaultStyle()
            defaultColorRampNames = myStyle.colorRampNames()        
            ramp = myStyle.colorRamp(defaultColorRampNames[0])
            ranges  = []
            nCats = ramp.count()
            #print("nCats: {0}".format(nCats))
            print("Total colors: "+str(nCats))
            rng = maxValue - minValue
            red0 = 255
            red1 = 0
            green0 = 255
            green1 = 0
            blue0 = 255
            blue1 = 255
            nCats = 50
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                red = red0 + float(i)/float(nCats-1)*(red1-red0)
                green = green0 + float(i)/float(nCats-1)*(green1-green0)
                blue = blue0 + float(i)/float(nCats-1)*(blue1-blue0)
                symbol.setColor(QColor(red, green, blue))
                myRange = QgsRendererRangeV2(v0,v1, symbol, "")
                ranges.append(myRange)
            
            # The first parameter refers to the name of the field that contains the calculated value (expression) 
            renderer = QgsGraduatedSymbolRendererV2(layerName + "_JoinField" + fieldname, ranges)
            #renderer = QgsGraduatedSymbolRendererV2("JoinField" + fieldname, ranges)
            
            renderer.setSourceColorRamp(ramp)
            layer.setRendererV2(renderer)

            group.insertLayer((layersCount+1), layer)
            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()

        return True

    def load_tranus_folder(self, folder=None):
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
    
    def load_zones_shape(self, shape): #, expr):
        self.shape = shape
        #print("self.shape: "+self.shape)
        registry = QgsMapLayerRegistry.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(shape, 'Zonas', 'ogr')
        if not layer.isValid():
            self['zones_shape'] = ''
            self['zones_shape_id'] = ''
            return False, None
        
        zones_shape_fields = [field.name() for field in layer.pendingFields()]
        
        project = shape[0:max(shape.rfind('\\'), shape.rfind('/'))]     
            
        if self.map_data.indicators is not None:
            if len(self.map_data.indicators.scenarios) == 0:
                self.map_data.indicators = load_map_indicators(project)
                self.map_data.load_dictionaries()

        if self['zones_shape_id']:
            existing_tree = self.proj.layerTreeRoot().findLayer(self['zones_shape_id'])
            if existing_tree:
                existing = existing_tree.layer()
                registry.removeMapLayer(existing.id())   # OJO TODO: esto lo movi a la derecha, estaba fuera del if

        registry.addMapLayer(layer, False)
        group.insertLayer(0, layer)
        self['zones_shape'] = layer.source()
        self['zones_shape_id'] = layer.id()
        return True, zones_shape_fields 

    def __getitem__(self, key):
        value, _ = self.proj.readEntry('qtranus', key)
        return value

    def __setitem__(self, key, value):
        self.proj.writeEntry('qtranus', key, value)


    def is_created(self):
        return not not self['project_name']

    def is_valid(self):
        return not not (self['zones_shape'] and self['project_name'] and self['tranus_folder'])

    def get_layers_group(self):
        group_name = self['layers_group_name'] or 'QTRANUS'
        layers_group = self.proj.layerTreeRoot().findGroup(group_name)
        if layers_group is None:
            layers_group = self.proj.layerTreeRoot().addGroup(group_name)
        return layers_group

    def load_shapes(self):
        zones_shape = self['zones_shape']
        layers_group = self.get_layers_group()
        
        for layer in layers_group.findLayers():
            if layer.layer().source() == zones_shape:
                self['zones_shape_id'] = layer.layer().id()
            

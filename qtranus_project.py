#encoding=UTF-8

from __future__ import unicode_literals
import os
import re
import random
import string
import numpy as np
from pickle import NONE
from os import listdir
from os.path import isfile, join

from PyQt5 import QtWidgets
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

import qgis.utils
from qgis.core import QgsMessageLog, QgsProject, QgsVectorLayer, QgsFields, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo, QgsProject, QgsMapUnitScale, QgsSimpleLineSymbolLayer, QgsLineSymbol

from .tranus import TranusProject
from .classes.GeneralObject import GeneralObject
from .classes.Indicator import Indicator
from .classes.MapData import MapData
from .classes.Stack import Stack
from .classes.ZoneCentroid import ZoneCentroid
from .classes.TripMatrix import TripMatrix
from .classes.network.Network import Network
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Helpers import Helpers
from .classes.general.FileManagement import FileManagement as FileMXML
from .classes.ExpressionData import ExpressionData
from .classes.CustomExceptions import InputFileSourceError

class QTranusProject(object):
    def __init__(self, proj, iface):
        """
            @summary: Constructor
        """
        self.iface = iface
        self.proj = proj
        self.tranus_project = None
        self.map_data = MapData()
        self.shape = None
        self.zonesIdFieldName = None
        self.network_model = Network()
        self.centroids_file_path = None
        self.network_link_shape_path = None
        self.network_nodes_shape_path = None
        self.db_path = None
        self.custom_variables_dict = dict()
        self.load()
            

    def load(self):
        """
            @summary: Load method
        """
        self.custom_variables_dict = QgsProject.instance().customVariables()
        self.tranus_project = None
        self.proj.readProject.connect(self.loadLayersProject)
        self.proj.layerRemoved.connect(self.removeLayer)
        self.proj.removeAll.connect(self.clearObjects)
        self.load_tranus_folder()
        self.load_shapes()


    def clearObjects(self):
        """
            @summary: Clear Objects
        """
        #print("Data Eliminada")
        self.map_data.clear_dictionaries()


    def removeLayer(self, idLayer):
        config = self.proj.customVariables()
        try:
            projectPath = config['project_qtranus_folder']
            if FileMXML.if_exist_xml_layers(projectPath):
                FileMXML.remove_layer_element(projectPath, idLayer)

        except Exception as e:
            print(e)
            pass

        
    def loadLayersProject(self):
        """
            @summary: Load layers from XML file
            @param config: Type Layer
            @type config: Varible Project
            @param layers: layers
            @type layers: layers
            @param config: projectPath
            @type config: projectPath
        """
        config = self.proj.customVariables()
        layers = self.proj.mapLayers()
        projectPath = config['project_qtranus_folder'] or None

        if FileMXML.if_exist_xml_layers(projectPath):
            self.load_tranus_folder(projectPath)
            self.map_data.indicators = self.load_map_indicators(projectPath)
            self.load_map_trip_structure(projectPath, None)
            self.map_data.load_dictionaries()    
            centroid_shape_file_path = self['centroid_shape_file_path'] or None
            network_links_shape_file_path = self['network_links_shape_file_path'] or None
            network_nodes_shape_file_path = self['network_nodes_shape_file_path'] or None
            zones_shape_file_path = self['zones_shape'] or None

            self.load_tranus_folder(self.tranus_project.path)
            self.load_project_file_shape_files(zones_shape_file_path, 'zones')
            self.load_project_file_shape_files(network_links_shape_file_path, 'network')
            self.load_project_file_shape_files(centroid_shape_file_path, 'centroids')
            
            for layerId in layers:
                if layers[layerId].name()[-5:]=='zones':
                    shapeFile = config['project_qtranus_zones_shape'] or None 
                    sectorsExpression, fieldName, layerName, scenariosExpression, idFieldName = FileMXML.find_layer_data(projectPath, layerId)
                    scenariosExpression = Helpers().strToList(scenariosExpression)
                    scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
                    sectorsExpressionResult, sectorsExpressionList = ExpressionData.validate_sectors_expression(sectorsExpression.strip())
                    self.loadZonesLayer(layerName, scenariosExpressionStack, fieldName, sectorsExpressionList, layerId, shapeFile, idFieldName)
                
                if layers[layerId].name()[-7:]=='network':
                    self.load_map_trip_structure(projectPath, None)
                    shapeFileNetwork = config['project_qtranus_network_shape'] or None
                    sectorsExpression, field, layerName, scenarioExpression, fieldName, method, level, color = FileMXML.find_layer_data(projectPath, layerId)
                    scenariosExpression = Helpers.expressionToList(scenarioExpression)
                    scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
                    sectorsExpressionList = []
                    if scenariosExpressionResult and sectorsExpression!='':
                        sectorsExpressionResult, sectorsExpressionList = ExpressionData.validate_sectors_expression(sectorsExpression.strip())
                    self.network_model.loadNetworkLayer(layerName, scenariosExpressionStack, sectorsExpressionList, field, level, projectPath, shapeFileNetwork, method, color, layerId)

                if layers[layerId].name()[-6:]=='matrix':
                    self.centroids_file_path = config['project_qtranus_matrix_shape'] or None
                    self.load_zones_centroids_data()
                    sectorsExpression, field, layerName, scenarioExpression, id_field_name, originZones, destinationZones, method, color = FileMXML.find_layer_data(projectPath, layerId)
                    scenariosExpression = Helpers.expressionToList(scenarioExpression)
                    originZonesList = Helpers.expressionToList(originZones)
                    destinationZonesList = Helpers.expressionToList(destinationZones)
                    scenariosExpressionResult, scenariosExpressionStack = ExpressionData.validate_scenarios_expression(scenariosExpression)
                    matrixExpressionResult, matrixExpressionList = ExpressionData.validate_sectors_expression(sectorsExpression.strip())                      
                    self.loadMatrixLayer(projectPath, layerName, scenariosExpressionStack, originZonesList, destinationZonesList, matrixExpressionList, method, color, layerId)

                    
    def getLayers(self,typeLayer):
        """
            @summary: List of layer Type
            @param layerType: Type Layer
            @type layerType: String
            @return: List of type of layer
        """
        lstLayers = QgsProject.instance().mapLayers()

        layers = []

        for key, values in lstLayers.items():
            if typeLayer == 'zones':
                if str(values.name())[-5:]==typeLayer:
                    layers.append({"id":values.id(),"text":values.name()})
            elif typeLayer == 'network':
                if str(values.name())[-7:]==typeLayer:
                    layers.append({"id":values.id(),"text":values.name()})
            elif typeLayer == 'matrix':
                if str(values.name())[-6:]==typeLayer:
                    layers.append({"id":values.id(),"text":values.name()})
        
        return layers

    def addZonesLayer(self, progressBar, layerName, scenariosExpression, fieldName, sectorsExpression, sectorsExpressionText):
        """
            @summary: Adds new zone layer to project
            @param layerName: Layer Name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: String
            @param fieldName: Field name
            @type fieldName: String
            @param sectorsExpression: Sectors expression
            @type sectorsExpression: String
            @return: Boolean result of layer addition
        """
        if scenariosExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if (self.zonesIdFieldName is None) or (self.zonesIdFieldName == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Zone Id", "Zone Id Field Name was not specified.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Zone Id Field Name was not specified.")
            return False
        
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        # Gets shape's file folder
        projectPath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]

        # Set Custom Project Variable to save Project path
        tranus_dictionary = dict(project_qtranus_folder=projectPath, project_qtranus_zones_shape=self.shape)
        self.custom_variables_dict.update(tranus_dictionary)
        QgsProject.instance().setCustomVariables(self.custom_variables_dict)

        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())
        
        group = self.get_layers_group()
        layer = QgsVectorLayer(self.shape, layerName, 'ogr')
        epsg = layer.crs().postgisSrid()
        #registry.addMapLayer(layer, False)
        if not layer.isValid():
            self['zones_shape'] = ''
            self['zones_shape_id'] = ''
            return False
        
        # Gets field name
        fieldName = fieldName.strip()
        
        # layerName = layerName.encode('UTF-8')
        # Create VectorLayer in Memory
        result, minValue, maxValue, rowCounter, zoneList = self.map_data.create_data_memory(layerName, scenariosExpression, fieldName, projectPath, sectorsExpression)
        progressBar.setValue(15)

        if result:

            shpField = self.zonesIdFieldName

            # Create a list with layer features
            feats = [ feat for feat in layer.getFeatures() ]

            # Create a vector layer with data on Memory 
            memoryLayer = QgsVectorLayer("Polygon?crs=epsg:"+str(epsg), layerName+"_zones", "memory")
            registry.addMapLayer(memoryLayer)
            
            memory_data = memoryLayer.dataProvider()
            joinedFieldName = "JoinField"+"_"+fieldName

            attr = layer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName,QVariant.Double)]
            memory_data.addAttributes(attr)
            memory_data.addFeatures(feats)
            
            num = 30
            progressBar.setValue(num)
            progressInterval = 70/len(zoneList)

            memoryLayer.startEditing()
            counter = 0
            for itemZone in zoneList:
                value = 0
                if fieldName.upper() == 'TOTPROD':
                    value = float(itemZone.totProd)
                if fieldName.upper() == 'TOTDEM':
                    value = float(itemZone.totDem)
                if fieldName.upper() == 'PRODCOST':
                    value = float(itemZone.prodCost)
                if fieldName.upper() == 'PRICE':
                    value = float(itemZone.price)
                if fieldName.upper() == 'MINRES':
                    value = float(itemZone.minRes)
                if fieldName.upper() == 'MAXRES':
                    value = float(itemZone.maxRes)
                if fieldName.upper() == 'ADJUST':
                    value = float(itemZone.adjust)
            
                minValue = min(minValue, value)
                maxValue = max(maxValue, value)
                
                it = memoryLayer.getFeatures( u'"'+shpField+'" = '+itemZone.id )

                num += progressInterval
                progressBar.setValue(num)

                for id_feature in it:
                    result = memoryLayer.changeAttributeValue(id_feature.id(), memory_data.fieldNameIndex(joinedFieldName), QVariant(round(value,2)))
                    counter += 1


            memoryLayer.commitChanges()
            
            myStyle = QgsStyle().defaultStyle()
            defaultColorRampNames = myStyle.colorRampNames()        
            ramp = myStyle.colorRamp(defaultColorRampNames[0])
            ranges  = []
            nCats = ramp.count()
            rng = maxValue - minValue
            red0 = 255
            red1 = 0
            green0 = 255
            green1 = 0
            blue0 = 255
            blue1 = 255
            nCats = 8
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                symbol = QgsSymbol.defaultSymbol(memoryLayer.geometryType())
                red = red0 + float(i)/float(nCats-1)*(red1-red0)
                green = green0 + float(i)/float(nCats-1)*(green1-green0)
                blue = blue0 + float(i)/float(nCats-1)*(blue1-blue0)
                symbol.setColor(QColor(red, green, blue))
                myRange = QgsRendererRange(v0,v1, symbol, "")
                ranges.append(myRange)
            
            # The first parameter refers to the name of the field that contains the calculated value (expression) 
            modeRender = QgsGraduatedSymbolRenderer.Mode(2)
            renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
            renderer.setMode(modeRender)
            renderer.setSourceColorRamp(ramp)
            renderer.updateClasses(memoryLayer, modeRender, 8)
            memoryLayer.setRenderer(renderer)
            typeLayer = "zone"
            # Create XML File ".qtranus" with the parameters of the executions
            if FileMXML.if_exist_xml_layers(projectPath):
                if FileMXML.if_exist_layer(projectPath, memoryLayer.id()):
                    FileMXML.update_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
                else:
                    FileMXML.add_layer_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText, shpField, typeLayer)
            else:
                FileMXML.create_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText, shpField, typeLayer)

            #group.insertLayer((layersCount+2), memoryLayer)
            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()
            progressBar.setValue(100)

            if counter == 0:
                return False
        return True


    def editZonesLayer(self, progressBar, layerName, scenariosExpression, fieldName, sectorsExpression, sectorsExpressionText, layerId):
        """
            @summary: Adds new zone layer to project
            @param layerName: Layer Name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: String
            @param fieldName: Field name
            @type fieldName: String
            @param sectorsExpression: Sectors expression
            @type sectorsExpression: String
            @param layerId: Layer ID to Edit features
            @type layerId: String
            @return: Boolean result of layer addition
        """
        if scenariosExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("There is not scenarios information.")
            return False
        
        if (self.zonesIdFieldName is None) or (self.zonesIdFieldName == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Zone Id", "Zone Id Field Name was not specified.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Zone Id Field Name was not specified.")
            return False
        
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        # Gets shape's file folder
        projectPath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]
        layer = QgsVectorLayer(self.shape, layerName, 'ogr')
        epsg = layer.crs().postgisSrid()

        registry = QgsProject.instance()

        memoryLayer = registry.mapLayer(layerId)
                
        # Gets field name
        fieldName = fieldName.strip()
        
        # Creation of VectorLayer on Memory
        result, minValue, maxValue, rowCounter, zoneList = self.map_data.create_data_memory(layerName, scenariosExpression, fieldName, projectPath, sectorsExpression)
        progressBar.setValue(15)

        if result:

            shpField = self.zonesIdFieldName

            # Create a vector layer with data on Memory 
            memory_data = memoryLayer.dataProvider()
            joinedFieldName = "JoinField"+"_"+fieldName

            attr = memoryLayer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName,QVariant.Double)]
            memory_data.addAttributes(attr)

            num = 30
            progressBar.setValue(num)
            progressInterval = 70/len(zoneList)

            memoryLayer.startEditing()
            counter = 0
            for itemZone in zoneList:
                value = 0
                if fieldName.upper() == 'TOTPROD':
                    value = float(itemZone.totProd)
                if fieldName.upper() == 'TOTDEM':
                    value = float(itemZone.totDem)
                if fieldName.upper() == 'PRODCOST':
                    value = float(itemZone.prodCost)
                if fieldName.upper() == 'PRICE':
                    value = float(itemZone.price)
                if fieldName.upper() == 'MINRES':
                    value = float(itemZone.minRes)
                if fieldName.upper() == 'MAXRES':
                    value = float(itemZone.maxRes)
                if fieldName.upper() == 'ADJUST':
                    value = float(itemZone.adjust)
            
                minValue = min(minValue, value)
                maxValue = max(maxValue, value)
                
                num += progressInterval
                progressBar.setValue(num)
                it = memoryLayer.getFeatures( u'"'+shpField+'" = '+itemZone.id )

                for id_feature in it:
                    memoryLayer.changeAttributeValue(id_feature.id(), memory_data.fieldNameIndex(joinedFieldName), QVariant(value))
                    counter += 1

            memoryLayer.commitChanges()
            
            myStyle = QgsStyle().defaultStyle()
            defaultColorRampNames = myStyle.colorRampNames()        
            ramp = myStyle.colorRamp(defaultColorRampNames[0])
            ranges  = []
            nCats = ramp.count()
            rng = maxValue - minValue
            red0 = 255
            red1 = 0
            green0 = 255
            green1 = 0
            blue0 = 255
            blue1 = 255
            nCats = 8
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                symbol = QgsSymbol.defaultSymbol(memoryLayer.geometryType())
                red = red0 + float(i)/float(nCats-1)*(red1-red0)
                green = green0 + float(i)/float(nCats-1)*(green1-green0)
                blue = blue0 + float(i)/float(nCats-1)*(blue1-blue0)
                symbol.setColor(QColor(red, green, blue))
                myRange = QgsRendererRange(v0,v1, symbol, "")
                ranges.append(myRange)
            
            # The first parameter refers to the name of the field that contains the calculated value (expression) 
            renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
            renderer.updateClasses(memoryLayer, modeRender, 8)
            renderer.setSourceColorRamp(ramp)
            memoryLayer.setRenderer(renderer)
            typeLayer = "zone"
            # Create XML File ".qtranus" with the parameters of the executions
            if FileMXML.if_exist_xml_layers(projectPath):
                if FileMXML.if_exist_layer(projectPath, memoryLayer.id()):
                    FileMXML.update_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
                else:
                    FileMXML.add_layer_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText, typeLayer)
            else:
                FileMXML.create_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText, typeLayer)
                
            #group.insertLayer((layersCount+2), memoryLayer)
            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()
            if counter == 0:
                return False
        return True

    def loadZonesLayer(self, layerName, scenariosExpression, fieldName, sectorsExpression,  layerId, shapeFile, idFieldName):
        """
            @summary: Adds new zone layer to project
            @param layerName: Layer Name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: String
            @param fieldName: Field name
            @type fieldName: String
            @param sectorsExpression: Sectors expression
            @type sectorsExpression: String
            @param layerId: Layer ID to Edit features
            @type layerId: String
            @param shapeFile: URI to shapefile
            @type shapeFile: String
            @return: Boolean result of layer addition
        """
        self.zonesIdFieldName = idFieldName
        
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        # Gets shape's file folder
        projectPath = shapeFile[0:max(shapeFile.rfind('\\'), shapeFile.rfind('/'))]
        layer = QgsVectorLayer(shapeFile, layerName, 'ogr')
        epsg = layer.crs().postgisSrid()

        registry = QgsProject.instance()

        memoryLayer = registry.mapLayer(layerId)
        
        # Delete all Attributes of the Layer
        memoryLayer.startEditing()
        memoryLayer.deleteAttributes(memoryLayer.attributeList())
        memoryLayer.commitChanges()

        # Gets field name
        fieldName = fieldName.strip()
        
        # Creation of VectorLayer on Memory
        result, minValue, maxValue, rowCounter, zoneList = self.map_data.load_data_memory(layerName, scenariosExpression, fieldName, projectPath, sectorsExpression)
        if result:

            shpField = self.zonesIdFieldName

            # Create a vector layer with data on Memory 
            memory_data = memoryLayer.dataProvider()

            joinedFieldName = "JoinField"+"_"+fieldName

            # Create a list with layer features
            feats = [ feat for feat in layer.getFeatures() ]

            # Create a vector layer with data on Memory 
            attr = layer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName,QVariant.Double)]
            memory_data.addAttributes(attr)
            memory_data.addFeatures(feats)

            memoryLayer.startEditing()
            for itemZone in zoneList:
                value = 0
                if fieldName.upper() == 'TOTPROD':
                    value = float(itemZone.totProd)
                if fieldName.upper() == 'TOTDEM':
                    value = float(itemZone.totDem)
                if fieldName.upper() == 'PRODCOST':
                    value = float(itemZone.prodCost)
                if fieldName.upper() == 'PRICE':
                    value = float(itemZone.price)
                if fieldName.upper() == 'MINRES':
                    value = float(itemZone.minRes)
                if fieldName.upper() == 'MAXRES':
                    value = float(itemZone.maxRes)
                if fieldName.upper() == 'ADJUST':
                    value = float(itemZone.adjust)
            
                minValue = min(minValue, value)
                maxValue = max(maxValue, value)
                it = memoryLayer.getFeatures( u'"'+shpField+'" = '+itemZone.id )

                for id_feature in it:
                    memoryLayer.changeAttributeValue(id_feature.id(), memory_data.fieldNameIndex(joinedFieldName), QVariant(value))

            memoryLayer.commitChanges()
            
            print(minValue, maxValue, rowCounter)
            
            myStyle = QgsStyle().defaultStyle()
            defaultColorRampNames = myStyle.colorRampNames()        
            ramp = myStyle.colorRamp(defaultColorRampNames[0])
            ranges  = []
            nCats = ramp.count()
            rng = maxValue - minValue
            red0 = 255
            red1 = 0
            green0 = 255
            green1 = 0
            blue0 = 255
            blue1 = 255
            nCats = 8
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                symbol = QgsSymbol.defaultSymbol(memoryLayer.geometryType())
                red = red0 + float(i)/float(nCats-1)*(red1-red0)
                green = green0 + float(i)/float(nCats-1)*(green1-green0)
                blue = blue0 + float(i)/float(nCats-1)*(blue1-blue0)
                symbol.setColor(QColor(red, green, blue))
                myRange = QgsRendererRange(v0,v1, symbol, "")
                ranges.append(myRange)
            
            # The first parameter refers to the name of the field that contains the calculated value (expression) 
            modeRender = QgsGraduatedSymbolRenderer.Mode(2)
            renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
            renderer.setMode(modeRender)
            renderer.setSourceColorRamp(ramp)
            renderer.updateClasses(memoryLayer, modeRender, 8)
            
            memoryLayer.setRenderer(renderer)

            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()
        return True

    def addMatrixLayer(self, progressBar, layerName, scenariosExpression, originZones, destinationZones, matrixExpression, matrixExpressionText, method, color):
        print("Centroids {} ".format(self.centroids_file_path))
        if scenariosExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if originZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not origin zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not origin zones information.")
            return False
        
        if destinationZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not destination zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not destination zones information.")
            return False
        
        # Creates centroids layer
        if not self.centroids_file_path is None:
            self.load_zones_centroids_data()
        else:
            self.load_zones_centroids()

        progressBar.setValue(30)
        # Gets shape's file folder
        registry = QgsProject.instance()
        projectPath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]

        # Set Custom Project Variable to save Project path
        try:
            self.centroids_file_path = self.centroids_file_path[0]
        except:
            self.centroids_file_path=''

        tranus_dictionary = dict(project_qtranus_folder=projectPath, project_qtranus_matrix_shape=self.centroids_file_path)
        self.custom_variables_dict.update(tranus_dictionary)
        QgsProject.instance().setCustomVariables(self.custom_variables_dict)

        intMethod = 0 if method == "Color" else 1

        result, matrixResultData, minValue, maxValue, matrixList = self.map_data.create_trip_matrix_memory_file(layerName, scenariosExpression, originZones, destinationZones, matrixExpression, projectPath)
        
        if result:
            layer = registry.mapLayersByName('Zonas_Centroids')[0]
            epsg = layer.crs().postgisSrid()
            group = self.get_layers_group()
            tripsMatrixLayer = QgsVectorLayer("LineString?crs=epsg:"+str(epsg),  layerName +"_matrix", "memory")
        progressBar.setValue(50)
        
        joinedFieldName = "Trip"
        feats_arr = []
        fields = QgsFields()
        attrs = [QgsField('OrZoneId_DestZoneId', QVariant.String),QgsField('Trip', QVariant.Double)]

        tripsMatrixLayer.dataProvider().addAttributes(attrs)

        tripsMatrixLayer.startEditing()
        for valor in matrixList:
            geom = QgsGeometry()
            geom = geom.fromWkt(valor[1])
            feat = QgsFeature()
            feat.setGeometry(geom)
            feat.setAttributes([valor[0],valor[2]])
            feats_arr.append(feat)

        tripsMatrixLayer.dataProvider().addFeatures(feats_arr)
        tripsMatrixLayer.commitChanges()

        rowCounter = len(matrixResultData)
        myStyle = QgsStyle().defaultStyle()
        defaultColorRampNames = myStyle.colorRampNames()        
        ramp = myStyle.colorRamp(defaultColorRampNames[0])
        ranges  = []
        nCats = ramp.count()
        rng = maxValue - minValue
        nCats = 8
        scale = QgsMapUnitScale(minValue, maxValue)

        if method == "Color":
            color1 = list(map(lambda x: int(x), color['color1'].split(",")[0:3]))
            color2 = list(map(lambda x: int(x), color['color2'].split(",")[0:3]))
            interpolatedColors = Helpers.linear_gradient(color1, color2, nCats)

        progressBar.setValue(55)
        for i in range(0,nCats):
            v0 = minValue + rng/float(nCats)*i
            v1 = minValue + rng/float(nCats)*(i+1)        
            progressBar.setValue(65)
            if method == "Color":
                line = QgsSimpleLineSymbolLayer(QColor(interpolatedColors['r'][i], interpolatedColors['g'][i], interpolatedColors['b'][i]))
                line.setWidth(0.8)
                line.setOffset(0.55)
                symbol = QgsLineSymbol()
                symbol.changeSymbolLayer(0,line)
                myRange = QgsRendererRange(v0,v1, symbol, "")                    
            elif method == "Size":
                qcolor = QColor()
                qcolor.setRgb(color)
                line = QgsSimpleLineSymbolLayer(qcolor)
                line.setOffset(0.2)
                symbolo = QgsLineSymbol()
                symbolo.changeSymbolLayer(0,line)
                myRange = QgsRendererRange(v0,v1, symbolo, "")

            ranges.append(myRange)
            
        # The first parameter refers to the name of the field that contains the calculated value (expression) 
        modeRender = QgsGraduatedSymbolRenderer.Mode(2)
        renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
        renderer.setMode(modeRender)
        renderer.setGraduatedMethod(intMethod)

        if method == "Size":
            renderer.setSymbolSizes(0.200000, 2.60000)

        renderer.setSourceColorRamp(ramp)
        tripsMatrixLayer.setRenderer(renderer)
        QgsProject.instance().addMapLayer( tripsMatrixLayer, False )
        group.insertLayer(len(QgsProject.instance().mapLayers())+1, tripsMatrixLayer)
        
        # Create XML File ".qtranus" with the parameters of the executions
        typeLayer = "matrix"
        fieldName = "Trip"
        shpField = ""
        if FileMXML.if_exist_xml_layers(projectPath):
            if FileMXML.if_exist_layer(projectPath, tripsMatrixLayer.id()):
                FileMXML.update_xml_file(tripsMatrixLayer.name(), tripsMatrixLayer.id(), scenariosExpression, fieldName, matrixExpression, projectPath, matrixExpressionText, method=method, color=color, originZones=originZones, destinationZones=destinationZones)
            else:
                FileMXML.add_layer_xml_file(tripsMatrixLayer.name(), tripsMatrixLayer.id(), scenariosExpression, fieldName, matrixExpression, projectPath, matrixExpressionText, shpField, typeLayer, method=method, color=color, originZones=originZones, destinationZones=destinationZones)
        else:
            FileMXML.create_xml_file(tripsMatrixLayer.name(), tripsMatrixLayer.id(), scenariosExpression, fieldName, matrixExpression, projectPath, matrixExpressionText, shpField, typeLayer, method=method, color=color, originZones=originZones, destinationZones=destinationZones)
        progressBar.setValue(100)
        return True
        
    def loadMatrixLayer(self, projectPath, layerName, scenariosExpression, originZones, destinationZones, matrixExpression, method, color, layerId):

        if scenariosExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if originZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not origin zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not origin zones information.")
            return False
        
        if destinationZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not destination zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not destination zones information.")
            return False

        # Gets shape's file folder
        registry = QgsProject.instance()

        intMethod = 0 if method == "Color" else 1
        result, matrixResultData, minValue, maxValue, matrixList = self.map_data.create_trip_matrix_memory_file(layerName, scenariosExpression, originZones, destinationZones, matrixExpression, projectPath)
        print("matrixList {}".format(matrixList))
        if result:
            layer = registry.mapLayersByName('Zonas_Centroids')[0]
            epsg = layer.crs().postgisSrid()
            group = self.get_layers_group()

            tripsMatrixLayer = registry.mapLayer(layerId)

        tripsMatrixLayer.startEditing()
        tripsMatrixLayer.deleteAttributes([0,1]) 
        tripsMatrixLayer.commitChanges()

        joinedFieldName = "Trip"
        feats_arr = []
        fields = QgsFields()
        attrs = [QgsField('OrZoneId_DestZoneId', QVariant.String),QgsField('Trip', QVariant.Double)]

        tripsMatrixLayer.dataProvider().addAttributes(attrs)

        tripsMatrixLayer.startEditing()
        for valor in matrixList:
            geom = QgsGeometry()
            geom = geom.fromWkt(valor[1])
            feat = QgsFeature()
            feat.setGeometry(geom)
            feat.setAttributes([valor[0],valor[2]])
            feats_arr.append(feat)

        tripsMatrixLayer.dataProvider().addFeatures(feats_arr)
        tripsMatrixLayer.commitChanges()

        rowCounter = len(matrixResultData)
        myStyle = QgsStyle().defaultStyle()
        defaultColorRampNames = myStyle.colorRampNames()        
        ramp = myStyle.colorRamp(defaultColorRampNames[0])
        ranges  = []
        nCats = ramp.count()
        rng = maxValue - minValue
        nCats = 8
        scale = QgsMapUnitScale(minValue, maxValue)
        color = eval(color)
        if method == "Color":
            color1 = list(map(lambda x: int(x), color['color1'].split(",")[0:3]))
            color2 = list(map(lambda x: int(x), color['color2'].split(",")[0:3]))
            interpolatedColors = Helpers.linear_gradient(color1, color2, nCats)

        for i in range(0,nCats):
            v0 = minValue + rng/float(nCats)*i
            v1 = minValue + rng/float(nCats)*(i+1)        
            if method == "Color":
                line = QgsSimpleLineSymbolLayer(QColor(interpolatedColors['r'][i], interpolatedColors['g'][i], interpolatedColors['b'][i]))
                line.setWidth(0.8)
                line.setOffset(0.55)
                symbol = QgsLineSymbol()
                symbol.changeSymbolLayer(0,line)
                myRange = QgsRendererRange(v0,v1, symbol, "")                    
            elif method == "Size":
                qcolor = QColor()
                qcolor.setRgb(color)
                line = QgsSimpleLineSymbolLayer(qcolor)
                line.setOffset(0.2)
                symbolo = QgsLineSymbol()
                symbolo.changeSymbolLayer(0,line)
                myRange = QgsRendererRange(v0,v1, symbolo, "")

            ranges.append(myRange)
            
        # The first parameter refers to the name of the field that contains the calculated value (expression) 
        modeRender = QgsGraduatedSymbolRenderer.Mode(2)
        renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
        renderer.setMode(modeRender)
        renderer.setGraduatedMethod(intMethod)

        if method == "Size":
            renderer.setSymbolSizes(0.200000, 2.60000)

        renderer.setSourceColorRamp(ramp)
        tripsMatrixLayer.setRenderer(renderer)

        return True

    def editMatrixLayer(self, progressBar, layerName, scenariosExpression, originZones, destinationZones, matrixExpression, matrixExpressionText, method, color, oldLayerId):
        progressBar.setValue(30)
        if scenariosExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if originZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not origin zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not origin zones information.")
            return False
        
        if destinationZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not destination zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not destination zones information.")
            return False
        registry = QgsProject.instance()
        
        # Creates centroids layer
        if not self.centroids_file_path is None:
            self.load_zones_centroids_data()
        else:
            self.load_zones_centroids()
        
        # Gets shape's file folder
        projectPath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]

        intMethod = 0 if method == "Color" else 1
        #result, matrixResultData, minValue, maxValue = self.map_data.create_trip_matrix_csv_file(layerName, scenariosExpression, originZones, destinationZones, matrixExpression, projectPath)
        result, matrixResultData, minValue, maxValue, matrixList = self.map_data.create_trip_matrix_memory_file(layerName, scenariosExpression, originZones, destinationZones, matrixExpression, projectPath)

        if result:
            layer = registry.mapLayersByName('Zonas_Centroids')[0]
            epsg = layer.crs().postgisSrid()
            group = self.get_layers_group()
            tripsMatrixLayer = QgsVectorLayer("LineString?crs=epsg:"+str(epsg),  layerName +"_matrix", "memory")
        progressBar.setValue(50)
        
        joinedFieldName = "Trip"
        feats_arr = []
        fields = QgsFields()
        attrs = [QgsField('OrZoneId_DestZoneId', QVariant.String),QgsField('Trip', QVariant.Double)]

        tripsMatrixLayer.dataProvider().addAttributes(attrs)

        tripsMatrixLayer.startEditing()
        for valor in matrixList:
            geom = QgsGeometry()
            geom = geom.fromWkt(valor[1])
            feat = QgsFeature()
            feat.setGeometry(geom)
            feat.setAttributes([valor[0],valor[2]])
            feats_arr.append(feat)

        tripsMatrixLayer.dataProvider().addFeatures(feats_arr)
        tripsMatrixLayer.commitChanges()

        rowCounter = len(matrixResultData)
        myStyle = QgsStyle().defaultStyle()
        defaultColorRampNames = myStyle.colorRampNames()        
        ramp = myStyle.colorRamp(defaultColorRampNames[0])
        ranges  = []
        nCats = ramp.count()
        rng = maxValue - minValue
        nCats = 8
        scale = QgsMapUnitScale(minValue, maxValue)

        if method == "Color":
            color1 = list(map(lambda x: int(x), color['color1'].split(",")[0:3]))
            color2 = list(map(lambda x: int(x), color['color2'].split(",")[0:3]))
            interpolatedColors = Helpers.linear_gradient(color1, color2, nCats)

        progressBar.setValue(55)
        for i in range(0,nCats):
            v0 = minValue + rng/float(nCats)*i
            v1 = minValue + rng/float(nCats)*(i+1)        
            progressBar.setValue(65)
            if method == "Color":
                line = QgsSimpleLineSymbolLayer(QColor(interpolatedColors['r'][i], interpolatedColors['g'][i], interpolatedColors['b'][i]))
                line.setWidth(0.8)
                line.setOffset(0.55)
                symbol = QgsLineSymbol()
                symbol.changeSymbolLayer(0,line)
                myRange = QgsRendererRange(v0,v1, symbol, "")                    
            elif method == "Size":
                qcolor = QColor()
                qcolor.setRgb(color)
                line = QgsSimpleLineSymbolLayer(qcolor)
                line.setOffset(0.2)
                symbolo = QgsLineSymbol()
                symbolo.changeSymbolLayer(0,line)
                myRange = QgsRendererRange(v0,v1, symbolo, "")

            ranges.append(myRange)
            
        # The first parameter refers to the name of the field that contains the calculated value (expression) 
        modeRender = QgsGraduatedSymbolRenderer.Mode(2)
        renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
        renderer.setMode(modeRender)
        renderer.setGraduatedMethod(intMethod)

        if method == "Size":
            renderer.setSymbolSizes(0.200000, 2.60000)

        renderer.setSourceColorRamp(ramp)
        tripsMatrixLayer.setRenderer(renderer)
        QgsProject.instance().addMapLayer( tripsMatrixLayer, False )
        group.insertLayer(len(QgsProject.instance().mapLayers())+1, tripsMatrixLayer)
        
        # Create XML File ".qtranus" with the parameters of the executions
        typeLayer = "matrix"
        fieldName = "Trip"
        shpField = ""
        registry.removeMapLayers([oldLayerId])
        if FileMXML.if_exist_xml_layers(projectPath):
            if FileMXML.if_exist_layer(projectPath, oldLayerId):
                FileMXML.update_xml_file(tripsMatrixLayer.name(), tripsMatrixLayer.id(), scenariosExpression, fieldName, matrixExpression, projectPath, matrixExpressionText, method=method, color=color, originZones=originZones, destinationZones=destinationZones, oldIdLayer=oldLayerId)
            else:
                FileMXML.add_layer_xml_file(tripsMatrixLayer.name(), tripsMatrixLayer.id(), scenariosExpression, fieldName, matrixExpression, projectPath, matrixExpressionText, shpField, typeLayer, method=method, color=color, originZones=originZones, destinationZones=destinationZones)
        else:
            FileMXML.create_xml_file(tripsMatrixLayer.name(), tripsMatrixLayer.id(), scenariosExpression, fieldName, matrixExpression, projectPath, matrixExpressionText, shpField, typeLayer, method=method, color=color, originZones=originZones, destinationZones=destinationZones)
        progressBar.setValue(100)
        return True


    def load_tranus_folder(self, folder=None):
        """
            @summary: Loads tranus project folder
            @param folder: Folder
            @type folder: String
        """
        folder = folder or self['tranus_folder']
        # path = os.path.join(folder, 'W_TRANUS.CTL')
        path = folder
        try:

            #Load all indicators (Sectors, Scenarios, Operator, Routes)
            self.map_data = MapData()
            self.map_data.indicators = self.load_map_indicators(folder)
            self.map_data.load_dictionaries()
            if self.load_map_trip_structure(folder, None):
                self.map_data.load_dictionaries()
            #End load
            
            tranus_project = TranusProject.load_project(path)

        except Exception as e:
            print (e)
            self.tranus_project = None
            return False
        else:
            self.tranus_project = tranus_project
            self['tranus_folder'] = folder
            return True
    

    def load_map_indicators(self, path):
        """
            @summary: Loads zone indicators
            @param path: Path
            @type path: String 
        """

        files = [f for f in listdir(path) if isfile(join(path, f))]
        prog = re.compile('location_indicators_(.*)\..*')
        indicators = Indicator()
        for fn in files:
            result=prog.match(fn)
            if result != None:
                indicators.load_indicator_file(path+"/"+fn)
        return indicators
    

    def load_map_trip_structure(self, path, scenario):
        """
            @summary: Loads trips structure
            @param path: Path
            @type path: String
        """
        fileName = None
        tripMatrix = None
        files = [f for f in listdir(path) if isfile(join(path, f))]
        
        if scenario is None:
            fileName = re.compile('trip_matrices_(.*)\..*')
        else:
            selectedScenario = next((sc for sc in self.map_data.trip_matrices if sc.Id == scenario), None)
            if selectedScenario is not None:
                return True
            else:
                fileName = re.compile('trip_matrices_' + scenario + '\..*')

        for fn in files:
            isValidFile = fileName.match(fn)
            if isValidFile != None:
                tripMatrixItem = TripMatrix()
                tripMatrix = np.genfromtxt(path + "/" + fn, delimiter = ',', skip_header = 0
                                , dtype = None
                                #, names = [str('OrZonId'), str('OrZonName'), str('DeZonId'), str('DeZonName'), str('CatId'), str('CatName'), str('Trips')]
                                , names = True
                                )
                tripMatrixItem.Id = fn[14:17] if scenario is None else scenario 
                tripMatrixItem.Name = tripMatrixItem.Id
                tripMatrixItem.tripMatrix = tripMatrix
                self.map_data.trip_matrices.append(tripMatrixItem)
                
                if tripMatrix is not None and scenario == None:
                    self.map_data.load_matrix_zones()
                
                return True
            
        return False
    
    def load_zones_shape(self, shape):
        """
            @summary: Loads zone shape
            @param shape: Path
            @type shape: String
        """
        self.shape = shape
        #print("self.shape: "+self.shape)
        #registry = QgsProject.instance()
        registry = QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(shape, 'Zonas', 'ogr')
        if not layer.isValid():
            self['zones_shape'] = ''
            self['zones_shape_id'] = ''
            return False, None
        
        zones_shape_fields = [field.name() for field in layer.fields()]
        project = shape[0:max(shape.rfind('\\'), shape.rfind('/'))]     
        
        if self['zones_shape_id']:
            existing_tree = self.proj.layerTreeRoot().findLayer(self['zones_shape_id'])
            if existing_tree:
                existing = existing_tree.layer()
                registry.removeMapLayer(existing.id())

        # Load dictionaries with data "Sectors, Scenarios etc ..."
        #if self.map_data.indicators is not None:
            #if len(self.map_data.indicators.scenarios) == 0:
        """self.map_data = MapData()
        self.map_data.indicators = self.load_map_indicators(project)
        self.map_data.load_dictionaries()
        if self.load_map_trip_structure(project, None):
            self.map_data.load_dictionaries()"""
        
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
        #return not not self.project_name

    def is_valid(self):
        return not not (self['zones_shape'] and self['project_name'] and self['tranus_folder'])
        #return not not (self.zones_shape and self.project_name and self.tranus_folder)
    
    def is_valid_network(self):
        print(self['network_links_shape_file_path'], self['project_name'], self['tranus_folder'])
        return not not (self['network_links_shape_file_path'] and self['project_name'] and self['tranus_folder'])
        #return not not (self.network_links_shape_file_path and self.project_name and self.tranus_folder)

    def get_layers_group(self):
        """
            @summary: Gets layer group
        """
        group_name = self['layers_group_name'] or 'QTRANUS'
        layers_group = self.proj.layerTreeRoot().findGroup(group_name)
        if layers_group is None:
            layers_group = self.proj.layerTreeRoot().addGroup(group_name)
        return layers_group

    def load_shapes(self):
        """
            @summary: Loads zone shape
        """
        zones_shape = self['zones_shape']
        layers_group = self.get_layers_group()
        
        for layer in layers_group.findLayers():
            if layer.layer().source() == zones_shape:
                self['zones_shape_id'] = layer.layer().id()

    def load_centroid_file(self, file_path):
        """
            @summary: Loads centroid shape
            @param file_path: File path
            @type file_path: String
            @return: Boolean value of the load
        """
        self.centroids_file_path = file_path
        registry =  QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(file_path[0], 'Zonas_Centroids', 'ogr')
        if not layer.isValid():
            self['centroid_shape_file_path'] = ''
            self['centroid_shape_id'] = ''
            return False

        registry.addMapLayer(layer, False)
        group.insertLayer(0, layer)
        self['centroid_shape_file_path'] = layer.source()
        self['centroid_shape_id'] = layer.id()
        return True 
    
    def load_network_links_shape_file(self, file_path):
        self.network_link_shape_path = file_path if isinstance(file_path,str) else file_path[0]
        
        registry = QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(self.network_link_shape_path, 'Network_Links', 'ogr')
        
        if not layer.isValid():
            self['network_links_shape_file_path'] = ''
            self['network_links_shape_id'] = ''
            return False, False
        network_shape_fields = [field.name() for field in layer.fields()]    
        registry.addMapLayer(layer, False)
        group.insertLayer(0, layer)
        self['network_links_shape_file_path'] = layer.source()
        self['network_links_shape_id'] = layer.id()
        return True, network_shape_fields


    def load_network_nodes_shape_file(self, file_path):
        self.network_nodes_shape_path = file_path if isinstance(file_path,str) else file_path[0]
        registry = QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(self.network_nodes_shape_path, 'Network_Nodes', 'ogr')

        if not layer.isValid():
            self['network_nodes_shape_file_path'] = ''
            self['network_nodes_shape_id'] = ''
            return False

        nodes_shape_fields = [field.name() for field in layer.fields()]    

        registry.addMapLayer(layer, False)
        group.insertLayer(0, layer)
        self['network_nodes_shape_file_path'] = layer.source()
        self['network_nodes_shape_id'] = layer.id()
        return True, nodes_shape_fields

    def load_project_file_shape_files(self, file_path, shape):
        layer_name = ''
        shape_path = ''
        shape_id = ''

        if shape == 'zones':
            self.shape = file_path
            print("SHAPE FILE PATH {} ".format(file_path))
            shape = file_path
            layer = QgsVectorLayer(file_path, 'Zonas', 'ogr')
            if not layer.isValid():
                self['zones_shape'] = ''
                self['zones_shape_id'] = ''
                return False, None
        
            zones_shape_fields = [field.name() for field in layer.fields()]   
       
            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()

            return True, zones_shape_fields

        
        if shape == 'centroids':
            self.centroids_file_path = file_path
            layer_name = 'Zonas_Centroids'
            shape_path = 'centroid_shape_file_path'
            shape_id = 'centroid_shape_id'
       
        if shape == 'network':
            self.network_link_shape_path = file_path
            layer_name = 'Network_Links'
            shape_path = 'network_links_shape_file_path'
            shape_id = 'network_links_shape_id'

        layer = QgsVectorLayer(file_path, layer_name, 'ogr')
        if not layer.isValid():
            self[shape_path] = ''
            self[shape_id] = ''
            return False
            
        self[shape_path] = layer.source()
        self[shape_id] = layer.id()

        return True
    
    def load_db_file(self, file_path):
        self.db_path = file_path
        self['db_path'] = self.db_path  
    
    def load_zones_centroids_data(self):
        """
            @summary: Loads centroids information from file
        """
        filePath = self.centroids_file_path[0:max(self.centroids_file_path[0].rfind('\\'), self.centroids_file_path[0].rfind('/'))]
        layer = QgsProject.instance().mapLayersByName('Zonas_Centroids')[0]
        epsg = layer.crs().postgisSrid()
        prov =  layer.dataProvider()
        group = self.get_layers_group()
        for f in layer.getFeatures():
            pt = f.geometry().centroid().asPoint()
            zoneCentroid = ZoneCentroid()
            zoneCentroid.id = f.attributes()[0]
            zoneCentroid.name = f.attributes()[1]
            zoneCentroid.longitude = pt.x()
            zoneCentroid.latitude = pt.y()
            self.map_data.zoneCentroids.append(zoneCentroid)
        
        #self.map_data.create_trip_matrix_csv_file(filePath)
#         tripMatrixFileUri = ("file:///%s?crs=%s&delimiter=%s&wktField=%s" % (filePath + "/trips_map.csv", str(epsg), ",", "Geom")).encode('utf-8') 
#         tripsMatrixLayer = QgsVectorLayer(tripMatrixFileUri, layer.name() + '_trips_map', 'delimitedtext')
#         QgsProject.instance().addMapLayer( tripsMatrixLayer, False )
#         group.insertLayer(len(QgsProject.instance().mapLayers())+1, tripsMatrixLayer)
    
    def load_zones_centroids(self):
        """
            @summary: Loads centroids file information from centroid layer and creates a csv file
        """
        
        layer = QgsProject.instance().mapLayersByName('Zonas')[0]
        filePath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]
        group = self.get_layers_group()
        print(layer.name())
        
        if layer is not None:
            epsg = layer.crs().postgisSrid()
            uri = ("Point?crs=epsg:" + str(epsg) + "&field=zoneID:long&field=zoneName:string&field=posX:double&field=posY:double&index=yes")
            print("Proyecto: {}".format(type(uri), uri))
            mem_layer = QgsVectorLayer(uri, layer.name() + '_Centroids', 'memory')
            prov = mem_layer.dataProvider()
            
            for f in layer.getFeatures():
                feat = QgsFeature()
                pt = f.geometry().centroid().asPoint()
                print(pt)
                feat.setAttributes([f.attributes()[0], f.attributes()[1], pt.x(), pt.y()])
                feat.setGeometry(QgsGeometry.fromPointXY(pt))
                prov.addFeatures([feat])
                
                zoneCentroid = ZoneCentroid()
                zoneCentroid.id = f.attributes()[0]
                zoneCentroid.name = f.attributes()[1]
                zoneCentroid.longitude = pt.x()
                zoneCentroid.latitude = pt.y()
                self.map_data.zoneCentroids.append(zoneCentroid)
            
            QgsProject.instance().addMapLayer(mem_layer, False)
            group.insertLayer(len(QgsProject.instance().mapLayers())+1, mem_layer)
            
            # Creates the Centroids CSV file
            self.map_data.create_zone_centroids_csv_file(filePath, layer.name())
#encoding=UTF-8

from __future__ import unicode_literals
from os import listdir
from os.path import isfile, join


from .tranus import TranusProject

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo 

from qgis.core import QgsProject

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

from qgis.core import QgsMessageLog  # for debugging
from .classes.GeneralObject import GeneralObject
from .classes.Indicator import Indicator
from .classes.MapData import MapData
from .classes.Stack import Stack
from .classes.ZoneCentroid import ZoneCentroid
from .classes.TripMatrix import TripMatrix
from .classes.network.Network import Network
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.FileManagement import FileManagement as FileMXML

import os
import re
import random
import string
import numpy as np
from pickle import NONE

class QTranusProject(object):
    def __init__(self, proj):
        """
            @summary: Constructor
        """
        self.proj = proj
        self.tranus_project = None
        self.shape = None
        self.centroids_file_path = None
        self.load()
        self.map_data = MapData()
        self.zonesIdFieldName = None
        self.network_model = Network()
        self.network_link_shape_path = None
        self.network_nodes_shape_path = None
        self.db_path = None

    def load(self):
        """
            @summary: Load method
        """
        self.tranus_project = None
        self.load_tranus_folder()
        self.load_shapes()


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
            if str(values.name())[-5:]==typeLayer:
                layers.append({"id":values.id(),"text":values.name()})
        
        return layers

    def addZonesLayer(self, layerName, scenariosExpression, fieldName, sectorsExpression, sectorsExpressionText):
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
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if (self.zonesIdFieldName is None) or (self.zonesIdFieldName == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Zone Id", "Zone Id Field Name was not specified.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Zone Id Field Name was not specified.")
            return False
        
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        # Gets shape's file folder
        projectPath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]
        
        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())
        #print ('Number of Layers: {0}'.format(layersCount))

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
        # Creation of VectorLayer on Memory
        result, minValue, maxValue, rowCounter, zoneList = self.map_data.create_data_memory(layerName, scenariosExpression, fieldName, projectPath, sectorsExpression)
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
                    #feature = memoryLayer.getFeature(id_feature.id())
                    

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
            memoryLayer.setRenderer(renderer)

            # Create XML File ".qtranus" with the parameters of the executions
            if FileMXML.if_exist_xml_layers(projectPath):
                if FileMXML.if_exist_layer(projectPath, memoryLayer.id()):
                    FileMXML.update_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
                else:
                    FileMXML.add_layer_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
            else:
                FileMXML.create_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)

            #group.insertLayer((layersCount+2), memoryLayer)
            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()
        return True

    def editZonesLayer(self, layerName, scenariosExpression, fieldName, sectorsExpression, sectorsExpressionText, layerId):
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
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if (self.zonesIdFieldName is None) or (self.zonesIdFieldName == ''):
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Zone Id", "Zone Id Field Name was not specified.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
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
        if result:

            shpField = self.zonesIdFieldName

            # Create a vector layer with data on Memory 
            memory_data = memoryLayer.dataProvider()
            joinedFieldName = "JoinField"+"_"+fieldName

            attr = memoryLayer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName,QVariant.Double)]
            memory_data.addAttributes(attr)

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
                    #feature = memoryLayer.getFeature(id_feature.id())
                    

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
            renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
            
            renderer.setSourceColorRamp(ramp)
            memoryLayer.setRenderer(renderer)

            # Create XML File ".qtranus" with the parameters of the executions
            if FileMXML.if_exist_xml_layers(projectPath):
                if FileMXML.if_exist_layer(projectPath, memoryLayer.id()):
                    FileMXML.update_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
                else:
                    FileMXML.add_layer_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
            else:
                FileMXML.create_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText)
                
            #group.insertLayer((layersCount+2), memoryLayer)
            self['zones_shape'] = layer.source()
            self['zones_shape_id'] = layer.id()
        return True

    def addMatrixLayer(self, layerName, scenariosExpression, originZones, destinationZones, matrixExpression):

        if scenariosExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Matrix expression", "There is not scenarios information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not scenarios information.")
            return False
        
        if originZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Matrix expression", "There is not origin zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not origin zones information.")
            return False
        
        if destinationZones is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Matrix expression", "There is not destination zones information.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print  ("There is not destination zones information.")
            return False

        # Looks for scenarios information
        #if not slef.map_data.trip_matrices is None:
        
        # Creates centroids layer
        if not self.centroids_file_path is None:
            self.load_zones_centroids_data()
        else:
            self.load_zones_centroids()
        
        # Gets shape's file folder
        projectPath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]
        #filePath = self.centroids_file_path[0:max(self.centroids_file_path.rfind('\\'), self.centroids_file_path.rfind('/'))]
        
        result = self.map_data.create_trip_matrix_csv_file(layerName, scenariosExpression, originZones, destinationZones, matrixExpression, projectPath)
        if result:
            layer = QgsMapLayerRegistry.instance().mapLayersByName('Zonas_Centroids')[0]
            epsg = layer.crs().postgisSrid()
            group = self.get_layers_group()
            tripMatrixFileUri = ("file:///%s?crs=%s&delimiter=%s&wktField=%s" % (projectPath + "/trips_map.csv", str(epsg), ",", "Geom")).encode('utf-8') 
            tripsMatrixLayer = QgsVectorLayer(tripMatrixFileUri, layerName + '_trips_map', 'delimitedtext')
            QgsMapLayerRegistry.instance().addMapLayer( tripsMatrixLayer, False )
            group.insertLayer(len(QgsMapLayerRegistry.instance().mapLayers())+1, tripsMatrixLayer)
        
        return True

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
        #registry = QgsMapLayerRegistry.instance()
        registry = QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(shape, 'Zonas', 'ogr')
        if not layer.isValid():
            self['zones_shape'] = ''
            self['zones_shape_id'] = ''
            return False, None
        
        zones_shape_fields = [field.name() for field in layer.fields()]
        project = shape[0:max(shape.rfind('\\'), shape.rfind('/'))]     
            
        if self.map_data.indicators is not None:
            if len(self.map_data.indicators.scenarios) == 0:
                self.map_data.indicators = self.load_map_indicators(project)
                self.map_data.load_dictionaries()
                if self.load_map_trip_structure(project, None):
                    self.map_data.load_dictionaries()

        if self['zones_shape_id']:
            existing_tree = self.proj.layerTreeRoot().findLayer(self['zones_shape_id'])
            if existing_tree:
                existing = existing_tree.layer()
                registry.removeMapLayer(existing.id())

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
    
    def load_network_links_shape_file(self, file_path):
        self.network_link_shape_path = file_path
        registry = QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(file_path[0], 'Network_Links', 'ogr')
        if not layer.isValid():
            self['network_links_shape_file_path'] = ''
            self['network_links_shape_id'] = ''
            return False
            
        registry.addMapLayer(layer, False)
        group.insertLayer(0, layer)
        self['network_links_shape_file_path'] = layer.source()
        self['network_links_shape_id'] = layer.id()
        return True
        
    def load_network_nodes_shape_file(self, file_path):
        self.network_nodes_shape_path = file_path
        registry = QgsProject.instance()
        group = self.get_layers_group()
        layer = QgsVectorLayer(file_path[0], 'Network_Nodes', 'ogr')
        if not layer.isValid():
            self['network_nodes_shape_file_path'] = ''
            self['network_nodes_shape_id'] = ''
            return False
            
        registry.addMapLayer(layer, False)
        group.insertLayer(0, layer)
        self['network_nodes_shape_file_path'] = layer.source()
        self['network_nodes_shape_id'] = layer.id()
        return True
    
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
    
    def load_db_file(self, file_path):
        self.db_path = file_path
        self['db_path'] = self.db_path  
    
    def load_zones_centroids_data(self):
        """
            @summary: Loads centroids information from file
        """
        
        filePath = self.centroids_file_path[0:max(self.centroids_file_path.rfind('\\'), self.centroids_file_path.rfind('/'))]
        layer = QgsMapLayerRegistry.instance().mapLayersByName('Zonas_Centroids')[0]
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
#         QgsMapLayerRegistry.instance().addMapLayer( tripsMatrixLayer, False )
#         group.insertLayer(len(QgsMapLayerRegistry.instance().mapLayers())+1, tripsMatrixLayer)
    
    def load_zones_centroids(self):
        """
            @summary: Loads centroids file information from centroid layer and creates a csv file
        """
        
        layer = QgsMapLayerRegistry.instance().mapLayersByName('Zonas')[0]
        filePath = self.shape[0:max(self.shape.rfind('\\'), self.shape.rfind('/'))]
        group = self.get_layers_group()
        print (layer.name())
        
        if layer is not None:
            epsg = layer.crs().postgisSrid()
            uri = ("Point?crs=epsg:" + str(epsg) + "&field=zoneID:long&field=zoneName:string&field=posX:double&field=posY:double&index=yes").encode('utf-8')
            mem_layer = QgsVectorLayer(uri, layer.name() + '_Centroids', 'memory')
            prov = mem_layer.dataProvider()
            
            for f in layer.getFeatures():
                feat = QgsFeature()
                pt = f.geometry().centroid().asPoint()
                feat.setAttributes([f.attributes()[0], f.attributes()[1], pt.x(), pt.y()])
                feat.setGeometry(QgsGeometry.fromPoint(pt))
                prov.addFeatures([feat])
                
                zoneCentroid = ZoneCentroid()
                zoneCentroid.id = f.attributes()[0]
                zoneCentroid.name = f.attributes()[1]
                zoneCentroid.longitude = pt.x()
                zoneCentroid.latitude = pt.y()
                self.map_data.zoneCentroids.append(zoneCentroid)
            
            QgsMapLayerRegistry.instance().addMapLayer(mem_layer, False)
            group.insertLayer(len(QgsMapLayerRegistry.instance().mapLayers())+1, mem_layer)
            
            # Creates the Centroids CSV file
            self.map_data.create_zone_centroids_csv_file(filePath, layer.name())
            #self.map_data.create_trip_matrix_csv_file(filePath)
            
            #tripMatrixFileUri = ("file:///%s?crs=%s&delimiter=%s&wktField=%s" % (filePath + "/trips_map.csv", str(epsg), ",", "Geom")).encode('utf-8') 
            #tripsMatrixLayer = QgsVectorLayer(tripMatrixFileUri, layer.name() + '_trips_map', 'delimitedtext')
            
            ###
            ### This section loads style file to the layer
            ###
            #styleUri = ("file:///%s" % (filePath + "/Style.qlm")).encode('utf-8')
#             styleUri = (filePath + "/Style.qml").encode('utf-8')
#             tripsMatrixLayer.loadNamedStyle(styleUri)
#             tripsMatrixLayer.triggerRepaint()
#             QgsMapLayerRegistry.instance().addMapLayer(tripsMatrixLayer)
            
            ###
            ### This section manage the layer style
            ###
            #registry = QgsSymbolLayerV2Registry.instance()
            #lineMeta = registry.symbolLayerMetadata("SimpleLine")
            #markerMeta = registry.symbolLayerMetadata("MarkerLine")
            #symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
            #Line layer
            #lineLayer = lineMeta.createSymbolLayer({'width': '0.26', 'color': '255,0,0', 'offset': '0', 'penstyle': 'solid', 'use_custom_dash': '0', 'joinstyle': 'bevel', 'capstyle': 'square'})
            
            #Marker layer
            #markerLayer = markerMeta.createSymbolLayer({'width': '0.26', 'color': '255,0,0', 'rotate': '1', 'placement': 'centralpoint', 'offset': '0'})
            #subSymbol = markerLayer.subSymbol()
            #subSymbol.deleteSymbolLayer(0)
            #triangle = registry.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'filled_arrowhead', 'color': '255,0,0', 'color_border': '0,0,0', 'offset': '0,0', 'size': '3', 'angle': '0'})
            #subSymbol.appendSymbolLayer(triangle)
            
            #Replace the default layer with our two custom layers
            #symbol.deleteSymbolLayer(0)
            #symbol.appendSymbolLayer(lineLayer)
            #symbol.appendSymbolLayer(markerLayer)
            
            #Replace the renderer of the current layer
            #renderer = QgsSingleSymbolRendererV2(symbol)
            #tripsMatrixLayer.setRendererV2(renderer)
            
            #QgsMapLayerRegistry.instance().addMapLayer( tripsMatrixLayer, False )
            #group.insertLayer(len(QgsMapLayerRegistry.instance().mapLayers())+1, tripsMatrixLayer)

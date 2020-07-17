# -*- coding: utf-8 -*-
import numpy as np

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from qgis.core import  QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo, QgsLineSymbolLayer, QgsSimpleLineSymbolLayer, QgsMapUnitScale, QgsSimpleLineSymbolLayer, QgsLineSymbol, QgsMarkerLineSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsWkbTypes, QgsPoint, QgsFeatureRequest, QgsPointXY

from ..general.FileManagement import FileManagement as FileMXML
from ..general.Helpers import Helpers as HP
from ..GeneralObject import GeneralObject
from .NetworkDataAccess import NetworkDataAccess


class Network(object):
    def __init__(self):
        self.variables_dic = {}
        self.scenarios = []
        self.operators_dic = {}
        self.routes_dic = {}
        self.networ_matrices = []
        self.network_data_access = NetworkDataAccess()
        self.network_link_shape_location = None
        self.network_node_shape_location = None
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def __set_variables_dic(self):
        """
            @summary: Sets fields dictionary
        """
        self.variables_dic = self.network_data_access.get_variables_dic()

    def get_sorted_variables(self):
        """
            @summary: Method that gets variables sorted
            @return: Fields dictionary
        """
        if self.variables_dic is not None:
            return sorted(self.variables_dic.values())
        return None
    
    def get_operators(self):
        """
            @summary: Gets operators
        """
        if self.operators_dic is not None:
            return self.operators_dic.values()
        return None
    
    def get_operators_dictionary(self):
        """
            @summary: Gets operators dictionary
        """
        if self.operators_dic is not None:
            return self.operators_dic
        return None
    
    def get_routes(self):
        """
            @summary: Gets routes
        """
        if self.routes_dic is not None:
            return self.routes_dic.values()
        return None
    
    def get_routes_dictionary(self):
        """
            @summary: Gets routes dictionary
        """
        if self.routes_dic is not None:
            return self.routes_dic
        return None
    
    def load_dictionaries(self):
        """
            @summary: Loads dictionaries
        """
        self.__set_variables_dic()
        
    def load_network_scenarios(self, projectPath):
        """
            @summary: Loads zone shape
            @param shape: Path
            @type shape: String
        """
        self.scenarios = self.network_data_access.get_valid_network_scenarios(projectPath)
                
    def get_sorted_scenarios(self):
        """
            @summary: Gets sorted scenarios
        """
        if self.scenarios is not None:
            return sorted(self.scenarios)
        
    def load_operators(self, projectPath, scenario):
        """
            @summary: Loads operators
            @param projectPath: Project path
            @type projectPath: String
            @param scenario: Scenario
            @type scenario: String 
        """
        self.operators_dic = self.network_data_access.get_scenario_operators(projectPath, scenario)
                    
    def load_routes(self, projectPath, scenario):
        """
            @summary: Loads routes
            @param projectPath: Project path
            @type projectPath: String
            @param scenario: Scenario
            @type scenario: String
        """
        self.routes_dic = self.network_data_access.get_scenario_routes(projectPath, scenario)

    def addNetworkLayer(self, progressBar, layerName, scenariosExpression, networkExpression, variable, level, projectPath, group, networkLinkShapePath, method, expressionNetworkText, color):
        """
            @summary: Get operators dictionary
            @param layerName: Layer name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression
            @type networkExpression: Stack object
            @param variable: Variable to evaluate
            @type variable: String
            @param level: Level to evaluate (Total, Routes, Operators)
            @type level: Level object
            @param projectPath: Project path
            @type projectPath: String
            @param group: Project group
            @type group: Layer group
            @param networkLinkShapePath: Network link shape path
            @type networkLinkShapePath: String
            @return: Result of the layer creation
        """
        if scenariosExpression is None:
            QMessageBox.warning(None, "Network expression", "There is not scenarios information.")
            print  ("There is not scenarios information.")
            return False
        
        result, resultData, minValue, maxValue = self.network_data_access.create_network_memory(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        progressBar.setValue(15)
        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())

        if result:

            # Source shape, name of the new shape, providerLib
            layer = QgsVectorLayer(networkLinkShapePath, layerName+"_network", 'ogr')
            epsg = layer.crs().postgisSrid()
            intMethod = 0 if method == "Color" else 1
            progressBar.setValue(20)

            if not layer.isValid():
                return False

            feats = [ feat for feat in layer.getFeatures() ]

            # Create a vector layer with data on Memory 
            memoryLayer = QgsVectorLayer("LineString?crs=epsg:"+str(epsg), layerName+"_network", "memory")
            registry.addMapLayer(memoryLayer)
            memory_data = memoryLayer.dataProvider()
            joinedFieldName = "Result"
            shpField = "Id"
            attr = layer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName, QVariant.Double)]
            
            progressBar.setValue(25)

            memory_data.addAttributes(attr)
            memory_data.addFeatures(feats)
            memoryLayer.startEditing()
            
            num = 30
            progressBar.setValue(num)
            progressInterval = 70/len(resultData)

            for rowItem in np.nditer(resultData):
                value = 0
                num += progressInterval
                progressBar.setValue(num)

                it = memoryLayer.getFeatures( "LINKID  = '{0}'".format(str(rowItem['Id']).replace("b","").replace("'","")))
                for id_feature in it:
                    if rowItem['Result']=='Level A':
                        rowItem['Result'] = 1
                    elif rowItem['Result']=='Level B':
                        rowItem['Result'] = 2
                    elif rowItem['Result']=='Level C':
                        rowItem['Result'] = 3
                    elif rowItem['Result']=='Level D':
                        rowItem['Result'] = 4
                    elif rowItem['Result']=='Level E':
                        rowItem['Result'] = 5
                    elif rowItem['Result']=='Level F':
                        rowItem['Result'] = 6
                    elif rowItem['Result']=='Level G':
                        rowItem['Result'] = 7
                    elif rowItem['Result']=='Level H':
                        rowItem['Result'] = 8

                    memoryLayer.changeAttributeValue(id_feature.id(), memory_data.fieldNameIndex(joinedFieldName), QVariant(round(float(rowItem['Result']),2)))

            memoryLayer.commitChanges()
            
            rowCounter = len(resultData)
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
                interpolatedColors = HP.linear_gradient(color1, color2, nCats)
            
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                
                if method == "Color":
                    line = QgsSimpleLineSymbolLayer(QColor(interpolatedColors['r'][i], interpolatedColors['g'][i], interpolatedColors['b'][i]))
                    #line.setOffsetUnit(2)
                    line.setOffset(0.55)
                    #line.setWidthUnit(2)
                    line.setWidth(0.7)
                    symbol = QgsLineSymbol()
                    symbol.changeSymbolLayer(0,line)
                    myRange = QgsRendererRange(v0,v1, symbol, "")
                    
                elif method == "Size":
                    qcolor = QColor()
                    qcolor.setRgb(color)
                    line = QgsSimpleLineSymbolLayer(qcolor)
                    #line.setOffsetUnit(2)
                    line.setOffset(0.2)
                    #line.setWidthUnit(2)
                    #line.setWidth(1)

                    # Symbol
                    # symbolLine = QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.ArrowHead)
                    # Mark line
                    # markLine = QgsMarkerLineSymbolLayer()
                    # markLine.setPlacement(4)
                    symbolo = QgsLineSymbol()
                    symbolo.changeSymbolLayer(0,line)
                    # symbolo.appendSymbolLayer(line)
                    myRange = QgsRendererRange(v0,v1, symbolo, "")
                ranges.append(myRange)
                
            # The first parameter refers to the name of the field that contains the calculated value (expression) 
            modeRender = QgsGraduatedSymbolRenderer.Mode(2)
            renderer = QgsGraduatedSymbolRenderer(joinedFieldName, ranges)
            renderer.setMode(modeRender)
            
            if method == "Size":
                renderer.setSymbolSizes(0.200000, 2.60000)
            else:
                renderer.setSourceColorRamp(ramp)
            renderer.setGraduatedMethod(intMethod)
            #renderer.updateClasses(memoryLayer, modeRender, 8)
            memoryLayer.setRenderer(renderer)

            typeLayer = "network"
            networkExpressionText = str(scenariosExpression)

            # Create XML File ".qtranus" with the parameters of the executions
            if FileMXML.if_exist_xml_layers(projectPath):
                if FileMXML.if_exist_layer(projectPath, memoryLayer.id()):
                    FileMXML.update_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, variable, networkExpression, projectPath, expressionNetworkText, method, level, color)
                else:
                    FileMXML.add_layer_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, variable, networkExpression, projectPath, expressionNetworkText, shpField, typeLayer, method, level, color)
            else:
                FileMXML.create_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, variable, networkExpression, projectPath, expressionNetworkText, shpField, typeLayer, method, level, color)

            #group.insertLayer((layersCount+1), memoryLayer)
            progressBar.setValue(100)
        return True

    def loadNetworkLayer(self, layerName, scenariosExpression, networkExpression, variable, level, projectPath, networkLinkShapePath, method, color, layerId):
        """
            @summary: Get operators dictionary
            @param layerName: Layer name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression
            @type networkExpression: Stack object
            @param variable: Variable to evaluate
            @type variable: String
            @param level: Level to evaluate (Total, Routes, Operators)
            @type level: Level object
            @param projectPath: Project path
            @type projectPath: String
            @param group: Project group
            @type group: Layer group
            @param networkLinkShapePath: Network link shape path
            @type networkLinkShapePath: String
            @return: Result of the layer creation
        """
        if scenariosExpression is None:
            QMessageBox.warning(None, "Network expression", "There is not scenarios information.")
            print  ("There is not scenarios information.")
            return False
        
        result, resultData, minValue, maxValue = self.network_data_access.create_network_memory(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())

        if result:
            # Source shape, name of the new shape, providerLib
            layer = QgsVectorLayer(networkLinkShapePath, layerName+"_network", 'ogr')
            epsg = layer.crs().postgisSrid()
            intMethod = 0 if method == "Color" else 1

            if not layer.isValid():
                return False

            feats = [ feat for feat in layer.getFeatures() ]

            # Create a vector layer with data on Memory
            memoryLayer = registry.mapLayer(layerId) 
            memory_data = memoryLayer.dataProvider()
            joinedFieldName = "Result"
            shpField = "Id"

            attr = layer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName, QVariant.Double)]

            memory_data.addAttributes(attr)
            memory_data.addFeatures(feats)
            memoryLayer.startEditing()
            num = 30

            for rowItem in np.nditer(resultData):
                value = 0
                it = memoryLayer.getFeatures( "LINKID  = '{0}'".format(str(rowItem['Id']).replace("b","").replace("'","")))
                for id_feature in it:
                    memoryLayer.changeAttributeValue(id_feature.id(), memory_data.fieldNameIndex(joinedFieldName), QVariant(round(float(rowItem['Result']),2)))

            memoryLayer.commitChanges()
            
            rowCounter = len(resultData)
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
                interpolatedColors = HP.linear_gradient(color1, color2, nCats)
            
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                
                if method == "Color":
                    line = QgsSimpleLineSymbolLayer(QColor(interpolatedColors['r'][i], interpolatedColors['g'][i], interpolatedColors['b'][i]))
                    #line.setOffsetUnit(2)
                    line.setOffset(0.55)
                    #line.setWidthUnit(2)
                    line.setWidth(0.7)
                    symbol = QgsLineSymbol()
                    symbol.changeSymbolLayer(0,line)
                    myRange = QgsRendererRange(v0,v1, symbol, "")
                    
                elif method == "Size":
                    qcolor = QColor()
                    qcolor.setRgb(color)
                    line = QgsSimpleLineSymbolLayer(qcolor)
                    #line.setOffsetUnit(2)
                    line.setOffset(0.2)
                    #line.setWidthUnit(2)
                    #line.setWidth(1)

                    # Symbol
                    # symbolLine = QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.ArrowHead)
                    # Mark line
                    # markLine = QgsMarkerLineSymbolLayer()
                    # markLine.setPlacement(4)
                    symbolo = QgsLineSymbol()
                    symbolo.changeSymbolLayer(0,line)
                    # symbolo.appendSymbolLayer(line)
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
            memoryLayer.setRenderer(renderer)

        return True

    def editNetworkLayer(self, progressBar, layerName, scenariosExpression, networkExpression, variable, level, projectPath, group, networkLinkShapePath, method, layerId, expressionNetworkText, color):
        """
            @summary: Get operators dictionary
            @param layerName: Layer name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression
            @type networkExpression: Stack object
            @param variable: Variable to evaluate
            @type variable: String
            @param level: Level to evaluate (Total, Routes, Operators)
            @type level: Level object
            @param projectPath: Project path
            @type projectPath: String
            @param group: Project group
            @type group: Layer group
            @param networkLinkShapePath: Network link shape path
            @type networkLinkShapePath: String
            @return: Result of the layer creation
        """
        
        if scenariosExpression is None:
            QMessageBox.warning(None, "Network expression", "There is not scenarios information.")
            print  ("There is not scenarios information.")
            return False
        
        registry = QgsProject.instance()
        layersCount = len(registry.mapLayers())
        result, resultData, minValue, maxValue = self.network_data_access.create_network_memory(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        progressBar.setValue(15)

        if result:
            # Source shape, name of the new shape, providerLib
            layer = QgsVectorLayer(networkLinkShapePath, layerName+"_network", 'ogr')
            epsg = layer.crs().postgisSrid()
            intMethod = 0 if method == "Color" else 1
            rowCounter = len(resultData)

            if not layer.isValid():
                return False

            feats = [ feat for feat in layer.getFeatures() ]

            # Create a vector layer with data on Memory 
            memoryLayer = registry.mapLayer(layerId)

            memory_data = memoryLayer.dataProvider()
            joinedFieldName = "Result"
            shpField = "Id"
            attr = layer.dataProvider().fields().toList()
            attr += [QgsField(joinedFieldName, QVariant.Double)]
            progressBar.setValue(25)

            memory_data.addAttributes(attr)
            memory_data.addFeatures(feats)

            num = 30
            progressBar.setValue(num)
            progressInterval = 70/len(resultData)

            memoryLayer.startEditing()
            for rowItem in np.nditer(resultData):
                value = 0
                num += progressInterval
                progressBar.setValue(num)

                it = memoryLayer.getFeatures( "LINKID  = '{0}'".format(str(rowItem['Id']).replace("b","").replace("'","")))
                for id_feature in it:
                    memoryLayer.changeAttributeValue(id_feature.id(), memory_data.fieldNameIndex(joinedFieldName), QVariant(round(float(rowItem['Result']),2)))

            memoryLayer.commitChanges()
            
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
                interpolatedColors = HP.linear_gradient(color1, color2, nCats)
                
            for i in range(0,nCats):
                v0 = minValue + rng/float(nCats)*i
                v1 = minValue + rng/float(nCats)*(i+1)
                if method == "Color":
                    line = QgsSimpleLineSymbolLayer(QColor(interpolatedColors['r'][i], interpolatedColors['g'][i], interpolatedColors['b'][i]))
                    line.setOffsetUnit(2)
                    line.setOffset(2)
                    line.setWidth(0.8)
                    symbol = QgsLineSymbol()
                    symbol.changeSymbolLayer(0,line)
                    myRange = QgsRendererRange(v0,v1, symbol, "")
                    
                elif method == "Size":
                    qcolor = QColor()
                    qcolor.setRgb(color)
                    line = QgsSimpleLineSymbolLayer(qcolor)
                    line.setOffsetUnit(2)
                    line.setOffset(0.7)
                    # Symbol
                    # symbolLine = QgsSimpleMarkerSymbolLayer(QgsSimpleMarkerSymbolLayerBase.ArrowHead)
                    # Mark line
                    # markLine = QgsMarkerLineSymbolLayer()
                    # markLine.setPlacement(4)
                    symbolo = QgsLineSymbol()
                    symbolo.changeSymbolLayer(0,line)
                    # symbolo.appendSymbolLayer(line)
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
            memoryLayer.setRenderer(renderer)

            typeLayer = "network"
            fieldName = "LINKID"
            networkExpressionText = str(scenariosExpression)
            
            # Create XML File ".qtranus" with the parameters of the executions
            if FileMXML.if_exist_xml_layers(projectPath):
                if FileMXML.if_exist_layer(projectPath, memoryLayer.id()):
                    FileMXML.update_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, variable, networkExpression, projectPath, expressionNetworkText, method, level, color)
                else:
                    FileMXML.add_layer_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, variable, networkExpression, projectPath, expressionNetworkText, shpField, typeLayer, method, level, color)
            else:
                FileMXML.create_xml_file(memoryLayer.name(), memoryLayer.id(), scenariosExpression, variable, networkExpression, projectPath, expressionNetworkText, shpField, typeLayer, method, level, color)

            #group.insertLayer((layersCount+1), memoryLayer)
            progressBar.setValue(100)

        return True

    @staticmethod
    def addLinkFeatureShape(layerId, originPoint, destinationPoint, scenarioCode, linkId, name, fromNode, toNode, idType, length, direction, capacity, networkShapeFields=None):
        
        """
            @summary: Build link to Shape Network
            @param originPoint: Layer name
            @type originPoint: QgsPointXY
            @param destinationPoint: Layer name
            @type destinationPoint: QgsPointXY
            @param originIdNode: Origin Node
            @type originIdNode: Integer
            @destinationIdNode: Destination Node
            @type destinationIdNode: Integer
            @param twoWay: Flag to mark two-way links
            @type twoWay: Integer
            @return: Result of the layer creation
        """
        try:
            if not networkShapeFields:
                raise Exception("networkShapeFields is None")

            project = QgsProject.instance()
            layer = project.mapLayer(layerId)
            fields = [value.name() for value in layer.fields()]
            values = [None] * len(fields)
            
            values[fields.index(networkShapeFields['scenario'])] = scenarioCode
            values[fields.index(networkShapeFields['name'])] = name
            values[fields.index(networkShapeFields['id'])] = linkId
            values[fields.index(networkShapeFields['origin'])] = fromNode
            values[fields.index(networkShapeFields['destination'])] = toNode
            values[fields.index(networkShapeFields['type'])] = idType
            values[fields.index(networkShapeFields['length'])] = length
            values[fields.index(networkShapeFields['direction'])] = direction
            values[fields.index(networkShapeFields['capacity'])] = capacity

            layer.startEditing()

            geom = QgsGeometry()
            geom.addPoints([QgsPoint(originPoint), QgsPoint(destinationPoint)], QgsWkbTypes.LineGeometry)

            feat = QgsFeature()
            feat.setGeometry(geom)
            #feat.setAttributes([f'name',f'{originIdNode}-{destinationIdNode}', originIdNode, destinationIdNode])
            feat.setAttributes(values)

            layer.dataProvider().addFeature(feat)

            if direction:
                geom = QgsGeometry()
                geom.addPoints([QgsPoint(destinationPoint), QgsPoint(originPoint)], QgsWkbTypes.LineGeometry)
                values[fields.index(networkShapeFields['id'])] = f'{toNode}-{fromNode}'
                feat = QgsFeature()
                feat.setGeometry(geom)
                feat.setAttributes(values)            
                layer.dataProvider().addFeature(feat)

            layer.commitChanges()
            return True
        except:
            return False


    @staticmethod
    def updateLinkFeatureShape(layerId, scenarioCode, linkId, name, fromNode, toNode, idType, length, direction, capacity, networkShapeFields=None):
        
        """
            @summary: Build link to Shape Network
            @param originPoint: Layer name
            @type originPoint: QgsPointXY
            @param destinationPoint: Layer name
            @type destinationPoint: QgsPointXY
            @param originIdNode: Origin Node
            @type originIdNode: Integer
            @destinationIdNode: Destination Node
            @type destinationIdNode: Integer
            @param twoWay: Flag to mark two-way links
            @type twoWay: Integer
            @return: Result of the layer creation
        """
        try:
        
            if not networkShapeFields:
                return False
                raise Exception("networkShapeFields is None")

            project = QgsProject.instance()
            layer = project.mapLayer(layerId)
            fields = [value.name() for value in layer.fields()]
            values = [None] * len(fields)

            features = layer.getFeatures(QgsFeatureRequest().setFilterExpression(f"linkID = '{linkId}'"))
            features = list(features)

            layer.startEditing()
            #layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['scenario']), scenarioCode)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['name']), name)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['id']), linkId)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['origin']), fromNode)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['destination']), toNode)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['type']), idType)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['length']), length)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['direction']), direction)
            layer.changeAttributeValue(features[0].id(), fields.index(networkShapeFields['capacity']), capacity)
            layer.commitChanges()

            return True
        except:
            return False


    @staticmethod
    def deleteLinkFeatureShape(layerId, scenarioCode, linkId, networkShapeFields=None):
        
        """
            @summary: Build link to Shape Network
            @param originPoint: Layer name
            @type originPoint: QgsPointXY
            @param destinationPoint: Layer name
            @type destinationPoint: QgsPointXY
            @param originIdNode: Origin Node
            @type originIdNode: Integer
            @destinationIdNode: Destination Node
            @type destinationIdNode: Integer
            @param twoWay: Flag to mark two-way links
            @type twoWay: Integer
            @return: Result of the layer creation
        """
        try:

            project = QgsProject.instance()
            layer = project.mapLayer(layerId)
            fields = [value.name() for value in layer.fields()]
            values = [None] * len(fields)

            features = layer.getFeatures(QgsFeatureRequest().setFilterExpression(f"{networkShapeFields['id']} = '{linkId}'"))
            feature = list(features)

            layer.startEditing()
            result = layer.dataProvider().deleteFeatures([feature[0].id()])
            layer.commitChanges()
            
            if result:
                return True
            else:
                return False    
        except:
            return False

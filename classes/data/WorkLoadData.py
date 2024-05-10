    # -*- coding: utf-8 -*-
import os, re, webbrowser, time
from string import *
import threading

from PyQt5.QtCore import *
from PyQt5.QtCore import QThread, pyqtSignal

from qgis.core import QgsVectorLayer

class WorkerSyncThread(QThread):
    error_signal = pyqtSignal(str)
    loading_signal = pyqtSignal(dict)
    
    def __init__(self, zones_params, nodes_params, links_params, dataBaseSqlite, parent=None):
        super(WorkerSyncThread, self).__init__(parent)
        
        self.dataBaseSqlite = dataBaseSqlite
        self.shape = zones_params['shape']
        self.zones_shape_id = zones_params['zones_id']
        self.zones_shape_name = zones_params['zones_name']

        self.shape_nodes = nodes_params['shape_nodes']
        self.idNode = nodes_params['idNode']
        self.typeNode = nodes_params['typeNode']
        self.nameNode = nodes_params['nameNode']
        self.xNode = nodes_params['xNode']
        self.yNode = nodes_params['yNode']

        self.links_scenario = links_params['scenario']
        self.links_origin = links_params['origin']
        self.links_destination = links_params['destination']
        self.links_id = links_params['id']
        self.links_name = links_params['name']
        self.links_type = links_params['type']
        self.links_length = links_params['length']
        self.links_direction = links_params['direction']
        self.links_capacity = links_params['capacity']
        self.links_shape = links_params['links_shape']
        

    def run(self):
        layer = QgsVectorLayer(self.shape, 'Zonas', 'ogr')
        nodes_layer = QgsVectorLayer(self.shape_nodes, 'Network_Nodes', 'ogr')
        layer_network = QgsVectorLayer(self.links_shape, 'Network_Links', 'ogr')
        typeSql ='IGNORE'
        try:
            if not layer.isValid():
                self.error_signal.emit("Layer Zones is invalid")
                return False
            else:
                # Loading Zones
                self.loading_signal.emit(dict(type='zones', status=True))
                zones_shape_fields = [field.name() for field in layer.fields()]
                features = layer.getFeatures()
                result_a = self.dataBaseSqlite.selectAll('zone', " where id = 0")
                if len(result_a)==0:
                    self.dataBaseSqlite.addZone(0, 'Global Increments')
                data_list = []

                zoneIdField = self.zones_shape_id
                zoneNameField = self.zones_shape_name
                for feature in features:
                    zoneId = feature.attribute(zoneIdField)
                    zoneName = feature.attribute(zoneNameField)[0:25] if feature.attribute(zoneNameField) else None
                    zoneName = re.sub(r'[^A-Za-z0-9 .]', '', zoneName)
                    result = self.dataBaseSqlite.selectAll('zone', " where id = {}".format(zoneId))
                    if typeSql == 'IGNORE':
                        if not (isinstance(zoneId, QVariant) and zoneId.isNull()):
                            if re.findall(r'\d+',str(zoneId)):
                                if len(result) == 0:
                                    data_list.append((zoneId, zoneName))
                            else:
                                raise ExceptionFormatID(zoneId, typeFile='Import error in Zone shape file')
                    elif typeSql == 'REPLACE':
                        if re.findall(r'\d+',str(zoneId)):
                            data_list.append((zoneId, zoneName))
                        #else:
                        #    raise ExceptionFormatID(zoneId, typeFile='Import error in Zone shape file')                     
                self.dataBaseSqlite.addZoneFFShape(data_list, typeSql=typeSql)
                self.loading_signal.emit(dict(type='zones', status=False))
            
            # Loading Nodes
            if not nodes_layer.isValid():
                self.error_signal.emit("Layer Nodes is invalid")
                return False
            else:
                self.loading_signal.emit(dict(type='nodes', status=True))
                layer = QgsVectorLayer(self.shape_nodes, 'Network_Nodes', 'ogr')
                result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
               
                if result:
                    scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])
                    if not layer.isValid():
                        self.error_signal.emit("Layer Nodes is invalid")
                        return False
                    else:
                        network_shape_fields = [field.name() for field in layer.fields()]
                        features = layer.getFeatures()
                        idNode = self.idNode
                        typeNode = self.typeNode
                        nameNode = self.nameNode
                        xNode = self.xNode
                        yNode = self.yNode

                        data_list = []
                        for feature in features:
                            _id = feature.attribute(idNode) if idNode else None
                            if not (isinstance(_id, QVariant) and _id.isNull()): 
                                if re.findall(r'\d+',str(_id)):
                                    id_type = feature.attribute(typeNode) if typeNode else None
                                    name = feature.attribute(nameNode) if nameNode else None
                                    name = None if str(name) == 'NULL' else name
                                    description = None
                                    x = feature.attribute(xNode) if xNode else None
                                    y = feature.attribute(yNode) if yNode else None
                                    x = None if str(x) == 'NULL' else x
                                    y = None if str(y) == 'NULL' else y
                                    
                                    if not isinstance(_id, int):
                                        self.error_signal.emit(f"Loading Nodes error Id:{_id} wrong type")
                                    
                                    if not isinstance(id_type, int):
                                        self.error_signal.emit(f"Loading Nodes error Id:{_id} wrong type")
                                    
                                    if x == None:
                                        self.error_signal.emit(f"Loading Nodes error Id:{_id} field: {xNode} is null")

                                    if y == None:
                                        self.error_signal.emit(f"Loading Nodes error Id:{_id} field: {yNode} is null")
                                    
                                    data_list.append((_id, x, y, name, description, id_type))
                                    
                                else:
                                    self.error_signal.emit(f"Import error in Nodes shape file: Wrong id format {_id} ")
                        self.dataBaseSqlite.addNodeFShape(scenarios_arr, data_list, typeSql=typeSql)
                        self.loading_signal.emit(dict(type='nodes', status=False))
            
            # Loading Links
            result = self.dataBaseSqlite.selectAll(' scenario ', where=" where cod_previous = ''", columns=' code ')
            scenarios_arr = self.dataBaseSqlite.selectAllScenarios(result[0][0])
            
            if not layer_network.isValid():
                self.error_signal.emit("Layer Links is invalid")
                return False
            else:
                self.loading_signal.emit(dict(type='links', status=True))
                network_shape_fields = [field.name() for field in layer_network.fields()]
                features = layer.getFeatures()
                data_list = []
                for feature in layer_network.getFeatures():
                    scenarioField = self.links_scenario
                    linkIdField = self.links_id
                    linkNameField = self.links_name
                    typeField = self.links_type
                    lengthField = self.links_length
                    directionField = self.links_direction
                    capacityField = self.links_capacity
                    
                    linkId = feature.attribute(linkIdField) if linkIdField != 'Select' else '0-0'
                    # print(linkId.typeName())
                    if not (isinstance(linkId, QVariant) and linkId.isNull()): 
                        if re.findall(r'\d+-\d+',linkId):
                            
                            Or_node = linkId.split('-')[0]
                            Des_node = linkId.split('-')[1]
                            name = feature.attribute(linkNameField) if linkNameField != 'Select' else None
                            codScenario = feature.attribute(scenarioField) if scenarioField != 'Select' else None
                            idType = feature.attribute(typeField) if typeField != 'Select' else None
                            #two_way = 1 if (feature.attribute(directionField) if directionField != 'Select' else None)  == 0 else None
                            two_way = feature.attribute(directionField) if directionField != 'Select' else None 
                            length = feature.attribute(lengthField) if lengthField != 'Select' else None
                            capacity = feature.attribute(capacityField) if capacityField != 'Select' else None

                            # Optional parameter
                            codScenario = None if isinstance(codScenario, QVariant) else codScenario
                            name = None if isinstance(name, QVariant) and name.isNull() else name
                            resultOrNode = self.dataBaseSqlite.selectAll(" node ", where=f" where id = {Or_node}")
                            resultDesNode = self.dataBaseSqlite.selectAll(" node ", where=f" where id = {Des_node}")
                            name = None if isinstance(name, QVariant) else name
                            idType = None if isinstance(idType, QVariant) else idType
                            length = None if isinstance(length, QVariant) else length
                            two_way = None if isinstance(two_way, QVariant) else two_way
                            capacity = None if isinstance(capacity, QVariant) else capacity
                            if resultOrNode and resultDesNode:
                                data_list.append((codScenario, f"{Or_node}-{Des_node}", Or_node, Des_node, idType, length, two_way, capacity, name))
                                if two_way != None:
                                    data_list.append((codScenario, f"{Des_node}-{Or_node}", Des_node, Or_node, idType, length, two_way, capacity, name))
                            
                        else:
                            self.error_signal.emit(f"Invalid layer id {linkId}")             
                qry = """select 
                        distinct b.code, linkid, node_from, node_to, id_linktype, length, two_way, capacity, a.name
                        from link a
                        join scenario b on (a.id_scenario = b.id)"""

                result = self.dataBaseSqlite.executeSql(qry)
        
                # result: database data
                # data_list: network shape file data
                resultList = Helpers.union_elements_by_column(result, data_list)

                if typeSql=='REPLACE':
                    # self.dataBaseSqlite.executeDML('delete from link')
                    resultList = data_list

                self.dataBaseSqlite.addLinkFFShape(scenarios_arr, resultList, typeSql=typeSql)
                self.loading_signal.emit(dict(type='links', status=False))
                return True
            
        except Exception as e:
            print(e)
            self.error_signal.emit(" has happend")
from ..general.FileManagement import FileManagement
from ..GeneralObject import GeneralObject
from NetworkDataAccess import NetworkDataAccess
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsVectorJoinInfo
import numpy as np

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
        if self.operators_dic is not None:
            return self.operators_dic.values()
        return None
    
    def get_operators_dictionary(self):
        if self.operators_dic is not None:
            return self.operators_dic
        return None
    
    def get_routes(self):
        if self.routes_dic is not None:
            return self.routes_dic.values()
        return None
    
    def get_routes_dictionary(self):
        if self.routes_dic is not None:
            return self.routes_dic
        return None
    
    def load_dictionaries(self):
        self.__set_variables_dic()
        
    def load_network_scenarios(self, projectPath):
        """
            @summary: Loads zone shape
            @param shape: Path
            @type shape: String
        """
        self.scenarios = self.network_data_access.get_valid_network_scenarios(projectPath)
                
    def get_sorted_scenarios(self):
        if self.scenarios is not None:
            return sorted(self.scenarios)
        
    def load_operators(self, projectPath, scenario):
        
        self.operators_dic = self.network_data_access.get_scenario_operators(projectPath, scenario)
                    
    def load_routes(self, projectPath, scenario):
        
        self.routes_dic = self.network_data_access.get_scenario_routes(projectPath, scenario)

    def addNetworkLayer(self, layerName, scenariosExpression, networkExpression, variable, level, projectPath, group, networkLinkShapePath):
        if scenariosExpression is None:
            QMessageBox.warning(None, "Network expression", "There is not scenarios information.")
            print  ("There is not scenarios information.")
            return False
        
        result = self.network_data_access.create_network_csv_file(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        if result:
            registry = QgsMapLayerRegistry.instance()
            layersCount = len(registry.mapLayers())

            # Source shape, name of the new shape, providerLib
            layer = QgsVectorLayer(networkLinkShapePath, layerName, 'ogr')
            
            
            registry.addMapLayer(layer, False)
            if not layer.isValid():
                self['network_links_shape_file_path'] = ''
                self['network_links_shape_id'] = ''
                return False
            csvFile_uri = ("file:///" + projectPath + "/network_data.csv?delimiter=,").encode('utf-8')
            print(csvFile_uri)
            csvFile = QgsVectorLayer(csvFile_uri, layerName, "delimitedtext")
            registry.addMapLayer(csvFile, False)
            shpField = 'LinkId'
            csvField = 'Id'
            joinObject = QgsVectorJoinInfo()
            joinObject.joinLayerId = csvFile.id()
            joinObject.joinFieldName = csvField
            joinObject.targetFieldName = shpField
            joinObject.memoryCache = True
            layer.addJoin(joinObject)

            group.insertLayer((layersCount+1), layer)

        return True
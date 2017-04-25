from ..general.FileManagement import FileManagement
from ..GeneralObject import GeneralObject
import numpy as np

class Network(object):
    def __init__(self):
        self.variables_dic = {}
        self.scenarios = []
        self.operators_dic = {}
        self.routes_dic = {}
        self.networ_matrices = []
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def __set_variables_dic(self):
        """
            @summary: Sets fields dictionary
        """
        self.variables_dic = {0:"StVeh/Cap", 1:"StVeh", 2:"TotVeh", 3:"ServLev", 4:"Demand", 5:"Dem/Cap", 6:"FinSpeed", 7:"FinWait", 8:"Energy" }
        #self.data_fields_dic = {0:"Dem/Cap", 1:"StVeh", 2:"TotVeh", 3:"ServLev", 4:"Capac", 5:"Demand", 6:"Vehics", 7:"Dem/Cap", 8:"StVeh", 9:"IniSpeed", 10:"FinSpeed", 11:"IniWait", 12:"FinWait", 13:"Energy" }

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

        self.scenarios = FileManagement.get_scenarios_from_filename(projectPath, 'Assignment_SWN(.*)', '\..*')
                
    def get_sorted_scenarios(self):
        if self.scenarios is not None:
            return sorted(self.scenarios)
        
    def load_operators(self, projectPath, scenario):
        operatorsMatrix = None
        networkMatrix = FileManagement.get_np_matrix_from_csv(projectPath, 'Assignment_SWN', scenario, '\..*') 
        if networkMatrix is not None:
            if networkMatrix.data_matrix.size > 0:
                operatorsMatrix = np.unique(networkMatrix.data_matrix[['OperId', 'OperName']])
                operatorsMatrix.sort(order='OperId')
                
                for item in np.nditer(operatorsMatrix):
                    self.operators_dic[item.item(0)[0]] = item.item(0)[1]
                    
    def load_routes(self, projectPath, scenario):
        routesMatrix = None
        networkMatrix = FileManagement.get_np_matrix_from_csv(projectPath, 'Assignment_SWN', scenario, '\..*') 
        if networkMatrix is not None:
            if networkMatrix.data_matrix.size > 0:
                routesMatrix = np.unique(networkMatrix.data_matrix[['RouteId', 'RouteName']])
                routesMatrix.sort(order='RouteId')
                
                for item in np.nditer(routesMatrix):
                    self.routes_dic[item.item(0)[0]] = item.item(0)[1]

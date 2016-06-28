from Indicator import Indicator
from _ast import operator

class MapData(object):
    def __init__(self):
        self.indicators = Indicator()
        self.scenarios_dic = {}
        self.sectors_dic = {}
        self.data_fields_dic = None
    
    def __del__(self):
        print (self.__class__.__name__, "destroyed")
        
    def __set_scenarios(self):
        if self.indicators is not None:
            if self.indicators.scenarios is not None:
                for scenario in self.indicators.scenarios:
                    self.scenarios_dic[scenario.id] = scenario.name

    def __set_sectors(self):
        if self.indicators is not None:
            if self.indicators.scenarios is not None:
                scenario = self.indicators.scenarios[0]
                if scenario.sectors is not None: 
                    for sector in scenario.sectors:
                        self.sectors_dic[sector.id] = sector.name

    def __set_data_fields(self):
        self.data_fields_dic = {0:"TotProd", 1:"TotDem", 2:"ProdCost", 3:"Price", 4:"MinRes", 5:"MaxRes", 6:"Adjust" }

    def get_sorted_scenarios(self):
        if self.scenarios_dic is not None:
            return sorted(self.scenarios_dic.values())
        return None
        
    def get_sorted_sectors(self):
        if self.sectors_dic is not None:
            return sorted(self.sectors_dic.values())
        return None
        
    def get_sorted_fields(self):
        if self.data_fields_dic is not None:
            return sorted(self.data_fields_dic.values())
        return None

    def load_dictionaries(self):
        self.__set_scenarios()
        self.__set_sectors()
        self.__set_data_fields()
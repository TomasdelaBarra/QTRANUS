from Indicator import Indicator
from _ast import operator

import csv
from lib2to3.fixer_util import Newline
from asyncore import write

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
    
    """ Create a csv file to be used in the new layer """
    def create_csv_file(self, layerName, expression, scenario, fieldName, filePath):
        newField = ''
        minValue = 1e100
        maxValue = -1e100
        rowCounter = 0
        
        selectedScenario = next((sc for sc in self.indicators.scenarios if sc.id == scenario), None)
        if selectedScenario is None: 
            print ("The scenario {0} doesn't exist.".format(scenario))
            return False
 
        selectedSector = next((se for se in selectedScenario.sectors if se.name == expression), None)
        if selectedSector is None:
            print ("The sector {0} doesn't exist in the scenario {1}.".format(expression, scenario))
            return False
        else:
            rowCounter = len(selectedSector.zones) 
            
        if fieldName.upper() == 'TOTPROD':
            newField = 'TotProd'
        if fieldName.upper() == 'TOTDEM':
            newField = 'TotDem'
        if fieldName.upper() == 'PRODCOST':
            newField = 'ProdCost'
        if fieldName.upper() == 'PRICE':
            newField = 'Price'
        if fieldName.upper() == 'MINRES':
            newField = 'MinRes'
        if fieldName.upper() == 'MAXRES':
            newField = 'MaxRes'
        if fieldName.upper() == 'ADJUST':
            newField = 'Adjust'
        
        if newField == '':
            print ("The field selected doesn't exist.")
            
        csvFile = open(filePath + "\\" + layerName + ".csv", "wb")
        newFile = csv.writer(csvFile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
        print ('Writing CSV File "{0}"'.format(layerName))
        
        # Write header
        newFile.writerow(["ZoneId", "\tZoneName", "\t" + newField])
        for itemZone in selectedSector.zones:
            value = 0
            if newField.upper() == 'TOTPROD':
                value = float(itemZone.totProd)
            if newField.upper() == 'TOTDEM':
                value = float(itemZone.totDem)
            if newField.upper() == 'PRODCOST':
                value = float(itemZone.prodCost)
            if newField.upper() == 'PRICE':
                value = float(itemZone.price)
            if newField.upper() == 'MINRES':
                value = float(itemZone.minRes)
            if newField.upper() == 'MAXRES':
                value = float(itemZone.maxRes)
            if newField.upper() == 'ADJUST':
                value = float(itemZone.adjust)
        
            minValue = min(minValue, value)
            maxValue = max(maxValue, value)
        
            newFile.writerow([itemZone.id, "\t" + itemZone.name, "\t" + str(value)])
        
        del newFile, itemZone
        csvFile.close()
        del csvFile
        
        return True, minValue, maxValue, rowCounter
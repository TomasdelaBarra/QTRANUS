from Indicator import Indicator
from ExpressionData import ExpressionData

import csv

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
    def create_csv_file(self, layerName, expression, scenario, fieldName, filePath, stackOfExpression):
        newField = ''
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        
        selectedScenario = next((sc for sc in self.indicators.scenarios if sc.id == scenario), None)
        if selectedScenario is None:
            print ("The scenario {0} doesn't exist.".format(scenario))
            return False, 0, 0, 0
 
        if stackOfExpression is None:
            print ("There is no expression to evaluate.")
            return False, 0, 0, 0
        
        operand1 = None
        operand2 = None
        zoneList = None 
        stackLen = len(stackOfExpression.data)
        for item in stackOfExpression.data:
            if ExpressionData.is_operator(item):
                zoneList = ExpressionData.execute_expression(operand1, operand2, item, fieldName)
                operand1 = zoneList
                operand2 = None
            else:
                selectedSector = next((se for se in selectedScenario.sectors if se.name == item), None)
                if selectedSector is None:
                    print ("The sector {0} doesn't exist in the scenario {1}.".format(item, scenario))
                    return False, 0, 0, 0
                else:
                    rowCounter = len(selectedSector.zones)
                    if stackLen == 1:
                        zoneList =  selectedSector.zones
                    else:
                        if operand1 is None:
                            operand1 = selectedSector.zones
                        else:
                            if operand2 is None:
                                operand2 = selectedSector.zones
        
        if zoneList is None:
            print ("There was not data to evaluate.")
            return False, 0, 0, 0
        else:
            del operand1
            del operand2
            
        csvFile = open(filePath + "\\" + layerName + ".csv", "wb")
        newFile = csv.writer(csvFile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
        print ('Writing CSV File "{0}"'.format(layerName))
        
        # Write header
        newFile.writerow(["ZoneId", "\tZoneName", "\tJoinField" + fieldName])
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

            newFile.writerow([itemZone.id, "\t" + itemZone.name, "\t" + str(value)])
        
        del newFile, itemZone
        csvFile.close()
        del csvFile
        print("Min: {0}, Max: {1}, Counter: {2}").format(minValue, maxValue, rowCounter)
        return True, minValue, maxValue, rowCounter
# -*- coding: utf-8 -*-
from .Indicator import Indicator
from .ExpressionData import ExpressionData
from .Stack import Stack
from .general.QTranusMessageBox import QTranusMessageBox
from PyQt5 import QtWidgets

import csv, numpy as np, sys

class MapData(object):
    def __init__(self):
        """
            @summary: Constructor
        """
        self.indicators = Indicator()
        self.scenarios_dic = {}
        self.sectors_dic = {}
        self.data_fields_dic = None
        self.matrix_zones_dic = {}
        self.matrix_categories_dic = {}
        self.trip_matrices = []
        self.zoneCentroids = []
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def __set_scenarios(self):
        """
            @summary: Sets the scenarios dictionary
        """
        if self.indicators is not None:
            if self.indicators.scenarios is not None:
                for scenario in self.indicators.scenarios:
                    self.scenarios_dic[scenario.id] = scenario.name

    def __set_sectors(self):
        """
            @summary: Sets sectors dictionary  
        """
        if self.indicators is not None:
            if self.indicators.scenarios is not None:
                if len(self.indicators.scenarios) > 0:
                    scenario = self.indicators.scenarios[0]
                    if scenario.sectors is not None:
                        for sector in scenario.sectors:
                            self.sectors_dic[int(sector.id)] = sector.name

    def __set_data_fields(self):
        """
            @summary: Sets fields dictionary 
        """
        self.data_fields_dic = {0:"TotProd", 1:"TotDem", 2:"ProdCost", 3:"Price", 4:"MinRes", 5:"MaxRes", 6:"Adjust" }

    def get_sorted_scenarios(self):
        """
            @summary: Method that gets the scenarios sorted
            @return: Scenarios dictionary
        """
        if self.scenarios_dic is not None:
            return sorted(self.scenarios_dic.values())
        return None
        
    def get_sorted_sectors(self):
        """
            @summary: Method that gets the sectors sorted
            @return: Sectors dictionary
        """
        if self.sectors_dic is not None:
            return sorted(self.sectors_dic.values())
        return None
        
    def get_sorted_fields(self):
        """
            @summary: Method that gets fields sorted
            @return: Fields dictionary 
        """
        if self.data_fields_dic is not None:
            return sorted(self.data_fields_dic.values())
        return None

    def load_dictionaries(self):
        """
            @summary: Loads dictionaries 
        """
        self.__set_scenarios()
        self.__set_sectors()
        self.__set_data_fields()
    
    def get_sector_zones(self, scenario, sectorName):
        """
            @summary: Method that gets sector zones
            @param scenario: Scenario that contains the list of sector 
            @type scenario: Scenario object
            @param sectorName: Sector that contains the list of zones
            @type sectorName: String   
            @return: Zones list object
        """
        zoneList = None
        selectedSector = next((se for se in scenario.sectors if se.name == sectorName), None)
        if selectedSector is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Sector selected", ("The sector {0} doesn't exist in the scenario {1}.").format(sectorName, scenario.name), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("The sector {0} doesn't exist in the scenario {1}.").format(sectorName, scenario.name)
        else:
            zoneList =  selectedSector.zones
            
        return zoneList    
    
    def get_matrix_zones(self):
        if self.matrix_zones_dic is not None:
            return (self.matrix_zones_dic.values())
        return None
    
    def get_matrix_categories(self):
        if self.matrix_categories_dic is not None:
            return (self.matrix_categories_dic.values())
        return None
    
    def evaluate_sectors_expression(self, scenario, fieldName, sectorsExpression, conditionalFlag):
        """
            @summary: Method that evaluates sectors expression
            @param scenario: Scenario where the expression will be evaluated
            @type scenario: String
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @param sectorsExpression: Sectors expression to be evaluated for each scenario
            @type sectorsExpression: Stack object
            @param condtionalFlag: Flag to determine when a conditional will be evaluated
            @type conditionalFlag: Boolean
            @return: Zones list object  
        """
        
        selectedScenario = next((sc for sc in self.indicators.scenarios if sc.id == scenario), None)
        if selectedScenario is None:
            QMessageBox.warning(None, "Scenario selected", "The scenario {0} doesn't exist.".format(scenario))
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Sector selected", "The scenario {0} doesn't exist.".format(scenario), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("The scenario {0} doesn't exist.".format(scenario))
            return None

        if sectorsExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Sector expression", "There is no expression to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is no expression to evaluate.")
            return None
        
        operand1 = None
        operand2 = None
        zoneList = None
        stackLen = len(sectorsExpression.data)
        operands = Stack()
        for item in sectorsExpression.data:
            if ExpressionData.is_operator(item) or ExpressionData.is_conditional(item):
                operand2 = operands.pop()
                if type(operand2) is not list:
                    if ExpressionData.is_number(operand2):
                        operand2 = float(operand2)
                    elif operand2.isalpha():
                        operand2 = self.get_sector_zones(selectedScenario, operand2)
                    
                operand1 = operands.pop()
                if type(operand1) is not list:
                    if ExpressionData.is_number(operand1):
                        operand1 = float(operand1)
                    elif operand1.isalpha():
                        operand1 = self.get_sector_zones(selectedScenario, operand1)
                
                zoneList = ExpressionData.execute_expression(operand1, operand2, item, fieldName)
                operands.push(zoneList)
                operand1 = None
                operand2 = None
            else:
                if ExpressionData.is_number(item):
                    item = float(item)
                    if stackLen == 1:
                        if conditionalFlag:
                            return item
                        else:
                            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Sector expression", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                            messagebox.exec_()
                            print ("There is not data to evaluate.")
                            return None
                    else:
                        operands.push(item)

                elif item.isalpha():
                    if stackLen == 1:
                        zoneList =  self.get_sector_zones(selectedScenario, item)
                    else:
                        operands.push(item)

                else:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Sector expression", "Item {0}, is not recognized.".format(item), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    print ("Item {0}, is not recognized.").format(item)
                    return None
                
        if zoneList is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Sector expression", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is not data to evaluate.")
            return None
        else:
            del operand1
            del operand2
            del operands
            return zoneList
    
    def evaluate_scenarios_expression(self, scenariosExpression, sectorsExpression, fieldName):
        """
            @summary: Method that evaluates scenarios expression
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param sectorsExpression: Sectors expression to be evaluated for each scenario
            @type sectorsExpression: Stack object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @return: Zones list object, result of scenarios evaluation 
        """
        operand1 = None
        operand2 = None
        zoneList = None
        
        try:
            stackLen = len(scenariosExpression.data)
            generalOperands = Stack()
            
            for item in scenariosExpression.data:
                if ExpressionData.is_operator(item):            
                    operand2 = generalOperands.pop()
                    operand2 = self.evaluate_sectors_expression(operand2, fieldName, sectorsExpression[0], False)
                    
                    operand1 = generalOperands.pop()
                    operand1 = self.evaluate_sectors_expression(operand1, fieldName, sectorsExpression[0], False)
                    
                    zoneList = ExpressionData.execute_expression(operand1, operand2, item, fieldName)
                    
                    if zoneList is None:
                        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "There is not data to evaluate for sectors expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                        messagebox.exec_()
                        raise Exception("There is not data to evaluate for sectors expression.")
                    else:
                        if len(zoneList) > 0:                
                            generalOperands.push(zoneList)
                        else:
                            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "There is not data to evaluate for sectors expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                            messagebox.exec_()
                            raise Exception("There is not data to evaluate for sectors expression.")
                    
                    operand1 = None
                    operand2 = None
                else:
                    if stackLen == 1:
                        zoneList = self.evaluate_sectors_expression(item, fieldName, sectorsExpression[0], False)
                    else:
                        generalOperands.push(item)
                        
        except Exception as inst:
            print(inst)
            zoneList = None
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            zoneList = None
        finally:
            del operand1
            del operand2
            del generalOperands
            
        return zoneList

    def evaluate_conditional_expression(self, scenariosExpression, generalSectorsExpression, fieldName):
        """
            @summary: Method that evaluates conditional expression
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param generalSectorsExpression: A list of sectors expression to be evaluated for each scenario
            @type generalSectorsExpression: List object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @return: Zones list object, result of conditional evaluation 
        """
        operand1 = None
        operand2 = None
        zoneList = None
        
        try:
            stackLen = len(scenariosExpression.data)
            generalOperands = Stack()
            
            for scenario in scenariosExpression.data:
                for sectorExpression in generalSectorsExpression:
                    if type(sectorExpression) is Stack:
                        generalOperands.push(sectorExpression)
                        
                    elif ExpressionData.is_conditional(sectorExpression):
                        operand2 = self.evaluate_sectors_expression(scenario, fieldName, generalOperands.pop(), True)
                        operand1 = self.evaluate_sectors_expression(scenario, fieldName, generalOperands.pop(), True)
                        
                        zoneList = ExpressionData.execute_expression(operand1, operand2, sectorExpression, fieldName)
                        
                        if zoneList is None:
                            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "There is not data to evaluate for conditional expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                            messagebox.exec_()
                            raise Exception("There is not data to evaluate for conditional expression.")
                        else:
                            if len(zoneList) > 0:                
                                generalOperands.push(zoneList)
                            else:
                                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "There is not data to evaluate for conditional expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                                messagebox.exec_()
                                raise Exception("There is not data to evaluate conditional expression.")
                        
                        operand1 = None
                        operand2 = None
                        
        except Exception as inst:
            print (inst)
            zoneList = None
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            zoneList = None
        finally:
            del operand1
            del operand2
            del generalOperands
            
        return zoneList
    
    def create_csv_file(self, layerName, scenariosExpression, fieldName, filePath, sectorsExpression):
        """
            @summary: Method that creates a csv file to be used in the new layer
            @param layerName: Layer name
            @type: layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @param filePath: Path to save the file
            @type filePath: String
            @param sectorsExpression: Expression to be evaluated in reverse polish notation
            @type sectorsExpression: Stack object    
            @return: Result of the file creation, minValue, maxValue, rowCounter 
        """
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        
        expressionsPreResult = Stack()
        
        if len(sectorsExpression) > 1:
            zoneList = self.evaluate_conditional_expression(scenariosExpression, sectorsExpression, fieldName)
        else:
            zoneList = self.evaluate_scenarios_expression(scenariosExpression, sectorsExpression, fieldName)
            

        if zoneList is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Zone data", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is not data to evaluate.")
            return False, minValue, maxValue, rowCounter
        else:
            rowCounter = len(zoneList)
            
        csvFile = open(filePath + "\\" + layerName + ".csv", "w")
        newFile = csv.writer(csvFile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
        print ('Writing CSV File "{0}"'.format(layerName.encode('utf-8')))

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
            # print("Write row value:"+str(value))
        
        del newFile, itemZone
        csvFile.close()
        del csvFile
        print("Min: {0}, Max: {1}, Counter: {2}".format(minValue, maxValue, rowCounter))
        return True, minValue, maxValue, rowCounter

    def create_data_memory(self, layerName, scenariosExpression, fieldName, filePath, sectorsExpression):
        """
            @summary: Method that creates a csv file to be used in the new layer
            @param layerName: Layer name
            @type: layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @param filePath: Path to save the file
            @type filePath: String
            @param sectorsExpression: Expression to be evaluated in reverse polish notation
            @type sectorsExpression: Stack object    
            @return: Result of the file creation, minValue, maxValue, rowCounter 
        """
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        
        expressionsPreResult = Stack()
        
        if len(sectorsExpression) > 1:
            zoneList = self.evaluate_conditional_expression(scenariosExpression, sectorsExpression, fieldName)
        else:
            zoneList = self.evaluate_scenarios_expression(scenariosExpression, sectorsExpression, fieldName)
            

        if zoneList is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Zone data", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is not data to evaluate.")
            return False, minValue, maxValue, rowCounter
        else:
            rowCounter = len(zoneList)
            
        #csvFile = open(filePath + "\\" + layerName + ".csv", "w")
        #newFile = csv.writer(csvFile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
        #print ('Writing CSV File "{0}"'.format(layerName.encode('utf-8')))

        # Write header
        #newFile.writerow(["ZoneId", "\tZoneName", "\tJoinField" + fieldName])
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

            # newFile.writerow([itemZone.id, "\t" + itemZone.name, "\t" + str(value)])
            # print("Write row value:"+str(value))
        
        #del newFile, itemZone
        #csvFile.close()
        #del csvFile
        print("Min: {0}, Max: {1}, Counter: {2}".format(minValue, maxValue, rowCounter))
        return True, minValue, maxValue, rowCounter, zoneList
    
    def load_matrix_zones(self):
        """
            @summary: Loads matrix zones and categories dictionaries
        """
        if self.trip_matrices is not None:
            if len(self.trip_matrices) > 0:
                temp_matrix = self.trip_matrices[0]
                if temp_matrix is not None:
                    if temp_matrix.tripMatrix.size > 0:
                        temp_zone = None
                        temp_cat = None
                        for item in np.nditer(temp_matrix.tripMatrix):
                            if temp_zone is None:
                                temp_zone = item.item(0)[0]
                                self.matrix_zones_dic[item.item(0)[0]] = item.item(0)[1]
                            else:
                                if temp_zone != item.item(0)[0]:
                                    temp_zone = item.item(0)[0]
                                    self.matrix_zones_dic[item.item(0)[0]] = item.item(0)[1]
                                    
                            if temp_cat is None:
                                temp_cat = item.item(0)[4]
                                self.matrix_categories_dic[item.item(0)[4]] = item.item(0)[5]
                            else:
                                if temp_cat != item.item(0)[4]:
                                    temp_cat = item.item(0)[4]
                                    self.matrix_categories_dic[item.item(0)[4]] = item.item(0)[5]
                                    
    def get_matrix_row(self, scenarioData, originZone, destZone, category, types):
        """
            @summary: Gets specific matrix row based on parameters
            @param scenarioData: Scenario name
            @type scenarioData: String
            @param originZone: Origin zone
            @type originZone: String
            @param destZone: Destination zone
            @type destZone: String
            @param category: Trip category
            @type category: String
            @param types: Ndarray types
            @type types: Ndarray dtypes object
            @return: Trip row 
        """
        
        rowData = None
        rowData = scenarioData.tripMatrix[
                                          (scenarioData.tripMatrix['OrZonName'] == originZone)
                                          &
                                          (scenarioData.tripMatrix['DeZonName'] == destZone)
                                          &
                                          (scenarioData.tripMatrix['CatName'] == category)
                                         ]
        
        if rowData is not None:
            if rowData.size == 0:
                for item in self.matrix_zones_dic:
                    if self.matrix_zones_dic[item] == originZone:
                        originZoneIndex = item
                
                for item in self.matrix_zones_dic:
                    if self.matrix_zones_dic[item] == destZone:
                        destZoneIndex = item
                
                for item in self.matrix_categories_dic:
                    if self.matrix_categories_dic[item] == category:
                        catIndex = item
                        
                rowData = np.array([(originZoneIndex, originZone, destZoneIndex, destZone, catIndex ,category, 0)], dtype = types)
        
        return rowData

    def evaluate_matrix_expression(self, scenario, originList, destinationList, matrixExpression, conditionalFlag):
        """
            @summary: Method that evaluates matrix expression
            @param scenario: Scenario where the expression will be evaluated
            @type scenario: String
            @param originList: List of origin zones
            @type originList: List object
            @param destinationList: List of destination zones
            @type destinationList: List object
            @param condtionalFlag: Flag to determine when a conditional will be evaluated
            @type conditionalFlag: Boolean
            @return: Matrix of trips
        """
        
        scenarioData = next((sc for sc in self.trip_matrices if sc.Id == scenario), None)
        if scenarioData is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenario selected", "The scenario {0} doesn't exist.".format(scenario), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("The scenario {0} doesn't exist.".format(scenario))
            return None
        
        if matrixExpression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is no expression to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is no expression to evaluate.")
            return None
            
        operand1 = None
        operand2 = None
        matrixExpressionData = None
        if type(matrixExpression) is list:
            stackLen = len(matrixExpression[0].data)
            matrixExpressionData = matrixExpression[0]
        if type(matrixExpression) is Stack:
            stackLen = len(matrixExpression.data)
            matrixExpressionData = matrixExpression
        operands = Stack()
        matrixData = None
        try:
            
            # Origin Zones
            for origin in originList:
                # Destination Zones
                for dest in destinationList:
                    if origin != dest:
                        # Matrix Expression
                        expCounter = 0
                        for item in matrixExpressionData.data:
                            expCounter +=1
                            if ExpressionData.is_operator(item) or ExpressionData.is_conditional(item):
                                operand2 = operands.pop()
                                if type(operand2)is not np.ndarray:
                                    if ExpressionData.is_number(operand2):
                                        operand2 = float(operand2)
                                    elif operand2.isalpha():
                                        operand2 = self.get_matrix_row(scenarioData, origin, dest, operand2, scenarioData.tripMatrix.dtype)
                                    
                                operand1 = operands.pop()
                                if type(operand1) is not np.ndarray:
                                    if ExpressionData.is_number(operand1):
                                        operand1 = float(operand1)
                                    elif operand1.isalpha():
                                        operand1 = self.get_matrix_row(scenarioData, origin, dest, operand1, scenarioData.tripMatrix.dtype)

                                rowData = ExpressionData.execute_matrix_expression(operand1, operand2, item, scenarioData.tripMatrix.dtype)

                                if rowData is not None:
                                    if expCounter < stackLen:
                                        operands.push(rowData)
                                    else:
                                        if matrixData is None:
                                            matrixData = rowData
                                        else:
                                            matrixData = np.concatenate((matrixData, rowData))
                                
                            else:
                                if ExpressionData.is_number(item):
                                    item = float(item)
                                    if stackLen == 1:
                                        if conditionalFlag:
                                            return item
                                        else:
                                            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                                            messagebox.exec_()
                                            print ("There is not data to evaluate.")
                                            return None
                                    else:
                                        operands.push(item)
                                
                                if item.isalpha():
                                    if stackLen == 1:
                                        rowData = self.get_matrix_row(scenarioData, origin, dest, item, scenarioData.tripMatrix.dtype)
                                        if matrixData is None:
                                             matrixData = rowData
                                        else:
                                             matrixData = np.concatenate((matrixData, rowData))
                                    else:
                                        operands.push(item)
                                        
                                else:
                                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "Item {0}, is not recognized.".format(item), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                                    messagebox.exec_()
                                    print ("Item {0}, is not recognized.").format(item)
                                    return None
                        
            
            if matrixData is None:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix expression", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()
                print ("There is not data to evaluate.")
                return None
            else:
                del operand1
                del operand2
                del operands
                return matrixData
        
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            matrixData = None
        
        return None
                    
    def evaluate_matrix_scenarios_expression(self, scenariosExpression, matrixExpression, originList, destinationList):
        """
            @summary: Method that evaluates matrix scenarios expression
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param matrixExpression: Matrix expression
            @type matrixExpression: Stack object
            @param originList: List of origin zones
            @type originList: List object
            @param destinationList: List of destination zones
            @type destinationList: List object
            @return: Matrix of trips
        """
        
        operand1 = None
        operand2 = None
        matrixData = None
        
        try:
            if self.trip_matrices is not None:
                if len(self.trip_matrices) > 0:
            
                    stackLen = len(scenariosExpression.data)
                    generalOperands = Stack()
                            
                    for item in scenariosExpression.data:
                        if ExpressionData.is_operator(item):
                            operand2 = generalOperands.pop()
                            operand2 = self.evaluate_matrix_expression(operand2, originList, destinationList, matrixExpression, False)
                            
                            operand1 = generalOperands.pop()
                            operand1 = self.evaluate_matrix_expression(operand1, originList, destinationList, matrixExpression, False)
                            
                            matrixData = ExpressionData.execute_matrix_expression(operand1, operand2, item, operand1.dtype)
                            
                            if matrixData is None:
                                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix scenarios expression", "There is not data to evaluate for matrix expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                                messagebox.exec_()
                                raise Exception("There is not data to evaluate for matrix expression.")
                            else:
                                if len(matrixData) > 0:
                                    generalOperands.push(matrixData)
                                else:
                                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix scenarios expression", "There is not data to evaluate for matrix expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                                    messagebox.exec_()
                                    raise Exception("There is not data to evaluate for matrix expression.")
                            
                            operand1 = None
                            operand2 = None
                            
                        else:
                            if stackLen == 1:
                                matrixData = self.evaluate_matrix_expression(item, originList, destinationList, matrixExpression, False)
                            else:
                                generalOperands.push(item)

        except Exception as inst:
            print(inst)
            matrixData = None
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Error", "Unexpected error: {0}".format(inst), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            matrixData = None
        finally:
            del operand1
            del operand2
            del generalOperands
            
        return matrixData
    
    def create_zone_centroids_csv_file(self, filePath, layerName):
        """
            @summary: Method that creates the centroids csv file
            @param filePath: Path of the file
            @type filePath: String
            @param layerName: Name of the new centroids layer
            @type layerName: String 
        """
        if self.zoneCentroids is not None:
            csvFile = open(filePath + "\\" + layerName + "_Centroids.csv", "wb")
            newFile = csv.writer(csvFile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
            newFile.writerow(["ZoneId", "\tZoneName", "\tPointX", "\tPointY"])
            for itemCentroid in self.zoneCentroids:
                newFile.writerow([itemCentroid.id, "\t" + itemCentroid.name, "\t" + str(itemCentroid.longitude), "\t" + str(itemCentroid.latitude)])
            
            del newFile, itemCentroid
            csvFile.close()
            del csvFile
            
        else:
            print('There is not Zone Centroids data to create Centroids CSV File.')
        
    def evaluate_conditional_matrix_expression(self, scenariosExpression, generalMatrixExpression, originZones, destinationZones):
        """
            @summary: Method that evaluates conditional expressions
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param generalMatrixExpression: Matrix expression to be evaluated
            @type generalMatrixExpression: Stack object
            @param originZones: List of origin zones
            @type originZones: List object
            @param destinationZones: List of destinations zones
            @type destinationZones: List object
            @return: Matrix of trips   
        """
        
        operand1 =  None
        operand2 =  None
        matrixData = None
        
        try:
            stackLen = len(scenariosExpression.data)
            generalOperands = Stack()
            
            for scenario in scenariosExpression.data:
                for matrixExpression in generalMatrixExpression:
                    if type(matrixExpression) is Stack:
                        generalOperands.push(matrixExpression)
                    
                    elif ExpressionData.is_conditional(matrixExpression):
                        operand2 = self.evaluate_matrix_expression(scenario, originZones, destinationZones, generalOperands.pop(), True)
                        operand1 = self.evaluate_matrix_expression(scenario, originZones, destinationZones, generalOperands.pop(), True)
                        
                        operandTypes = None
                        if operand2 is not None:
                            if type(operand2) is np.ndarray:
                                operandTypes = operand2.dtype
                            
                        if operand1 is not None and operandTypes is None:
                            if type(operand1) is np.ndarray:
                                operandTypes = operand1.dtype
                        
                        if operandTypes is None:
                            return None
                        
                        matrixData = ExpressionData.execute_matrix_expression(operand1, operand2, matrixExpression, operandTypes)
                        
                        if matrixData is None:
                            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios matrix expression", "There is not data to evaluate for conditional expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                            messagebox.exec_()
                            raise Exception("There is not data to evaluate for conditional expression.")
                        else:
                            if len(matrixData) > 0:                
                                generalOperands.push(matrixData)
                            else:
                                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios matrix expression", "There is not data to evaluate for conditional expression.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                                messagebox.exec_()
                                raise Exception("There is not data to evaluate conditional expression.")
                            
                        operand1 = None
                        operand2 = None
            
        except Exception as inst:
            print(inst)
            matrixData = None
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Scenarios matrix expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            matrixData = None
        finally:
            del operand1
            del operand2
            del generalOperands
            
        return matrixData

    def create_trip_matrix_csv_file(self, layerName, scenariosExpression, originZones, destinationZones, matrixExpression, projectPath):
        """
            @summary: Method that creates a csv file to be used in the new matrix layer
            @param layerName: Layer Name
            @type layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression : Stack object
            @param originZones: Origin zones list
            @type originZones: List object
            @param destinationZones: Destination zones list
            @type destinationZones: List object
            @param matrixExpression: Matrix expression to be evaluated in reverse polish notation
            @type matrixExpression: Stack object
            @param projectPath: Main project path
            @type projectPath: String
            @return: The boolean result of file creation
        """
        
        rowCounter = 0
        if len(matrixExpression) > 1:
            matrixResult = self.evaluate_conditional_matrix_expression(scenariosExpression, matrixExpression, originZones, destinationZones)
        else:
            matrixResult = self.evaluate_matrix_scenarios_expression(scenariosExpression, matrixExpression, originZones, destinationZones)
        
        if matrixResult is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Matrix data", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is not data to evaluate.")
            return False
                           
        csvFile = open(projectPath + "\\trips_map.csv", "wb")
        newFile = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        newFile.writerow(['OrZoneId_DestZoneId', 'Geom', 'Trip'])
        
        originZoneCentroid = None
        destinationZoneCentroid = None
        for trip in np.nditer(matrixResult):
            if originZoneCentroid is None:
                originZoneCentroid = next((c for c in self.zoneCentroids if c.id == trip.item(0)[0]))
            else:
                if originZoneCentroid != trip.item(0)[0]:
                    originZoneCentroid = next((c for c in self.zoneCentroids if c.id == trip.item(0)[0]))
                    
            if destinationZoneCentroid is None:
                destinationZoneCentroid = next((c for c in self.zoneCentroids if c.id == trip.item(0)[2]))
            else:
                if destinationZoneCentroid != trip.item(0)[2]:
                    destinationZoneCentroid = next((c for c in self.zoneCentroids if c.id == trip.item(0)[2]))
            if originZoneCentroid is not None and destinationZoneCentroid is not None:
                newFile.writerow([str(trip.item(0)[0]) + "_" + str(trip.item(0)[2]),  
                        "LINESTRING("
                        + str(originZoneCentroid.longitude) + " " + str(originZoneCentroid.latitude)
                        + ","
                        + str(destinationZoneCentroid.longitude) + " " + str(destinationZoneCentroid.latitude)
                        + ")", str(trip.item(0)[6]) if len(matrixResult.dtype.names)> 5 else str(trip.item(0)[4])])
                    
        del newFile
        csvFile.close
        del csvFile
        
        return True
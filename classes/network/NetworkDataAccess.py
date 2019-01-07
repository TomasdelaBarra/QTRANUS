# -*- coding: utf-8 -*-
from .Level import *
import csv, numpy as np

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import  QMessageBox 

from ..general.QTranusMessageBox import QTranusMessageBox
from ..general.FileManagement import FileManagement
from ..Stack import Stack
from ..ExpressionData import ExpressionData

class NetworkDataAccess(object):
    def __init__(self):
        """
            @summary: Class constructor
        """
        self.variables_dic = {}
        self.scenarios = []
        self.operators_dic = {}
        self.routes_dic = {}
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def get_variables_dic(self):
        """
            @summary: Returns variables dictionary
            @return: Dictionary
        """
        return {0:"StVeh/Cap", 1:"StVeh", 2:"TotVeh", 3:"ServLev", 4:"Demand", 5:"Dem/Cap", 6:"FinSpeed", 7:"FinWait", 8:"Energy" }
    
    def get_valid_network_scenarios(self, projectPath):
        """
            @summary: Gets scenarios from file
            @param projectPath: Project path
            @type projectPath: String
            @return: List of Scenarios
        """
        return FileManagement.get_scenarios_from_filename(projectPath, 'Assignment_SWN(.*)', '\..*')
    
    def get_scenario_operators(self, projectPath, scenario):
        """
            @summary: Gets operators from scenario provided
            @param projectPath: Project path
            @type projectPath: String
            @param scenario: File scenario
            @type scenario: String
            @return: Dictionary  
        """
        operatorsMatrix = None
        operators_dic = {}
        networkMatrix = FileManagement.get_np_matrix_from_csv(projectPath, 'Assignment_SWN', scenario, '\..*') 
        if networkMatrix is not None:
            if networkMatrix.data_matrix.size > 0:
                operatorsMatrix = np.unique(networkMatrix.data_matrix[['OperId', 'OperName']])
                operatorsMatrix.sort(order='OperId')
                 
                for item in np.nditer(operatorsMatrix):
                    operators_dic[item.item(0)[0]] = item.item(0)[1]
                    
        return operators_dic 
    
    def get_scenario_routes(self, projectPath, scenario):
        """
            @summary: Gets routes from scenario provided
            @param projectPath: Project path
            @type projectPath: String
            @param scenario: File scenario
            @type scenario: String
            @return: Dictionary
        """
        routesMatrix = None
        routes_dic = {}
        networkMatrix = FileManagement.get_np_matrix_from_csv(projectPath, 'Assignment_SWN', scenario, '\..*') 
        if networkMatrix is not None:
            if networkMatrix.data_matrix.size > 0:
                routesMatrix = np.unique(networkMatrix.data_matrix[['RouteId', 'RouteName']])
                routesMatrix.sort(order='RouteId')
                
                for item in np.nditer(routesMatrix):
                    routes_dic[item.item(0)[0]] = item.item(0)[1]
        
        return routes_dic
    
    def __get_scenario_data(self, scenario, projectPath):
        """
            @summary: Gets data from the scenario
            @param scenario: Scenario
            @type scenario: String
            @param projectPath: Project path
            @type projectPath: String
            @return: Network matrix and matrix of links
        """
        # IMPORTANTE OJO PARAMETRO CABLEADO
        networkMatrix = FileManagement.get_np_matrix_from_csv(projectPath, 'Assignment_SWN', scenario, '\..*')
        links = self.__get_network_ids(networkMatrix)
        
        return networkMatrix, links 
    
    def __get_network_ids(self, networkMatrix):
        """
            @summary: Gets pairs of origin and destination
            @param networkMatrix: Network matrix
            @type networkMatrix: Numpy array
            @return: Matrix of links
        """
        if networkMatrix is not None:
            if networkMatrix.data_matrix.size > 0:
                linksMatrix = np.unique(networkMatrix.data_matrix[['Id', 'Orig', 'Dest']])

                return linksMatrix
        
        return None
    
    def __merge_netword_ids(self, links1, links2):
        """
            @summary: Merges two numpy arrays
            @param links1: Numpy array of links
            @type links1: Numpy array object
            @param links2: Numpy array of links
            @type links2: Numpy array object
            @return: Matrix of links 
        """
        links = None
        if links1 is not None and links2 is not None:
            links1 = np.concatenate((links1, links2))
            links = np.unique(links1[['Id', 'Orig', 'Dest']])
        
        return links
    
    def __get_network_rows(self, origin, destination, networkMatrix):
        """
            @summary: Gets network matrix rows looking by origin, destination
            @param origin: Origin
            @type origin: String
            @param destination: Destination
            @type destination: String
            @param networkMatrix: Network matrix
            @type networkMatrix: Numpy array
            @return: Matrix rows
        """
        #print("Origin {} Dest {} networkMatrix {} ".format(networkMatrix['Orig'], networkMatrix['Dest'], networkMatrix))
        rowsData = None
        rowsData = networkMatrix[
                                  (networkMatrix['Orig'] == origin)
                                  &
                                  (networkMatrix['Dest'] == destination)
                                 ]
        if rowsData is not None:
            if rowsData.size > 0:
                return rowsData
        
        return rowsData
    
    def __get_processed_network_rows(self, origin, destination, networkMatrix):
        """
            @summary: Gets network matrix rows looking by origin, destination
            @param origin: Origin
            @type origin: String
            @param destination: Destination
            @type destination: String
            @param networkMatrix: Network matrix
            @type networkMatrix: Numpy array
            @return: Matrix rows
        """
        rowsData = None
        rowsData = networkMatrix[(networkMatrix['Id'] == str(origin) + '-' + str(destination))]
        if rowsData is not None:
            if rowsData.size > 0:
                return rowsData
        
        return rowsData
    
    def __get_network_rows_by_operator(self, operator, oriDestMatrix):
        """
            @summary: Gets network matrix rows from a pair origin-destination looking by operator
            @param operator: Operator
            @type operator: String
            @param oriDestMatrix: Network matrix filtered by origin and destination
            @type oriDestMatrix: Numpy array
            @return: Matrix rows
        """
        rowsData = None
        rowsData = oriDestMatrix[(oriDestMatrix['OperName'] == operator)]
        if rowsData is not None:
            if rowsData.size > 0:
                return rowsData
        
        return None
            
    def __get_network_rows_by_route(self, route, oriDestMatrix):
        """
            @summary: Gets network matrix rows from a pair origin-destination looking by operator
            @param route: Route
            @type route: String
            @param oriDestMatrix: Network matrix filtered by origin and destination
            @type oriDestMatrix: Numpy array
            @return: Matrix rows
        """
        rowsData = None
        rowsData = oriDestMatrix[(oriDestMatrix['RouteName'] == route)]
        if rowsData is not None:
            if rowsData.size > 0:
                return rowsData
            
        return None

    def __evaluate_variable(self, rowsData, variable):
        """
            @summary: Evaluates data depending on variable selected
            @param rowsData: Network matrix rows
            @type rowsData: Numpy array
            @param variable: Variable selected
            @type variable: String
            @return: Matrix row
        """
        rowData = None
        
        if rowsData is not None:
            if rowsData.size > 0:
                if variable == 'StVeh/Cap':
                    stVehSum = rowsData['StVeh'].sum(axis=0)
                    cap = rowsData['LinkCap'][0]
                    if np.isinf(cap):
                            result = 0
                    else:
                        cap = float(cap)
                        if cap == 0:
                            result = 0
                        else:
                            result = stVehSum / cap
                    resultType = rowsData[0]['StVeh'].dtype
                                 
                if variable == 'StVeh':
                    result = rowsData['StVeh'].sum(axis=0)
                    resultType = rowsData[0]['StVeh'].dtype
                 
                if variable == 'TotVeh':
                    result = rowsData['Vehics'].sum(axis=0)
                    resultType = rowsData[0]['Vehics'].dtype
                     
                if variable == 'Demand':
                    result = rowsData['Demand'].sum(axis=0)
                    resultType = rowsData[0]['Demand'].dtype
                     
                if variable == 'Energy':
                    result = rowsData['Energy'].sum(axis=0)
                    resultType = rowsData[0]['Energy'].dtype
                 
                if variable == 'ServLev':
                    result = rowsData['ServLev'][0]
                    resultType = rowsData[0]['ServLev'].dtype
                     
                if variable == 'Dem/Cap':
                    sumDeman = rowsData['Demand'].sum(axis=0)
                    cap = rowsData['Capac'].sum(axis=0)
                    if np.isinf(cap):
                            result = 0
                    else:
                        cap = float(cap)
                        if cap == 0:
                            result = 0
                        else:
                            result = sumDeman / cap
                    resultType = rowsData[0]['Demand'].dtype
                     
                if variable == 'FinSpeed':
                    result = rowsData['FinSpeed'].max(axis=0)
                    resultType = rowsData[0]['FinSpeed'].dtype
                     
                if variable == 'FinWait':
                    timeList = rowsData['FinWait'].tolist()
                    totalSecs = 0
                    for tm in timeList:
                        timeParts = [int(s) for s in tm.split(':')]
                        totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                    totalSecs, sec = divmod(totalSecs, 60)
                    hr, min = divmod(totalSecs, 60)
                     
                    result =  format(hr, '02') + ':' + format(min, '02') + ':' + format(sec, '02')
                    #result = rowsData['FinWait'].sum(axis=0)
                    resultType = rowsData['FinWait'].dtype
                 
                rowData = np.array([(rowsData[0]['Id'], result)],
                                       dtype = [('Id', rowsData.dtype[0]), 
                                                ('Result', resultType)])
        
        return rowData
            
    def __evaluate_total(self, networkMatrixData, oriDestPairMatrix, variable):
        """
            @summary: Evaluates data at total level
            @param networkMatrixData: Network matrix
            @type networkMatrixData: Numpy array
            @param oriDestPairMatrix: Network matrix filtered by a pair origin-destination
            @type oriDestPairMatrix: Numpy array
            @param variable: Variable selected
            @type variable: String
            @return: Matrix of data
        """
        rowData = None
        rowsData = None
        matrixData = None
        
        if networkMatrixData is not None:
            if networkMatrixData.size > 0:
                if oriDestPairMatrix is not None:
                    for pair in np.nditer(oriDestPairMatrix):
                        rowsData = self.__get_network_rows(pair['Orig'], pair['Dest'], networkMatrixData)

                        if rowsData is not None:
                            rowData = self.__evaluate_variable(rowsData, variable)
                            
                            if rowData is not None:
                                if matrixData is None:
                                    matrixData = rowData
                                else:
                                    matrixData = np.concatenate((matrixData, rowData))
        
        return matrixData
    
    def __evaluate_levels(self, networkMatrixData, networkExpression, oriDestPairMatrix, variable, level):
        """
            @summary: Evaluates levels data
            @param networkMatrixData: Network matrix
            @type networkMatrixData: Numpy array
            @param networkExpression: Network expression to be evaluated
            @type networkExpression: Stack object
            @param oriDestPairMatrix: Network matrix filtered by a pair origin-destination
            @type oriDestPairMatrix: Numpy array
            @param variable: Variable selected
            @type variable: String
            @param level: Level we are evaluating (Operator or Route)
            @type level: Enum
            @return: Matrix of data
        """
        rowData = None
        rowsData = None
        operand1 = None
        operand2 = None
        matrixData = None
        try:
            if networkMatrixData is not None:
                if networkMatrixData.size > 0:
                    if type(networkExpression) is list:
                        stackLen = len(networkExpression[0].data)
                        networkExpressionData = networkExpression[0]
                    if type(networkExpression) is Stack:
                        stackLen = len(networkExpression.data)
                        networkExpressionData = networkExpression
                        
                    generalOperands = Stack()
                    
                    for pair in np.nditer(oriDestPairMatrix):
                        oriDestPairMatrix = self.__get_network_rows(pair['Orig'], pair['Dest'], networkMatrixData)
                        if oriDestPairMatrix is not None:
                            expCounter = 0
                            for item in networkExpressionData.data:
                                expCounter +=1
                                if ExpressionData.is_operator(item):
                                    operand2 = generalOperands.pop()
                                    if type(operand2) is not np.ndarray:
                                        if operand2 is not None:
                                            if ExpressionData.is_number(operand2):
                                                operand2 = float(operand2)
                                            else:
                                                operand2 = self.__evaluate_network_expression(operand2, variable, level, oriDestPairMatrix)
                                                                                
                                    operand1 = generalOperands.pop()
                                    if type(operand1) is not np.ndarray:
                                        if operand1 is not None:
                                            if ExpressionData.is_number(operand1):
                                                operand1 = float(operand1)
                                            else:
                                                operand1 = self.__evaluate_network_expression(operand1, variable, level, oriDestPairMatrix)
                                    
                                    rowData = self.__execute_network_expression(operand1, operand2, item, variable, networkMatrixData.dtype)
                                    
                                    if expCounter < stackLen:
                                        generalOperands.push(rowData)
                                    else:
                                        if rowData is not None:
                                            if matrixData is None:
                                                matrixData = rowData
                                            else:
                                                matrixData = np.concatenate((matrixData, rowData))
                                    
                                else:
                                    if stackLen == 1: 
                                        rowData = self.__evaluate_network_expression(item, variable, level, oriDestPairMatrix)
                                        
                                        if rowData is not None:
                                            if matrixData is None:
                                                matrixData = rowData
                                            else:
                                                matrixData = np.concatenate((matrixData, rowData))
                                    else:
                                        generalOperands.push(item)
                                    
        except Exception as inst:
            print(inst)
            matrixData = None
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Error", "Unexpected error: {0}".format(inst), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            matrixData = None
        finally:
            del rowData

        return matrixData

    def __execute_network_expression(self, operand1, operand2, operator, variable, types):
        """
            @summary: Executes network expression provided
            @param operand1: First operand
            @type operand1: Multi-type data
            @param operand2: Second operand
            @type operand2: Multi-type data
            @param operator: Operator
            @type operator: String
            @param variable: Variable selected
            @type variable: String
            @param types: Numpy array column types
            @type types: Numpy array
            @return: Matrix row
        """
        
        rowData = None
        
        if operand1 is None and operand2 is None:
            return None
        else:
            if operand1 is not None:
                if operand2 is not None:
                    if operand1.size < 1 and operand2.size < 1:
                        return None
        
        if operand1 is None and operand2 is not None:
            if operand2.size < 1:
                return None
         
        if operand1 is not None and operand2 is None:
            if operand1.size < 1:
                return None
        
        if operator is None:
            print ("There is no operator to perform the operation.")
            return None
        
        
        op1 = None
        op2 = None
        operand = None
        result = None
        if type(operand1) is np.ndarray and type(operand2) is np.ndarray:
            if variable == 'StVeh/Cap' or variable == 'StVeh' or variable == 'TotVeh' or variable == 'Demand' or variable == 'Energy' or variable == 'Dem/Cap':
                if operand1.size > 0:
                    op1 = operand1['Result']
                    operand =  operand1
                else:
                    op1 = 0
                
                if operand2.size > 0:
                    if operand is None: operand = operand2 
                    op2 = operand2['Result']
                    
                else:
                    op2 = 0
                
                result = ExpressionData.perform_arithmetic(op1, op2, operator)
                resultType = operand1['Result'].dtype

            if variable == 'ServLev':
                # Is the same value for both operands, we return the first operand with value
                if operand1.size > 0:
                    operand = operand1
                
                if operand2.size > 0:
                    if operand is None: operand = operand2

                return operand
            
            if variable == 'FinSpeed':
                if operand1.size > 0:
                    op1 = operand1['Result']
                    operand =  operand1
                else:
                    op1 = 0
                
                if operand2.size > 0: 
                    if operand is None: operand = operand2
                    op2 = operand2['Result']
                else:
                    op2 = 0

                if op1 >= op2:
                    return op1
                else:
                    return op2

            if variable == 'FinWait':
                if operand1.size > 0:
                    operand =  operand1
                    timeList1 = operand1['Result'].tolist()
                    totalSecs1 = 0
                    for tm1 in timeList1:
                        timeParts1 = [int(s) for s in tm1.split(':')]
                        totalSecs1 += (timeParts1[0] * 60 + timeParts1[1]) * 60 + timeParts1[2]
                else:
                    totalSecs1 = 0
                
                if operand2.size > 0:
                    if operand is None: operand = operand2
                    timeList2 = operand2['Result'].tolist()
                    totalSecs2 = 0
                    for tm2 in timeList2:
                        timeParts2 = [int(s) for s in tm2.split(':')]
                        totalSecs2 += (timeParts2[0] * 60 + timeParts2[1]) * 60 + timeParts2[2]
                else:
                    totalSecs2 = 0
                        
                result = ExpressionData.perform_arithmetic(totalSecs1, totalSecs2, operator)
                
                totalSecs, sec = divmod(result, 60)
                hr, min = divmod(totalSecs, 60)
                 
                result =  format(hr, '02') + ':' + format(min, '02') + ':' + format(sec, '02')
                resultType = operand1['Result'].dtype
             
            rowData = np.array([(operand[0]['Id'], result)],
                                   dtype = [('Id', operand.dtype[0]), 
                                            ('Result', resultType)])
        
        return rowData

    def __evaluate_network_expression(self, item, variable, level, oriDestMatrix):
        """
            @summary: Evaluates network expression
            @param item: List value of the level we are evaluating (Operator or Route)
            @type item: String 
            @param variable: Variable
            @type variable: String
            @param level: Level we are evaluating (Operator or Route)
            @type level: Enum
            @param oriDestMatrix: Network matrix filtered by origin and destination
            @type oriDestMatrix: Numpy matrix
            @return: Matrix row
        """
        rowData = None
        rowsData = None
        if int(level) == int(Level.Operators):
            rowsData = self.__get_network_rows_by_operator(item, oriDestMatrix)

        if int(level) == int(Level.Routes):
            rowsData = self.__get_network_rows_by_route(item, oriDestMatrix)
        
        if rowsData is not None:
            if rowsData.size > 0:
                rowData = self.__evaluate_variable(rowsData, variable)
        return rowData
    
    def __evaluate_scenarios(self, networkMatrixScenario1, networkMatrixScenario2, links, variable, operator):
        """
            @summary: Evaluates scenarios
            @param networkMatrixScenario1: Network matrix for scenario 1
            @type networkMatrixScenario1: Numpy array
            @param networkMatrixScenario2: Network matrix for scenario 2
            @type networkMatrixScenario2: Numpy array
            @param links: Links matrix
            @type links: Numpy array
            @param variable: Variable to evaluate
            @type variable: String
            @param operator: Operator
            @type operator: String
            @return: Matrix of data
        """
        rowData = None
        matrixData = None
        
        if networkMatrixScenario1 is not None and networkMatrixScenario2 is not None:
            if links is not None:
                for link in np.nditer(links):
                    operand1 = self.__get_processed_network_rows(link['Orig'], link['Dest'], networkMatrixScenario1)
                    operand2 = self.__get_processed_network_rows(link['Orig'], link['Dest'], networkMatrixScenario2)
                    
                    rowData = self.__execute_network_expression(operand1, operand2, operator, variable, networkMatrixScenario1.dtype)
                    
                    if rowData is not None:
                        if matrixData is None:
                            matrixData = rowData
                        else:
                            matrixData = np.concatenate((matrixData, rowData))
        
        return matrixData 
        
    def __evaluate_scenario(self, networkMatrix, oriDestPairs, networkExpression, variable, level, projectPath):
        """
            @summary: Evaluates network expression for a scenario
            @param scenariosExpression: Scenarios expression to be evaluated
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression to be evaluated
            @type networkExpression: Stack object
            @param variable: Variable
            @type variable: String
            @param level: Level we are evaluating (Operator or Route)
            @type level: Enum 
            @param projectPath: Project path
            @type projectPath: String
            @return: Matrix of data 
        """
    
        matrixData = None
        types = oriDestPairs.dtype
        #print("DENTRO DE __evaluate_scenario types {} oriDestPairs {} level {} Level.Total {} ".format(types, oriDestPairs, level, Level.Total))
        if oriDestPairs is not None:
            if level == Level.Total:
                matrixData = self.__evaluate_total(networkMatrix.data_matrix, oriDestPairs, variable)
            else:
                matrixData =  self.__evaluate_levels(networkMatrix.data_matrix, networkExpression, oriDestPairs, variable, level)

        return matrixData

    def __evaluate_network_scenarios_expression(self, layerName, scenariosExpression, networkExpression, variable, level, projectPath):
        """
            @summary: Evaluates network scenarios expression
            @param layerName: Layer name
            @type layerName: String
            @param scenariosExpression: Scenarios expression to be evaluated
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression to be evaluated
            @type networkExpression: Stack object
            @param variable: Variable
            @type variable: String
            @param level: Level we are evaluating (Operator or Route)
            @type level: Enum 
            @param projectPath: Project path
            @type projectPath: String
            @return: Matrix of data
        """
        rowData = None
        operand1 = None
        operand2 = None
        matrixData = None
        
        try:
            stackLen = len(scenariosExpression.data)
            generalOperands = Stack()
            
            for item in scenariosExpression.data:
                if ExpressionData.is_operator(item):
                    networkMatrix2, links2 = self.__get_scenario_data(generalOperands.pop(), projectPath)
                    networkMatrix1, links1 = self.__get_scenario_data(generalOperands.pop(), projectPath)
                    
                    links = self.__merge_netword_ids(links1, links2)
                    types = links.dtype
        
                    operand2 = self.__evaluate_scenario(networkMatrix2, links, networkExpression, variable, level, projectPath)
                    operand1 = self.__evaluate_scenario(networkMatrix1, links, networkExpression, variable, level, projectPath)
                    
                    matrixData =  self.__evaluate_scenarios(operand1, operand2, links, variable, item)                   
                else:
                    #print("dentro de la data else")
                    if stackLen == 1:
                        #print("dentro de la data else if ")
                        networkMatrix, links = self.__get_scenario_data(item, projectPath)
                        #print("dentro de la data else if {} links {}".format(networkMatrix, links))
                        matrixData = self.__evaluate_scenario(networkMatrix, links, networkExpression, variable, level, projectPath)
                        #print("DATAMATRIX {} ".format(matrixData))

                    else:
                        generalOperands.push(item)

        except Exception as inst:
            matrixData = None
            print(inst)
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Error", "Unexpected error: {0}".format(inst), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        except:
            matrixData = None
            print("Unexpected error:", sys.exc_info()[0])
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network expression", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

        return matrixData  
    
    def create_network_memory(self, layerName, scenariosExpression, networkExpression, variable, level, projectPath):
        """
            @summary: Creates new network csv file
            @param layerName: Layer name
            @type layerName: String
            @param scenariosExpression: Scenarios expression to be evaluated
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression to be evaluated
            @type networkExpression: Stack object
            @param variable: Variable
            @type variable: String
            @param level: Level we are evaluating (Operator or Route)
            @type level: Enum 
            @param projectPath: Project path
            @type projectPath: String
            @return: Resul of the process
        """
        rowCounter = 0
        networkMatrixResult = None
        minValue = float(1e100)
        maxValue = float(-1e100)
        print(" dentro create_network_memory layerName {}, scenariosExpression {}, networkExpression {}, variable {}, level {}, projectPath {} ".format(layerName, scenariosExpression, networkExpression, variable, level, projectPath))
        if level == Level.Total or len(networkExpression) == 1:
            print(" dentro del primer create_network_memory layerName {}, scenariosExpression {}, networkExpression {}, variable {}, level {}, projectPath {} ".format(layerName, scenariosExpression, networkExpression, variable, level, projectPath))
            networkMatrixResult = self.__evaluate_network_scenarios_expression(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        
        if networkMatrixResult is None:
            messagebox = QMessageBox.warning(None, "Network matrix data", "There is not data to evaluate.")
            #messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network matrix data", "There is not data to evaluate.", "", self, buttons = QtWidgets.QMessageBox.Ok)
            #messagebox.exec_()
            print ("There is not data to evaluate.")
            return False, None, minValue, maxValue
        
        for value in networkMatrixResult:
            maxValue = max(maxValue, value[1])
            minValue = min(minValue, value[1])

        return True, networkMatrixResult, minValue, maxValue

    def create_network_csv_file(self, layerName, scenariosExpression, networkExpression, variable, level, projectPath):
        """
            @summary: Creates new network csv file
            @param layerName: Layer name
            @type layerName: String
            @param scenariosExpression: Scenarios expression to be evaluated
            @type scenariosExpression: Stack object
            @param networkExpression: Network expression to be evaluated
            @type networkExpression: Stack object
            @param variable: Variable
            @type variable: String
            @param level: Level we are evaluating (Operator or Route)
            @type level: Enum 
            @param projectPath: Project path
            @type projectPath: String
            @return: Resul of the process
        """
        rowCounter = 0
        networkMatrixResult = None

        if level == Level.Total or len(networkExpression) == 1:
            networkMatrixResult = self.__evaluate_network_scenarios_expression(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        
        if networkMatrixResult is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Network matrix data", "There is not data to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
            print ("There is not data to evaluate.")
            return False
        
        csvFile = open(projectPath + "\\" + layerName + ".csv", "w")
        
        newFile = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        newFile.writerow(['ID', 'Result'])
        print(" Información: ".format(networkMatrixResult))
        for rowItem in np.nditer(networkMatrixResult):
            newFile.writerow([str(rowItem['Id']).replace("b","").replace("'",""), rowItem['Result']])

        del newFile
        csvFile.close
        del csvFile
        
        return True
    
    
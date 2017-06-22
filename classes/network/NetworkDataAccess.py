from ..general.FileManagement import FileManagement
from ..Stack import Stack
from ..ExpressionData import ExpressionData
from Level import *
import csv, numpy as np
from PyQt4.Qt import QMessageBox

class NetworkDataAccess(object):
    def __init__(self):
        """
            @summary: Class constructor
        """
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
        
    def get_variables_dic(self):
        """
            @summary: Returns variables dictionary
        """
        return {0:"StVeh/Cap", 1:"StVeh", 2:"TotVeh", 3:"ServLev", 4:"Demand", 5:"Dem/Cap", 6:"FinSpeed", 7:"FinWait", 8:"Energy" }
    
    def get_valid_network_scenarios(self, projectPath):
        """
            @summary: Gets scenarios from file
            @param projectPath: Project path
            @type projectPath: String  
        """
        return FileManagement.get_scenarios_from_filename(projectPath, 'Assignment_SWN(.*)', '\..*')
    
    def get_scenario_operators(self, projectPath, scenario):
        """
            @summary: Gets operators from scenario provided
            @param projectPath: Project path
            @type projectPath: String
            @param scenario: File scenario
            @type scenario: String  
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
    
    def __get_network_ids(self, networkMatrix):
        """
            @summary: Gets pairs of origin and destination
            @param networkMatrix: Network matrix
            @type networkMatrix: Numpy array
        """
        if networkMatrix is not None:
            if networkMatrix.data_matrix.size > 0:
                routesMatrix = np.unique(networkMatrix.data_matrix[['Id', 'Orig', 'Dest']])

                return routesMatrix
        
        return None
    
    def __get_network_rows(self, origin, destination, networkMatrix):
        """
            @summary: Gets network matrix rows looking by origin, destination
            @param origin: Origin
            @type origin: String
            @param destination: Destination
            @type destination: String
            @param networkMatrix: Network matrix
            @type networkMatrix: Numpy array
        """
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
            
    def __get_network_rows_by_operator(self, operator, oriDestMatrix):
        """
            @summary: Gets network matrix rows from a pair origin-destination looking by operator
            @param operator: Operator
            @type operator: String
            @param oriDestMatrix: Network matrix filtered by origin and destination
            @type oriDestMatrix: Numpy array
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
                            
                            if matrixData is None:
                                matrixData = rowData
                            else:
                                matrixData = np.concatenate((matrixData, rowData))
        
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
        """
        
        rowData = None
        
        if operand1 is None and operand2 is None:
            return None
        if operator is None:
            print ("There is no operator to perform the operation.")
            return None
        
        if operand1 is None and operand2 is not None:
            return operand2
        
        if operand1 is not None and operand2 is None:
            return operand1
        
        
        op1 = None
        op2 = None
        result = None
        if type(operand1) is np.ndarray and type(operand2) is np.ndarray:
            if variable == 'StVeh/Cap' or variable == 'StVeh' or variable == 'TotVeh' or variable == 'Demand' or variable == 'Energy' or variable == 'Dem/Cap':
                if operand1.size > 0 and operand2.size > 0:
                    op1 = operand1['Result']
                    op2 = operand2['Result']
                    result = ExpressionData.perform_arithmetic(op1, op2, operator)
                    resultType = operand1['Result'].dtype

            if variable == 'ServLev':
                # Is the same value for both operands, we return the first operand
                return operand1
            
            if variable == 'FinSpeed':
                if operand1['Result'] >= operand2['Result']:
                    return operand1
                else:
                    return operand2

            if variable == 'FinWait':
                timeList1 = operand1['Result'].tolist()
                timeList2 = operand2['Result'].tolist()
                totalSecs1 = 0
                totalSecs2 = 0
                for tm1 in timeList1:
                    timeParts1 = [int(s) for s in tm1.split(':')]
                    totalSecs1 += (timeParts1[0] * 60 + timeParts1[1]) * 60 + timeParts1[2]
                
                for tm2 in timeList2:
                    timeParts2 = [int(s) for s in tm2.split(':')]
                    totalSecs2 += (timeParts2[0] * 60 + timeParts2[1]) * 60 + timeParts2[2]
                        
                result = ExpressionData.perform_arithmetic(totalSecs1, totalSecs2, operator)
                
                totalSecs, sec = divmod(result, 60)
                hr, min = divmod(totalSecs, 60)
                 
                result =  format(hr, '02') + ':' + format(min, '02') + ':' + format(sec, '02')
                resultType = operand1['Result'].dtype
             
            rowData = np.array([(operand1[0]['Id'], result)],
                                   dtype = [('Id', operand1.dtype[0]), 
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
        """
        rowData = None
        rowsData = None
        
        if level == Level.Operators:
            rowsData = self.__get_network_rows_by_operator(item, oriDestMatrix)
        
        if level == Level.Routes:
            rowsData = self.__get_network_rows_by_route(item, oriDestMatrix)
        
        if rowsData is not None:
            if rowsData.size > 0:
                rowData = self.__evaluate_variable(rowsData, variable)
            
        return rowData
    
    def __evaluate_network_scenarios_expression(self, layerName, scenariosExpression, networkExpression, variable, level, projectPath):
        """
            @summary: Evaluates network expression for scenario
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
        """
    
        rowData = None
        rowsData = None
        operand1 = None
        operand2 = None
        matrixData = None
        try:
            
            networkMatrix = FileManagement.get_np_matrix_from_csv(projectPath, 'Assignment_SWN', scenariosExpression.pop(), '\..*')
            oriDestPairs = self.__get_network_ids(networkMatrix)
            types = oriDestPairs.dtype
            if oriDestPairs is not None:
                if level == Level.Total:
                        matrixData = self.__evaluate_total(networkMatrix.data_matrix, oriDestPairs, variable)
    
                else:
                    if networkMatrix is not None:
                        if networkMatrix.data_matrix.size > 0:
                            if type(networkExpression) is list:
                                stackLen = len(networkExpression[0].data)
                                networkExpressionData = networkExpression[0]
                            if type(networkExpression) is Stack:
                                stackLen = len(networkExpression.data)
                                networkExpressionData = networkExpression
                                
                            generalOperands = Stack()
                            
                            for pair in np.nditer(oriDestPairs):
                                oriDestMatrix = self.__get_network_rows(pair['Orig'], pair['Dest'], networkMatrix.data_matrix)
                                if oriDestMatrix is not None:
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
                                                        operand2 = self.__evaluate_network_expression(operand2, variable, level, oriDestMatrix)
                                                                                        
                                            operand1 = generalOperands.pop()
                                            if type(operand1) is not np.ndarray:
                                                if operand1 is not None:
                                                    if ExpressionData.is_number(operand1):
                                                        operand1 = float(operand1)
                                                    else:
                                                        operand1 = self.__evaluate_network_expression(operand1, variable, level, oriDestMatrix)
                                            
                                            rowData = self.__execute_network_expression(operand1, operand2, item, variable, networkMatrix.data_matrix.dtype)
                                            
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
                                                rowData = self.__evaluate_network_expression(item, variable, level, oriDestMatrix)
                                                
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
            QMessageBox.warning(None, "Error", "Unexpected error: {0}".format(inst))
        except:
            QMessageBox.warning(None, "Network expression", "Unexpected error: {0}".format(sys.exc_info()[0]))
            print("Unexpected error:", sys.exc_info()[0])
            matrixData = None
        finally:
            del rowData
            #del rowsData

        return matrixData    
    
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
        """
        rowCounter = 0
        networkMatrixResult = None

        if scenariosExpression.tp > 1:
            return True
        else:
            networkMatrixResult = self.__evaluate_network_scenarios_expression(layerName, scenariosExpression, networkExpression, variable, level, projectPath)
        
        if networkMatrixResult is None:
            QMessageBox.warning(None, "Network matrix data", "There is not data to evaluate.")
            print ("There is not data to evaluate.")
            return False
        
        csvFile = open(projectPath + "\\" + layerName + ".csv", "wb")
        
        newFile = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        newFile.writerow(['Id', 'Result'])
        for rowItem in np.nditer(networkMatrixResult):
            newFile.writerow([rowItem['Id'], rowItem['Result']])
                    
        del newFile
        csvFile.close
        del csvFile
        
        return True
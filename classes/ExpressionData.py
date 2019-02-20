# -*- coding: utf-8 -*-
from .Zone import Zone
from .Stack import Stack
from .general.QTranusMessageBox import QTranusMessageBox

import csv, numpy as np

class ExpressionData(object):
    @staticmethod
    def is_operator(operator):
        """
            @summary: Method that compares if the string sent is an operator
            @param operator: String to evaluate 
            @type operator: String
            @return: Boolean result of the evaluation 
        """
        return operator=='+' or operator=='-' or operator=='*' or operator=='/'
    
    @staticmethod
    def is_conditional(conditional):
        """
            @summary: Method that validates if the string sent is a conditional
            @param conditional: String to evaluate
            @type conditional: String
            @return: Boolean result of the evaluation
        """
        return conditional == '>' or conditional == '<' or conditional == '>=' or conditional == '<=' or conditional == '!=' or conditional == '=='
    
    @staticmethod
    def is_number(number):
        """
            @summary: Method that validates if the string sent is a number
            @param number: String to evaluate
            @type number: String
            @return: Boolean result of the evaluation
        """
        try:
            float(number)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def keep_iterating(o1, o2):
        return (o1=='-' and ExpressionData.is_operator(o2)) or (o1=='/' and (o2=='/' or o2=='*')) or (o1=='+' and (o2=='*' or o2=='/'))
    
    @staticmethod
    def tokenize(expression):
        """
            @summary: Split the expression in tokens
            @param expression: Expression to split 
            @type expression: String
            @return: Expression split in tokens
        """
        tokens = []
        i = 0
        temp = None
        expressionLen = len(expression)
        while i < expressionLen:
            if expression[i] == '(' or expression[i] == ')' or expression[i] == '*' or expression[i] == '/' or expression[i] == '+' or expression[i] == '-':
                tokens.append(expression[i])
                i = i + 1
            elif  expression[i] == '>' or expression[i] == '<' or expression[i] == '!' or expression[i] == '=':
                temp = expression[i]
                if (i + 1) >= expressionLen:
                    print("Incorrect expression, right part missing.")
                    return None
                else:
                    if expression[i + 1] == '=':
                        tokens.append(expression[i] + expression[i+1])
                        i = i + 2
                    else:
                        tokens.append(expression[i])
                        i = i + 1
            elif expression[i] == ' ' or expression[i]=='\t':
                i = i + 1
            elif expression[i].isdigit():
                start = i
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    i = i + 1
                nextToken = expression[start:i]
                tokens.append(nextToken)
            elif expression[i].isalpha() or expression[i] == '[':
                start = i
                while i < len(expression) and (expression[i].isalpha() or expression[i] == '.' or expression[i] == '[' or expression[i] == ']' or expression[i].isdigit()):
                    i = i + 1
                nextToken = expression[start:i]
                tokens.append(nextToken)
            else:
                print("Unexpected token: {0}").format(expression[i])
                i = i + 1
        return tokens

    @staticmethod
    def shutting_yard_parsing(tokens):
        """
            @summary: Parses expression
            @param tokens: Expression tokens
            @type tokens: Stack object  
            @return: Boolean parsing result and expression stack in reverse polish notation
        """
        output = Stack()
        operators = Stack()
        outputType = []
        result = True
        try:
            for token in tokens:
                if token[0].isdigit() or token[0].isalpha(): # number or id
                    output.push(token)
                elif token=='(':
                    operators.push(token)
                elif token==')':
                    while operators.top() != '(':
                        output.push(operators.pop())
                    operators.pop()
                else:   # operators
                    while not operators.empty() and ExpressionData.keep_iterating(token, operators.top()):
                        output.push(operators.pop())
                    operators.push(token)
            while not operators.empty():
                output.push(operators.pop())
                
            nOperators = 0
            nOperands = 0
            for x in output.data:
                if ExpressionData.is_operator(x):
                    nOperators = nOperators + 1
                else:
                    nOperands = nOperands + 1
                    
            if nOperators+1 != nOperands:
                messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Parsing", "Incorrect expression, please validate it.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
                messagebox.exec_()
                print("Incorrect expression, please validate it.")
                result = False
                output = None
                
        except Exception as e:
            result = False
            output = None
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Parsing", ("There was an error parsing the expression:\nErr. Codes:{0}\nErr. Message:{1}").format(e.errcode, e.errmsg), ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("There was an error parsing the expression:\nErr. Codes:{0}\nErr. Message:{1}").format(e.errcode, e.errmsg)

        finally:
            return result, output
    
    @staticmethod
    def validate_sectors_expression(expression):
        """
            @summary: Validates sectors expression
            @param expression: Sectors expression
            @type expression: String  
            @return: Boolean result of validation and expression stack in reverse polish notation
        """
        tokens = None
        outputExpressions = []
        
        if expression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Sectors expression", "There is not sectors expression to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("There is not sectors expression to evaluate.")
            return False, None
        
        if len(expression.strip()) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Sectors expression", "There is not sectors expression to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("There is not sectors expression to evaluate.")
            return False, None        
        
        tokens = ExpressionData.tokenize(expression)
        if tokens is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Sectors expression", "Incorrect expression, please validate it.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Incorrect expression, please validate it.")
            return False, None
        else:
            tokensResult, tokensList, hasConditionals = ExpressionData.validate_conditionals(tokens)
        
        if not tokensResult:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Sectors expression", "Incorrect expression, please validate it.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Incorrect expression, please validate it.")
            return False, None
        else:
            if not hasConditionals:
                result, output = ExpressionData.shutting_yard_parsing(tokensList)
                if result:
                    outputExpressions.append(output)
                else:
                    return False, None
            else:        
                for listItem in tokensList:
                    if type(listItem) is list:
                        result, output = ExpressionData.shutting_yard_parsing(listItem)
                        if result:
                            outputExpressions.append(output)
                        else:
                            return False, None
                    else:
                        if ExpressionData.is_conditional(listItem):
                            item = [True, listItem]
                            outputExpressions.append(listItem)
                        else:
                            return False, None
        
        return result, outputExpressions
    
    @staticmethod
    def validate_scenarios_expression(expression):
        """
            @summary: Validates scenarios expression
            @param expression: Scenarios expression
            @type expression: String  
            @return: Boolean result of validation and expression stack in reverse polish notation 
        """
        result = True
        output = None
                
        if expression is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios validation", "There is not scenarios expression to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("There is not scenarios expression to evaluate.")
            result = False
            output = None
        if len(expression) == 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenarios validation", "There is not scenarios expression to evaluate.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("There is not scenarios expression to evaluate.")
            result = False
            output = None
        
        result, output = ExpressionData.shutting_yard_parsing(expression)
        
        return result, output
    
    @staticmethod
    def validate_conditionals(tokens):
        """
            @summary: Validates if the expression tokens has a conditional, if so also validates both sides of the conditional
            @param tokens: Expression tokens
            @type tokens: List of strings
            @return: Boolean result of validation and a list of expressions
        """
        result = True
        output = None
        hasConditional = False
        
        conditionals = ['>', '<', '<=', '>=', '!=', '==']
        uncompletedConditionals = ['!', '='] 
        conditionalFound = {}
        uncompletedConditionalsFound = {}
        tokensList = []
        
        # Looks for completed conditionals
        for conditional in conditionals:
            if conditional in tokens:
                conditionalFound[tokens.index(conditional)] = conditional
        
        # Looks for uncompleted conditionals
        for uncompletedConditional in uncompletedConditionals:
            if uncompletedConditional in tokens:
                uncompletedConditionalsFound[tokens.index(uncompletedConditional)] = uncompletedConditional

        # If there is one or more uncompleted conditionals the expression is incorrect
        if len(uncompletedConditionalsFound) > 0:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Conditionals validation", "Uncompleted conditionals.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Uncompleted conditionals.")
            return False, None, True

        # If there is more than one conditional the expression is incorrect
        if len(conditionalFound) > 1:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Conditionals validation", "There is more than one conditional.", ":/plugins/QTranus/icon.png", self, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("There is more than one conditional.")
            return False, None, True
        # If it has one conditional is valid
        elif len(conditionalFound) == 1:
            tokensList.append(tokens[0:conditionalFound.keys()[0]])
            tokensList.append(tokens[(conditionalFound.keys()[0] + 1):(len(tokens) + 1)])
            tokensList.append(conditionalFound[conditionalFound.keys()[0]])
            output = tokensList
            hasConditional = True
        # If it has not conditionals is valid
        else:
            output = tokens
            hasConditional = False
        
        return result, output, hasConditional
    
    @staticmethod
    def perform_arithmetic(value1, value2, operator):
        """
            @summary: Method that perform the arithmetic operation between two operands
            @param value1: First Operand 
            @type: value1: Numeric value
            @param value2: Second Operand
            @type value2: Numeric value
            @param operator: Operator to perform arithmetic operation
            @type operator: String
            @return: Result of the arithmetic operation 
        """
        result = 0.0
        if operator == '+':
            result = value1 + value2
            
        elif operator == '-':
            result = value1 - value2
            
        elif operator == '*':
            result = value1 * value2
        
        elif operator == '/':
            if value2 == 0:
                result = 0
            else:
                result = value1 / value2
        
        elif operator == '>':
            if value1 > value2:
                result = 1
            else:
                result = 0
                
        elif operator == '<':
            if value1 < value2:
                result = 1
            else:
                result = 0
                
        elif operator == '>=':
            if value1 >= value2:
                result = 1
            else:
                result = 0
        
        elif operator == '<=':
            if value1 <= value2:
                result = 1
            else:
                result = 0
        
        elif operator == '!=':
            if value1 != value2:
                result = 1
            else:
                result = 0
        
        elif operator == '==':
            if value1 == value2:
                result = 1
            else:
                result = 0
        
        return result
    
    @staticmethod
    def fill_zone_data(zone, itemOp1, itemOp2, operator, fieldName):
        """
            @summary: Method that fills the Zone Object
            @param zone: Object to be filled 
            @type zone: Zone object
            @param itemOp1: Operator 1
            @type itemOp1: A Zone object or a numeric value
            @param itemOp2: Operator 2
            @type itemOp2: A Zone object or a numeric value
            @param operator: Operator to perform arithmetic operation
            @type operator: String
            @param fieldName: Field in object list which we get the value
            @type fieldName: String
            @return: Zone object 
        """
        value1 = 0.0
        value2 = 0.0
        
        if fieldName.upper() == 'TOTPROD':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.totProd
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.totProd
            else:
                value2 = itemOp2
                
            zone.totProd = ExpressionData.perform_arithmetic(value1, value2, operator)
 
        if fieldName.upper() == 'TOTDEM':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.totDem
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.totDem
            else:
                value2 = itemOp2
                
            zone.totDem = ExpressionData.perform_arithmetic(value1, value2, operator)
         
        if fieldName.upper() == 'PRODCOST':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.prodCost
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.prodCost
            else:
                value2 = itemOp2
            
            zone.prodCost = ExpressionData.perform_arithmetic(value1, value2, operator)
         
        if fieldName.upper() == 'PRICE':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.price
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.price
            else:
                value2 = itemOp2
            
            zone.price = ExpressionData.perform_arithmetic(value1, value2, operator)
         
        if fieldName.upper() == 'MINRES':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.minRes
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.minRes
            else:
                value2 = itemOp2
            
            zone.minRes = ExpressionData.perform_arithmetic(value1, value2, operator)
         
        if fieldName.upper() == 'MAXRES':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.maxRes
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.maxRes
            else:
                value2 = itemOp2
            
            zone.maxRes = ExpressionData.perform_arithmetic(value1, value2, operator)
         
        if fieldName.upper() == 'ADJUST':
            if isinstance(itemOp1, Zone):
                value1 = itemOp1.adjust
            else:
                value1 = itemOp1
                
            if isinstance(itemOp2, Zone):
                value2 = itemOp2.adjust
            else:
                value2 = itemOp2
            
            zone.adjust = ExpressionData.perform_arithmetic(value1, value2, operator)
    
    @staticmethod
    def execute_expression(operand1, operand2, operator, fieldName):
        """
            @summary: Method that executes the arithmetic operations between two operands
            @param operand1: First Operand 
            @type operand1: List of Zone objects or scalar value
            @param operand2: Second Operand
            @type operand2: List of Zone objects or scalar value
            @param operator: Operator to perform arithmetic
            @type operator: String
            @param fieldName: Field in object list which we get the value
            @type fieldName: String
            @return: A list of Zone object 
        """
        zoneList = []
        
        if operand1 is None:
            print ("There is no data for operand1.")
        if operand2 is None:
            print ("There is no data for operand2.")
        if operator is None:
            print ("There is no operator to perform the operation.")
        
        if type(operand1) is list and type(operand2) is list:
            for itemOp1, itemOp2 in zip(operand1, operand2):
                newZone = Zone()
                newZone.id = itemOp1.id
                newZone.name = itemOp1.name
    
                ExpressionData.fill_zone_data(newZone, itemOp1, itemOp2, operator, fieldName)
                
                zoneList.append(newZone)
                del newZone
                
        if type(operand1) is list and type(operand2) is not list:
            for itemOp1 in operand1:
                newZone = Zone()
                newZone.id = itemOp1.id
                newZone.name = itemOp1.name
    
                ExpressionData.fill_zone_data(newZone, itemOp1, operand2, operator, fieldName)
                
                zoneList.append(newZone)
                del newZone
        
        if type(operand1) is not list and type(operand2) is list:
            for itemOp2 in operand2:
                newZone = Zone()
                newZone.id = itemOp2.id
                newZone.name = itemOp2.name
    
                ExpressionData.fill_zone_data(newZone, operand1, itemOp2, operator, fieldName)
                
                zoneList.append(newZone)
                del newZone
        if type(operand1) is not list and type(operand2) is not list:
            print("There are not sectors to evaluate.")
            zoneList = None
        
        return zoneList
    
    @staticmethod
    def execute_matrix_expression(operand1, operand2, operator, types):
        """
            @summary: Method that executes the arithmetoc operation between two operands
            @param operand1: First operand
            @type operand1: Numpy ndarray or scalar value
            @param operand2: Secod operand
            @type operand1: Numpy ndarray or scalar value
            @param operator: Operator to perform arithmetic
            @type operator: String
            @param types: Ndarray types 
            @type types: Ndarray dtypes object
            @return: Ndarray with trips matrix result            
        """
        
        rowData = None
        matrixData = None
        
        if operand1 is None:
            print ("There is no data for operand1.")
            return None
        if operand2 is None:
            print ("There is no data for operand2.")
            return None
        if operator is None:
            print ("There is no operator to perform the operation.")
            return None
        
        trip1 = 0
        trip2 = 0
        result = 0
        
        if type(operand1) is np.ndarray and type(operand2) is np.ndarray:
            if operand1.size > 0 and operand2.size > 0:
                matrixData = [] 
                for itemOp1, itemOp2 in np.nditer([operand1, operand2]):
                    trip1 = itemOp1['Trips']
                    trip2 = itemOp2['Trips']
                    result = ExpressionData.perform_arithmetic(trip1, trip2, operator)
                    
                    rowData = itemOp1.astype([(itemOp1.dtype.names[0], itemOp1.dtype[0]), 
                                    (itemOp1.dtype.names[1], itemOp1.dtype[1]), 
                                    (itemOp1.dtype.names[2], itemOp1.dtype[2]), 
                                    (itemOp1.dtype.names[3], itemOp1.dtype[3]), 
                                    (itemOp1.dtype.names[6], itemOp1.dtype[6]) if len(itemOp1.dtype) == 7 else (itemOp1.dtype.names[4], itemOp1.dtype[4])])
                    
                    rowData['Trips'] = result
                    matrixData.append(rowData)
                
                matrixData = np.array(matrixData, rowData.dtype)         
        
        if type(operand1) is np.ndarray and type(operand2) is not np.ndarray:
            matrixData = []
            for itemOp in np.nditer(operand1):
                trip1 = itemOp['Trips']
                trip2 = operand2
                result = ExpressionData.perform_arithmetic(trip1, trip2, operator)
                
                rowData = itemOp.astype([(itemOp.dtype.names[0], itemOp.dtype[0]), 
                                (itemOp.dtype.names[1], itemOp.dtype[1]), 
                                (itemOp.dtype.names[2], itemOp.dtype[2]), 
                                (itemOp.dtype.names[3], itemOp.dtype[3]), 
                                (itemOp.dtype.names[6], itemOp.dtype[6]) if len(itemOp.dtype) == 7 else (itemOp.dtype.names[4], itemOp.dtype[4])])
                
                rowData['Trips'] = result
                
                matrixData.append(rowData)

            matrixData = np.array(matrixData, rowData.dtype)
                
        if type(operand1) is not np.ndarray and type(operand2) is np.ndarray:
            matrixData = []
            for itemOp in np.nditer(operand2):
                trip1 = operand1
                trip2 = itemOp['Trips']
                result = ExpressionData.perform_arithmetic(trip1, trip2, operator)
                
                rowData = itemOp.astype([(itemOp.dtype.names[0], itemOp.dtype[0]), 
                                (itemOp.dtype.names[1], itemOp.dtype[1]), 
                                (itemOp.dtype.names[2], itemOp.dtype[2]), 
                                (itemOp.dtype.names[3], itemOp.dtype[3]), 
                                (itemOp.dtype.names[6], itemOp.dtype[6]) if len(itemOp.dtype) == 7 else (itemOp.dtype.names[4], itemOp.dtype[4])])
                
                rowData['Trips'] = result
                matrixData.append(rowData)

            matrixData =  matrixData = np.array(matrixData, rowData.dtype)
            
        return matrixData
    
    
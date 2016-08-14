from Zone import Zone
from Stack import Stack
from _hashlib import new

class ExpressionData(object):
    @staticmethod
    def is_operator(st):
        """
            @summary: Method that compare is the string sent is an operator
            @param st: String to evaluate 
            @type st: String
            @return: Boolean result of the evaluation 
        """
        return st=='+' or st=='-' or st=='*' or st=='/'
    
    @staticmethod
    def keep_iterating(o1, o2):
        return (o1=='-' and ExpressionData.is_operator(o2)) or (o1=='/' and (o2=='/' or o2=='*')) or (o1=='+' and (o2=='*' or o2=='/'))
    
    @staticmethod
    def tokenize(expression):
        """
            @summary: Split the expression in tokens
            @param expression: Expression to split 
            @type expression: String
            @return: Expression splitted in tokens
        """
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i] == '(' or expression[i] == ')' or expression[i] == '*' or expression[i] == '/' or expression[i] == '+' or expression[i] == '-':
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
                print("Incorrect expression, please validate it.")
                result = False
                output = None
                
        except Exception as e:
            result = False
            output = None
            print("There was an error parsing the expression:\nErr. Codes:{0}\nErr. Message:{1}").format(e.errcode, e.errmsg)

        finally:
            return result, output
    
    @staticmethod
    def validate_sectors_expression(expression):
        """
            @summary: Validates sectors expression
            @param expression: Sectors expression
            @param expression: String  
            @return: Boolean result of validation and expression stack in reverse polish notation
        """
        tokens = None
        
        if expression is None:
            print("There is not sectors expression to evaluate.")
            return False, None
        
        if len(expression.strip()) == 0:
            print("There is not sectors  expression to evaluate.")
            return False, None        
        
        tokens = ExpressionData.tokenize(expression)
        result, output = ExpressionData.shutting_yard_parsing(tokens)
        
        return result, output
    
    @staticmethod
    def validate_scenarios_expression(expression):
        """
            @summary: Validates scenarios expression
            @param expression: Scenarios expression
            @param expression: String  
            @return: Boolean result of validation and expression stack in reverse polish notation 
        """
        result = True
        output = None
                
        if expression is None:
            print("There is not scenarios expression to evaluate.")
            result = False
            output = None
        if len(expression) == 0:
            print("There is not scenarios expression to evaluate.")
            result = False
            output = None
        
        result, output = ExpressionData.shutting_yard_parsing(expression)
        
        return result, output
    
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
            
        if operator == '-':
            result = value1 - value2
            
        if operator == '*':
            result = value1 * value2
        
        if operator == '/':
            if value2 == 0:
                result = 0
            else:
                result = value1 / value2
        
        return result
    
    @staticmethod
    def fill__zone_data(zone, itemOp1, itemOp2, operator, fieldName):
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
            @type operand1: List of Zone objects or numeric
            @param operand2: Second Operand
            @type operand2: List of Zone objects or numeric
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
    
                ExpressionData.fill__zone_data(newZone, itemOp1, itemOp2, operator, fieldName)
                
                zoneList.append(newZone)
                del newZone
                
        if type(operand1) is list and type(operand2) is not list:
            for itemOp1 in operand1:
                newZone = Zone()
                newZone.id = itemOp1.id
                newZone.name = itemOp1.name
    
                ExpressionData.fill__zone_data(newZone, itemOp1, operand2, operator, fieldName)
                
                zoneList.append(newZone)
                del newZone
        
        if type(operand1) is not list and type(operand2) is list:
            for itemOp2 in operand2:
                newZone = Zone()
                newZone.id = itemOp2.id
                newZone.name = itemOp2.name
    
                ExpressionData.fill__zone_data(newZone, operand1, itemOp2, operator, fieldName)
                
                zoneList.append(newZone)
                del newZone
        
        return zoneList
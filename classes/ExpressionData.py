from Zone import Zone
from _hashlib import new

class ExpressionData(object):
    @staticmethod
    def is_operator(st):
        """
            @summary: Method that compare is the string sent is an operator
            @param st: String to evaluate 
            @type: st: String
            @return: Boolean result of the evaluation 
        """
        return st=='+' or st=='-' or st=='*' or st=='/'
    
    @staticmethod
    def keep_iterating(o1, o2):
        return (o1=='-' and ExpressionData.is_operator(o2)) or (o1=='/' and (o2=='/' or o2=='*')) or (o1=='+' and (o2=='*' or o2=='/'))
    
    @staticmethod
    def perform_arithmetic(value1, value2, operator):
        """
            @summary: Method that perform the arithmetic operation between two operands
            @param value1: First Operand 
            @type: value1: Numeric value
            @param value2: Second Operand
            @type value2: Numeric value
            @param operator: Operator to perform arithmetic operation
            @type operator: str
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
            @type: zone: Zone object
            @param itemOp1: Operator 1
            @type itemOp1: A Zone object or a numeric value
            @param itemOp2: Operator 2
            @type itemOp2: A Zone object or a numeric value
            @param operator: Operator to perform arithmetic operation
            @type operator: str
            @param: fieldName: Field in object list which we get the value
            @type fieldName: str
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
            @type: operand1: List of Zone objects or numeric
            @param operand2: Second Operand
            @type operand2: List of Zone objects or numeric
            @param operator: Operator to perform arithmetic
            @type operator: str
            @param: fieldName: Field in object list which we get the value
            @type fieldName: str
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
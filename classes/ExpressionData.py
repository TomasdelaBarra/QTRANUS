from Zone import Zone

class ExpressionData(object):
    @staticmethod
    def is_operator(st):
        return st=='+' or st=='-' or st=='*' or st=='/'
    
    @staticmethod
    def keep_iterating(o1, o2):
        return (o1=='-' and ExpressionData.is_operator(o2)) or (o1=='/' and (o2=='/' or o2=='*')) or (o1=='+' and (o2=='*' or o2=='/'))
    
    @staticmethod
    def perform_arithmetic(value1, value2, operator):
        result = 0
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
    def execute_expression(operand1, operand2, operator, fieldName):
        zoneList = []
        
        if operand1 is None:
            print ("There is no data for operand1.")
        if operand2 is None:
            print ("There is no data for operand2.")
        if operator is None:
            print ("There is no operator to perform the operation.")
        
        for itemOp1, itemOp2 in zip(operand1, operand2):
            newZone = Zone()
            newZone.id = itemOp1.id
            newZone.name = itemOp1.name

            if fieldName.upper() == 'TOTPROD':
                newZone.totProd = ExpressionData.perform_arithmetic(itemOp1.totProd, itemOp2.totProd, operator)

            if fieldName.upper() == 'TOTDEM':
                newZone.totDem = ExpressionData.perform_arithmetic(itemOp1.totDem, itemOp2.totDem, operator)
            
            if fieldName.upper() == 'PRODCOST':
                newZone.prodCost = ExpressionData.perform_arithmetic(itemOp1.prodCost, itemOp2.prodCost, operator)
            
            if fieldName.upper() == 'PRICE':
                newZone.price = ExpressionData.perform_arithmetic(itemOp1.price, itemOp2.price, operator)
            
            if fieldName.upper() == 'MINRES':
                newZone.minRes = ExpressionData.perform_arithmetic(itemOp1.minRes, itemOp2.minRes, operator)
            
            if fieldName.upper() == 'MAXRES':
                newZone.maxRes = ExpressionData.perform_arithmetic(itemOp1.maxRes, itemOp2.maxRes, operator)
            
            if fieldName.upper() == 'ADJUST':
                newZone.adjust = ExpressionData.perform_arithmetic(itemOp1.adjust, itemOp2.adjust, operator)
            
            zoneList.append(newZone)
            del newZone        
        
        return zoneList
from GeneralObject import GeneralObject

""" Zone Class"""
class Zone(GeneralObject):
    """ Init Method """
    def __init__(self):
        GeneralObject.__init__(self)
        self.totProd = 0.0
        self.totDem = 0.0
        self.prodCost = 0.0
        self.price = 0.0
        self.minRes = 0.0
        self.maxRes = 0.0
        self.adjust = 0.0
        
    def __del__(self):
        print (self.__class__.__name__, "destroyed")
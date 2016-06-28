""" GeneralObject Class"""
class GeneralObject(object):
    def __init__(self):
        self.id = None
        self.name = None
    
    def __del__(self):
        print (self.__class__.__name__, "destroyed")
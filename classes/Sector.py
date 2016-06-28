from GeneralObject import GeneralObject

""" Sector Class"""
class Sector(GeneralObject):
    def __init__(self):
        GeneralObject.__init__(self)
        self.zones = []
        
    def __del__(self):
        print (self.__class__.__name__, "destroyed")
 
    def add_zone(self, newZone):
        self.zones.append(newZone)

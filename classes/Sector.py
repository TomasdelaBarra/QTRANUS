# -*- coding: utf-8 -*-
from .GeneralObject import GeneralObject

""" Sector Class """
class Sector(GeneralObject):
    def __init__(self):
        """
            @summary: Constructor
        """
        GeneralObject.__init__(self)
        self.zones = []
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
 
    def add_zone(self, newZone):
        """
            @summary: Adds a new zone
            @param newZone: Zone to be added
            @type newZone: Zone object
        """
        self.zones.append(newZone)

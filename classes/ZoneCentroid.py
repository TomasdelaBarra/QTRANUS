# -*- coding: utf-8 -*-
from GeneralObject import GeneralObject

""" Zone Centroid """
class ZoneCentroid(GeneralObject):
    def __init__(self):
        """
            @summary: Constructor
        """
        GeneralObject.__init__(self)
        # Point(x,y) = (longitude, latitude)
        self.longitude = 0.0
        self.latitude = 0.0
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
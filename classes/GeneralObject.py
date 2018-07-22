# -*- coding: utf-8 -*-
""" GeneralObject Class """
class GeneralObject(object):
    def __init__(self):
        """
            @summary: Constructor
        """
        self.id = None
        self.name = None
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
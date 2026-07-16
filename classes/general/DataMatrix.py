# -*- coding: utf-8 -*-
from ..GeneralObject import GeneralObject

""" DataMatrix Class """
class DataMatrix(GeneralObject):
    def __init__(self):
        """
            @summary: Constructor
        """
        GeneralObject.__init__(self)
        self.data_matrix = None
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
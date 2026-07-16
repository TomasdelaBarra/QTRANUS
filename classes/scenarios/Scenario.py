# -*- coding: utf-8 -*-
from ..general.FileManagement import FileManagement
from .GeneralObject import GeneralObject
from .NetworkDataAccess import NetworkDataAccess
import numpy as np

class Scenario(object):
    def __init__(self):
        self.variables_dic = {}
        self.scenarios = []
        self.operators_dic = {}
        self.routes_dic = {}
        self.networ_matrices = []
        self.network_data_access = NetworkDataAccess()
        self.network_link_shape_location = None
        self.network_node_shape_location = None
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")

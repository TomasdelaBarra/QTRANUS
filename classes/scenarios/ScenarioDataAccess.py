# -*- coding: utf-8 -*-
from general.FileManagement import FileManagement
import csv, numpy as np
from general.QTranusMessageBox import QTranusMessageBox

class ScenarioDataAccess(object):
    def __init__(self):
        """
            @summary: Class constructor
        """
        self.variables_dic = {}
        self.scenarios = []
        self.operators_dic = {}
        self.routes_dic = {}
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
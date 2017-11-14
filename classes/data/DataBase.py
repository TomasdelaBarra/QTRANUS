# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from ..general.QTranusMessageBox import QTranusMessageBox
from DataBaseDataAccess import DataBaseDataAccess
import sys, os

class DataBase(object):
    def __init__(self):
        self.scenarios = []
        self.database_data_access = DataBaseDataAccess()
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")

    def create_new_data_base(self, path, fileName):
            
        if (self.database_data_access.create_data_base(path, fileName)):
            return True
        else:
            return False
    
    def extract_scenarios_file_from_zip(self, zipFilePath, outputPath):
        if(self.database_data_access.extract_file_from_zip(zipFilePath, 'Scenarios.csv', outputPath)):
            return True
        else:
            return False
        
    def save_db(self, path, dbFileName, newDbFileName, dbFile, matrix):
        return self.database_data_access.save_db(path, dbFileName, newDbFileName, dbFile, matrix)
        
    def create_backup_file(self, path, dbFile):
        return self.database_data_access.backup_file(path, dbFile)
        
    def create_new_scenario_row(self, scenariosMatrix, code, name, description, previous):
        return self.database_data_access.create_new_scenario_row(scenariosMatrix, code, name, description, previous)
        
    def save_new_scenario(self, path, code, name, description, previous):
        if(self.database_data_access.save_scenario(path, code, name, description, previous)):
            return True
        else:
            return False
    
    def get_scenarios_list(self, path):
        return self.database_data_access.get_scenarios_list(path)
    
    def get_scenarios_array(self, path):
        return self.database_data_access.get_scenarios_array(path)
    
    def remove_scenario_from_file(self, scenariosMatrix, scenarioCode):
        return self.database_data_access.remove_scenario(scenariosMatrix, scenarioCode)
    
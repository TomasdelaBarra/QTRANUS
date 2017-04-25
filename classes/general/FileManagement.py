import re
#import csv
import numpy as np

from os import listdir
from os.path import isfile, join
from DataMatrix import DataMatrix

""" FileManagement Class """
class FileManagement(object):
    
    @staticmethod
    def get_scenarios_from_filename(path, wildcard, extension):
        scenarios = []
        
        files = [f for f in listdir(path) if isfile(join(path, f))]
        fileName = re.compile(wildcard + extension)
        for fn in files:
            result = fileName.match(fn)
            if result != None:
                strFound = fn.find('.csv')
                scenarioId = fn[strFound - 3 : strFound]
                scenarios.append(scenarioId)
                
        return scenarios
    
    @staticmethod
    def get_np_matrix_from_csv(path, wildcard, scenario, extension):
        fileName = None
        matrix_result = None
        
        if path is None or path.strip() == '':
            return None
        
        if scenario is None or scenario.strip() == '':
            return None
        
        files = [f for f in listdir(path) if isfile(join(path, f))]
        fileName = re.compile(wildcard + scenario + extension)
    
        for fn in files:
            isValidFile = fileName.match(fn)
            if isValidFile != None:
                
                matrix_result = DataMatrix()
                npMatrix = np.genfromtxt(path + "/" + fn, delimiter = ',', skip_header = 0
                                , dtype = None , names = True)
                matrix_result.Id = scenario
                matrix_result.Name = scenario
                matrix_result.data_matrix = npMatrix
        
        return matrix_result
        
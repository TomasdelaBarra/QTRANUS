# -*- coding: utf-8 -*-
from .Scenario import Scenario
from .Sector import Sector
from .Zone import Zone

""" Indicator Class """
class Indicator:
    def __init__(self):
        """
            @summary: Constructor
        """
        self.scenarios = []
           
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def add_scenario(self, scenario):
        """
            @summary: Adds a new scenario
            @param scenario: Scenario to be added
            @type scenario: Scenario object
        """
        self.scenarios.append(scenario)
        
    def load_indicator_file(self, indicatorFile):
        """
            @summary: Loads file indicator
            @param indicatorFile: Indicator file
            @type indicatorFile: String
        """
        f = open(indicatorFile)
        fileData = f.readlines()
        scenario = Scenario()
        scenario = self.__read_file(fileData)
        self.add_scenario(scenario)
        
        f.close()
    
    """ Read File Method """
    def __read_file(self, fileData):
        """
            @summary: Reads indicator file
            @param fileData: File data
            @type fileData: String
            @return: Scenario object
        """
        newScenario = None
        newSector = None
        
        if fileData is not None:
            newScenario = Scenario()
            newScenario.id, newScenario.name = fileData[1].split(',')[0].strip(), fileData[1].split(',')[0].strip()
            
            fileDataLen = len(fileData)
            for i in range(1, fileDataLen):
                line = fileData[i].strip().split(',')
                 
                if newSector is None:
                    newSector = Sector()
                 
                # Is a new sector
                if newSector.id is None:
                    newSector.id = line[1].strip().split(' ')[0].strip()
                    newSector.name = line[1].strip().split(' ')[1].strip()
                    
                # Change of sector information
                if newSector.id != line[1].strip().split(' ')[0].strip():
                    newScenario.add_sector(newSector)
                    del newSector
                    newSector = Sector()
                    newSector.id = line[1].strip().split(' ')[0].strip()
                    newSector.name = line[1].strip().split(' ')[1].strip()               
                
                # Process file line information
                newZone = Zone()
                newZone.id = line[2].strip().split(' ')[0].strip()
                newZone.name = line[2].strip().split(' ')[1].strip()
                newZone.totProd = float(line[3].strip())
                newZone.totDem = float(line[4].strip())
                newZone.prodCost = float(line[5].strip())
                newZone.price = float(line[6].strip())
                newZone.minRes = float(line[7].strip())
                newZone.maxRes = float(line[8].strip())
                newZone.adjust = float(line[9].strip())
                 
                newSector.add_zone(newZone)
                del newZone
                
                if i == (fileDataLen - 1):
                    newScenario.add_sector(newSector)
                    del newSector
        
        return newScenario
        
from Scenario import Scenari
from Sector import Sector
from Zone import Zone

""" Indicator Class"""
class Indicator:
    def __init__(self):
        self.scenarios = []
           
    def __del__(self):
        print (self.__class__.__name__, "destroyed")
        
    def add_scenario(self, scenario):
        self.scenarios.append(scenario)
        
    def load_indicator_file(self, indicatorFile):
        f = open(indicatorFile)
        fileData = f.readlines()
        scenario = Scenari()
        scenario = self.__read_file(fileData)
        self.add_scenario(scenario)
        
        f.close()
        
    """ Read File Method """
    def __read_file(self, fileData):
        newScenario = None
        newSector = None
        
        if fileData is not None:
            newScenario = Scenari()
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
                newZone.totProd = line[3].strip()
                newZone.totDem = line[4].strip()
                newZone.prodCost = line[5].strip()
                newZone.price = line[6].strip()
                newZone.minRes = line[7].strip()
                newZone.maxRes = line[8].strip()
                newZone.adjust = line[9].strip()
                 
                newSector.add_zone(newZone)
                del newZone
                
                if i == (fileDataLen - 1):
                    newScenario.add_sector(newSector)
                    del newSector
        
        return newScenario
        
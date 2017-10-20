#!/usr/bin/env python

#===============================================================================
# Class telling the location of the tranus files and the path to tranus executable 
# files i.e. .o files in linux
# tranusbinpath = location of the Tranus executables
# workingdirectory = Tranus project location
# scenrioId = Tranus Project specific scenario ID
# projectID = Tranus Project Id 
# Project is the .tuz file that you have constructed using TUS and run atleast once
#===============================================================================
import subprocess
import os.path
from sys import stdout
import logging
import glob

class TranusConfig:
	"Class which defines tranus configuration parameters"

	
	def __init__(self, 	
				 tranusBinPath, 
			     workingDirectory,
				 scenarioId):

		self.tranusBinPath 	= tranusBinPath #CHANGE THIS PATH ACCORDINGLY.   
		#check if Tranus binaries are in there:
		if not os.path.isfile(os.path.join(tranusBinPath,'lcal.exe')) or not os.path.isfile(os.path.join(tranusBinPath,'pasos.exe')) :
			logging.error('Tranus binaries not found in : %s'%tranusBinPath)

		self.workingDirectory 	= workingDirectory#DIRECTORY OF TRANUS MODEL
		self.scenarioId 		= scenarioId#ID OF THE SCENARIO EX 00A
		self.convFactor 		= "0.0001"
		self.nbIterations 		= "250"
		self.tranusConf_file	= 'W_TRANUS.CTL'
		self.obs_file = glob.glob(os.path.join(self.workingDirectory,'W_*.L0E'))[0]
		self.zone_file = glob.glob(os.path.join(self.workingDirectory,'W_*.Z1E'))[0]
		path_policy = os.path.join(self.workingDirectory,self.scenarioId)
		self.param_file = glob.glob(os.path.join(path_policy,'W_*.L1E'))[0]
		self.param_transport = glob.glob(os.path.join(path_policy,'W_*.P0E'))[0]
		
		
	def numberingZones(self):
		'''functions that returns the list number of a zone. Takes into account only first level internal zones'''
		fs = open(os.path.join(self.workingDirectory,self.zone_file), 'r')
		logging.debug("Reading zones from file : %s"%os.path.join(self.workingDirectory,self.zone_file) )
		ll = fs.readlines()
		for i in range(0,len(ll)):
			ll[i] = ll[i]#.decode("iso-8859-1")
		numbersZ1E = []
		numbersZ1Eext = []
		n=5  

		'''PRETTY MUCH BRUTE FORCE IMPLEMENTATION OF HOW TO READ THE ZONE NUMBERING FROM THE .Z1E FILE.'''
		while n<len(ll)-1:
			while ll[n][1:3]!="--":
				numbersZ1E.append(int(str.split(ll[n])[0]))                   
				n+=1             
			n+=6		#skiping second level zones
			while ll[n][1:3]!="--":
				numbersZ1Eext.append(int(str.split(ll[n])[0]))                  
				n+=1              
		return numbersZ1E, numbersZ1Eext

	def numberingSectors(self):
		'''functions that returns the list number of sectors ''' 

		fs = open(os.path.join(self.workingDirectory,self.scenarioId,self.param_file), 'r')
		logging.debug("Reading sectors from file : %s"%os.path.join(self.workingDirectory,self.scenarioId,self.param_file) )
		ll=fs.readlines()
		for i in range(0,len(ll)):
			ll[i]=ll[i]#.decode("iso-8859-1")
		numbersL1E=[]
		n=11  
		while n<len(ll):
			while ll[n][1:3]!="--":
				numbersL1E.append(int(str.split(ll[n])[0]))                   
				n+=1
			#n+=3               
			n=len(ll)
		return numbersL1E

	
    
# Testing module
if __name__ == '__main__':
    log_level = logging.DEBUG
    logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(message)s',
                        level  = log_level,
                        stream = stdout)
    t = TranusConfig()
    print "TRANUS binaries directory                    : ", t.tranusBinPath
    print "Directory where is located the .tuz file     : ", t.workingDirectory
    print "ID of the project that we want to simulate   : ", t.projectId
    print "ID of the scenario that we want to simulate  : ", t.scenarioId
    print "Parameters file                              : ", t.param_file
    print "Observations file                            : ", t.obs_file
    print "Zone file                                    : ", t.zone_file
    print "Convergence factor                           : ", t.convFactor
    print "Number of iterations                         : ", t.nbIterations

    from LcalInterface import *
    interface = LcalInterface(t)
	
    interface.runTranus(10)
    from LCALparam import *
    param = LCALparam(t)
    
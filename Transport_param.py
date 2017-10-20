import logging
import sys
import os.path
from TranusConfig import *

class TransParam:
    def __init__(self,trans_mode_id,trans_op_id,trans_cat_id):
        
        self.trans_mode= trans_mode_id
        self.trans_op = trans_op_id
        self.trans_cat = trans_cat_id
 
        
        
def read_P0E(tConf):
        
    list_trans_mode = []
    list_trans_op = []
    list_trans_cat = []
   
    filename=os.path.join(tConf.workingDirectory,tConf.scenarioId,tConf.param_transport)     
    filer = open(filename, 'r')
    lines = filer.readlines()
    filer.close()
    length_lines = len(lines)
 
    for i in range(length_lines):
        lines[i]=str.split(lines[i])
        
    string = "2.1"
    for line in range(len(lines)):
        if (lines[line][0] == string):
            break
     
    end_of_section = "*-"        
    line+=2
    while lines[line][0][0:2] != end_of_section:   
        list_trans_mode.append(lines[line][0])
        line+=1
        
    string = "2.2"
    for line in range(len(lines)):
        if (lines[line][0] == string):
            break
     
    end_of_section = "*-"        
    line+=2
    while lines[line][0][0:2] != end_of_section:   
        list_trans_op.append(lines[line][0])
        line+=1
        
    string = "3.0"
    for line in range(len(lines)):
        if (lines[line][0] == string):
            break
     
    end_of_section = "*-"        
    line+=2
    while lines[line][0][0:2] != end_of_section:   
        list_trans_cat.append(lines[line][0])
        line+=1
    
    
    result = TransParam(list_trans_mode,list_trans_op,list_trans_cat )
    return result

  
        
   
    
        
 


        


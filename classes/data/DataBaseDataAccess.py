# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from ..general.QTranusMessageBox import QTranusMessageBox
from ..general.FileManagement import FileManagement
import zipfile, csv, sys, os
import re, numpy as np, time
from os import listdir
from os.path import isfile, join
from DBFiles import *

class DataBaseDataAccess(object):
    def __init__(self):
        self.scenariosDBFileName = 'Scenarios.csv'
        self.dbFiles = []
        self.dbFiles.append(self.scenariosDBFileName)
        
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def create_data_base(self, path, fileName):
        dbCreated = False
        newZipFile = None
        try:
            
            newZipFile = zipfile.ZipFile(path + "\\" + fileName + ".zip", "w")
            newZipFile.close()
            newZipFile = zipfile.ZipFile(path + "\\" + fileName + ".zip", "a")
            if (self.__create_empty_scenarios_file(path)):
                newZipFile.write(os.path.join(path, self.scenariosDBFileName), os.path.basename(os.path.join(path, self.scenariosDBFileName)))
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenario file", "Scenarios.csv file couldn't be created.", ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
                messagebox.exec_()
                print("Scenarios.csv file couldn't be created.")

            dbCreated = True
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "New DB", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            dbCreated = False
        finally:
            newZipFile.close()
            del newZipFile
            
        return dbCreated
    
    def extract_file_from_zip(self, zipFilePath, fileName, outputPath):
        """
            
        """
        dbZipfile = None
        fileExtracted = False
        try:
            print(zipFilePath)
            print("output: " + outputPath)
            dbZipfile = zipfile.ZipFile(zipFilePath, 'r')
            dbZipfile.extract(fileName, outputPath)
            fileExtracted = True
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Extract File", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            fileExtracted = False
        finally:
            del dbZipfile
        
        return fileExtracted
    
    def save_db(self, path, dbFileName, newDbFileName, dbFile, matrix):
        dbSaved = False
        newZipFile = None
        try:
            files = [f for f in listdir(path) if isfile(join(path, f))]
            stringList = (newDbFileName.replace('/', '\\')).split('\\')
            for item in stringList: 
                if re.search('.zip', item, re.IGNORECASE):
                    if (item + '.tmp') in files:
                        # We rename the current DB zip file
                        os.remove(dbFileName + '.tmp')
                        break
            # We rename the file to create the temp file
            if dbFileName == newDbFileName:
                os.rename(dbFileName, dbFileName + '.tmp')
                print(time.strftime('%Y/%m/%d %H:%M:%S'))
            
            # We create the Db file with the same name as the current one
            newZipFile = zipfile.ZipFile(newDbFileName, "w")
            newZipFile.close()
            
            if(dbFile == DBFiles.Scenarios):
                self.__create_empty_scenarios_file(path)
                if matrix is not None:
                    if matrix.size > 0:
                        with open(os.path.join(path, self.scenariosDBFileName), 'wb') as outFile:
                            newFile = csv.writer(outFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            newFile.writerow(['ScenarioCode', 'PreviousScenarioCode', 'Name', 'Description'])
                            
                            for item in np.nditer(matrix):
                                newFile.writerow([item.item(0)[0], item.item(0)[1], item.item(0)[2], item.item(0)[3]])
                                                
                        
                newZipFile = zipfile.ZipFile(newDbFileName, "a")
                newZipFile.write(os.path.join(path, self.scenariosDBFileName), os.path.basename(os.path.join(path, self.scenariosDBFileName)))
                dbSaved = True
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Save DB", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            dbSaved = False
        finally:
            if newZipFile is not None:
                newZipFile.close()
                del newZipFile
            
        return dbSaved    
            
        
    def backup_file(self, path, dbFile):
        if(dbFile == DBFiles.Scenarios):
            source = os.path.join(path, self.scenariosDBFileName)
            destination = os.path.join(path, 'Scenarios.bkp')
            FileManagement.copy_file(source, destination)
            
        
    def __create_empty_scenarios_file(self, path):
        fileCreated = False
        csvFile = None
        newFile = None
        try:
            csvFile = open(os.path.join(path, self.scenariosDBFileName), "wb")
            
            newFile = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            newFile.writerow(['ScenarioCode', 'PreviousScenarioCode', 'Name', 'Description'])

            fileCreated = True
        except:
            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Scenario file", "Unexpected error: {0}".format(sys.exc_info()[0]), ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
            messagebox.exec_()
            print("Unexpected error:", sys.exc_info()[0])
            fileCreated = False
        finally:
            del newFile
            csvFile.close
            del csvFile
        
        return fileCreated
    
    def get_scenarios_list(self, scenariosMatrix):
        scenarios_list = []
        if scenariosMatrix is not None:
            if scenariosMatrix.size > 0:
                for item in np.nditer(scenariosMatrix):
                    scenario = []
                    scenario.append(item.item(0)[0])
                    scenario.append(item.item(0)[2])
                    scenarios_list.append(scenario)
                            
        return scenarios_list
    
    def get_scenarios_array(self, path):
        npScenariosMatrix = None
        npScenariosMatrix = self.__get_scenarios_from_file(path) 
        if npScenariosMatrix is not None:
            if npScenariosMatrix.size > 0:
                return npScenariosMatrix
                            
        return None
    
    def __get_scenarios_from_file(self, path):
        npScenariosMatrix = None 
        files = [f for f in listdir(path) if isfile(join(path, f))]
        fileName = re.compile(self.scenariosDBFileName)
    
        for fn in files:
            isValidFile = fileName.match(fn)
            if isValidFile != None:
                npScenariosMatrix = np.genfromtxt(path + "/" + fn, delimiter = ',', skip_header = 0,
                                    dtype = [('ScenarioCode', 'S12'), ('PreviousScenarioCode', 'S12'), ('Name', 'S32'), ('Description', 'S100')], names = True)
                npScenariosMatrix.sort(order='ScenarioCode')

                break
                
        return npScenariosMatrix
    
    def add_new_scenario(self, scenariosMatrix, code, name, description, previous):
        
        if scenariosMatrix is not None:
            if scenariosMatrix.size > 0:
                existingCode = scenariosMatrix[(scenariosMatrix['ScenarioCode'] == code)]
                
                if existingCode is not None:
                    if existingCode.size > 0:
                        messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Add scenario", "The scenario code already exists.", ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
                        messagebox.exec_()
                        print("The scenario code already exists.")
                        return None
        
        rowData = np.array([(code, previous, name, description)],                           
                dtype = [('ScenarioCode', 'S12'), ('PreviousScenarioCode', 'S12'), ('Name', 'S32'), ('Description', 'S100')])
        
        if scenariosMatrix is None:
            return rowData 
        else:
            return np.concatenate((scenariosMatrix, rowData))
    
    def save_scenario(self, path, code, name, description, previous):
        
        files = [f for f in listdir(path) if isfile(join(path, f))]
        fileName = re.compile(self.scenariosDBFileName)
    
        for fn in files:
            isValidFile = fileName.match(fn)
            if isValidFile != None:
                npScenariosMatrix = np.genfromtxt(path + "/" + fn, delimiter = ',', skip_header = 0, dtype = None , names = True)
                if npScenariosMatrix.size > 0:
                    existingCode = npScenariosMatrix[(npScenariosMatrix['ScenarioCode'] == code)]
                    
                    if existingCode is not None:
                        if existingCode.size > 0:
                            messagebox = QTranusMessageBox.set_new_message_box(QtGui.QMessageBox.Warning, "Add scenario", "The scenario code already exists.", ":/plugins/QTranus/icon.png", None, buttons = QtGui.QMessageBox.Ok)
                            messagebox.exec_()
                            print("The scenario code already exists.")
                            return False
                
                
                csvFile = open(path + "/" + fn, "ab")
                newFile = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                newFile.writerow([code, previous, name, description])
                
                del newFile
                csvFile.close()
                del csvFile
            
            
        return True
    
    def remove_scenario(self, scenariosMatrix, scenarioCode):
        if scenariosMatrix is not None:
            if scenariosMatrix.size > 0:
                existingCode = scenariosMatrix[(scenariosMatrix['ScenarioCode'] == scenarioCode)]
                if existingCode is not None:
                    if existingCode.size > 0:
                        resultScenarios = scenariosMatrix[(scenariosMatrix['ScenarioCode'] != scenarioCode)]
                        return True, resultScenarios

        return False, None
# -*- coding: utf-8 -*-
import re
import numpy as np
import zipfile
import shutil

from os import listdir
from os.path import isfile, join
from xml.etree import ElementTree as XMLEt
from .DataMatrix import DataMatrix
from .Helpers import Helpers as HP

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
        
    @staticmethod
    def create_zip_file(path, fileName):
        z = zipfile.ZipFile(path + "\\" + fileName + ".zip", "w")
    
    @staticmethod
    def copy_file(sourceFile, destinationFile):
        shutil.copy(sourceFile,destinationFile)

    
    @staticmethod
    def create_xml_file(layerName, layerId, scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText, shpField):
        """
        @summary: Create Qtranus Project XML file 
        @param layerName: Layer Name
        @type layerName: String
        @param layerId: Layer Name
        @type layerId: String
        @param scenariosExpression: Scenarios expression
        @type scenariosExpression: String
        @param fieldName: Field name
        @type fieldName: String
        @param sectorsExpression: Sectors expression
        @type sectorsExpression: String
        @param projectPath: Path Qtranus Workspace
        @type projectPath: String
        @return: Boolean result of file creation
        """

        data = XMLEt.Element("data")
        project = XMLEt.SubElement(data, "project")
        project.set("id", "123123_123123")

        layer = XMLEt.SubElement(project, "layer")
        layer.set("name", layerName)
        layer.set("id", layerId)
        layer.set("sectors_expression", sectorsExpressionText)
        layer.set("scenario", str(scenariosExpression))
        layer.set("type", "zones")
        layer.set("field", fieldName)
        layer.set("id_field_name", shpField)

        HP().indent(data)

        tree = XMLEt.ElementTree(data)

        try:
            tree.write(projectPath+"/.qtranus", xml_declaration=True, encoding='utf-8', method="xml")
            return True
        except EnviromentError as e:
            print(e)
            return False

    @staticmethod
    def find_layer_data(projectPath, layerId):
        try:
            tree = XMLEt.parse(projectPath+'/.qtranus')
            root = tree.getroot()
        except EnviromentError as e:
            print(e)
            return False

        name = root.findall("./project/layer/[@id='{}']".format(layerId))[0].attrib['name']
        field = root.findall("./project/layer/[@id='{}']".format(layerId))[0].attrib['field']
        scenario = root.findall("./project/layer/[@id='{}']".format(layerId))[0].attrib['scenario']
        expression = root.findall("./project/layer/[@id='{}']".format(layerId))[0].attrib['sectors_expression']
        id_field_name = root.findall("./project/layer/[@id='{}']".format(layerId))[0].attrib['id_field_name']
        return expression, field, name, scenario, id_field_name

    @staticmethod
    def remove_layer_element(projectPath, layerId):
        try:
            tree = XMLEt.parse(projectPath+'/.qtranus')
            root = tree.getroot()
        except EnviromentError as e:
            print(e)
            return False

        for parent in root.findall("project"):
            for country in parent.findall("./layer/[@id='{}']".format(layerId)):
                parent.remove(country)
        
        tree.write(projectPath+'/.qtranus', xml_declaration=True, encoding='utf-8', method="xml")

    @staticmethod
    def if_exist_layer(projectPath, layerId):
        try:
            tree = XMLEt.parse(projectPath+'/.qtranus')
            root = tree.getroot()

            if root.findall("./project/layer/[@id='{}']".format(layerId)):
                return True
            else:
                return False
        except EnviromentError as e:
            print(e)
            return False


    @staticmethod
    def update_xml_file(layerName, layerId, scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText):
        try:
            tree = XMLEt.parse(projectPath+'/.qtranus')
            root = tree.getroot()
            for valor in root.findall("./project/layer/[@id='{}']".format(layerId)):
                valor.attrib['field'] = fieldName
                valor.attrib['scenario'] = str(scenariosExpression)
                valor.attrib['sectors_expression'] = sectorsExpressionText

            tree.write(projectPath+'/.qtranus', xml_declaration=True, encoding='utf-8', method="xml")

        except Exception as e: 
            print(e)
            return False

    @staticmethod
    def add_layer_xml_file(layerName, layerId, scenariosExpression, fieldName, sectorsExpression, projectPath, sectorsExpressionText, shpField):
        try:
            tree = XMLEt.parse(projectPath+'/.qtranus')
            root = tree.getroot()
            project =  root.find("./project")
            layer = XMLEt.SubElement(project, "layer")
            layer.set("name", layerName)
            layer.set("id", layerId)
            layer.set("sectors_expression", sectorsExpressionText)
            layer.set("scenario", str(scenariosExpression))
            layer.set("type", "zones")
            layer.set("field", fieldName)
            layer.set("id_field_name", shpField)

            tree.write(projectPath+'/.qtranus', xml_declaration=True, encoding='utf-8', method="xml")
            
        except Exception as e: 
            print(e)
            return False

    @staticmethod
    def if_exist_xml_layers(projectPath):
        return isfile(projectPath+"/.qtranus")
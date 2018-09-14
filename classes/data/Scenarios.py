# -*- coding: utf-8 -*-
from .Scenario import Scenario
import numpy as np

class Scenarios(object):
    root = None
    def __init__(self):
        self.root = None
        
    def load_data(self, npScenariosMatrix):
        scenarios = []
        nodes = {}
        if npScenariosMatrix is not None:
            if npScenariosMatrix.size > 0:
                nodes = self.__get_dictionary(npScenariosMatrix)
                self.root = self.__create_tree(nodes)


    def __get_dictionary(self, npScenariosMatrix):
        nodes = {}
        if npScenariosMatrix is not None:
            if npScenariosMatrix.size > 0:
                for item in np.nditer(npScenariosMatrix):
                    nodes[item.item(0)[0]] = {
                        'name': item.item(0)[2],
                        'previous': item.item(0)[1] if item.item(0)[1].strip() != '' else None }
                    
        return nodes
    
    def __create_tree(self, nodes):
        scenarios = {}
        def get_or_create(code, data):
            if code is None:
                return None
            if code in scenarios:
                return scenarios[code]
            else:
                previous = data['previous']
                prevous_data = nodes[previous] if previous is not None else {}
                scenarios[code] = Scenario(code, data['name'], get_or_create(previous, prevous_data))
                return scenarios[code]
        root = None
        for code, data in nodes.items():
            node = get_or_create(code, data)
            if node.previous is None:
                root = node
        return root
            
        
# -*- coding: utf-8 -*-
from ..GeneralObject import GeneralObject

class Scenario(GeneralObject):
    #
    previous = None
    children = None
    
    def __init__(self, code, name, previous):
        GeneralObject.__init__(self)
        self.id = code
        self.name = name
        self.previous = previous
        self.children = []
        if self.previous is not None:
            self.previous.children.append(self)   
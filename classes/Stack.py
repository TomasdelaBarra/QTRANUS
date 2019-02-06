# -*- coding: utf-8 -*-
""" Stack Class """
class Stack(object):
    def __init__(self):
        """
            @summary: Constructor
        """
        self.data = []
        self.tp = 0

    def push(self, value):
        self.data.append(value)
        self.tp = self.tp + 1

    def pop(self):
        topval = self.data.pop()     
        self.tp = self.tp - 1
        return topval

    def empty(self):
        return self.tp == 0

    def top(self):
        return self.data[self.tp - 1]

    def __str__(self):
        return str(self.data)
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
# -*- coding: utf-8 -*-
from .GeneralObject import GeneralObject

""" Scenario Class """
class Scenario(GeneralObject):
	def __init__(self):
		"""
            @summary: Constructor
        """
		GeneralObject.__init__(self)
		self.sectors = []
	
	def __del__(self):
		"""
            @summary: Destroys the object
        """
		print (self.__class__.__name__, "destroyed")
	
	def add_sector(self, newSector):
		"""
			@summary: Adds a new sector
			@param newSector: Sector to be added
			@type newSector: Sector object
		"""
		self.sectors.append(newSector)
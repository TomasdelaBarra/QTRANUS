from GeneralObject import GeneralObject

""" Scenario Class"""
class Scenari(GeneralObject):
	def __init__(self):
		GeneralObject.__init__(self)
		self.sectors = []
	
	def __del__(self):
		print (self.__class__.__name__, "destroyed")
	
	def add_sector(self, newSector):
		self.sectors.append(newSector)
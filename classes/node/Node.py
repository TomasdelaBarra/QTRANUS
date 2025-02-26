# -*- coding: utf-8 -*-
import numpy as np

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from qgis.core import  QgsPointXY, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFeature, QgsSymbolLayerRegistry, QgsSingleSymbolRenderer, QgsRendererRange, QgsStyle, QgsGraduatedSymbolRenderer , QgsSymbol, QgsVectorLayerJoinInfo, QgsLineSymbolLayer, QgsSimpleLineSymbolLayer, QgsMapUnitScale, QgsSimpleLineSymbolLayer, QgsLineSymbol, QgsMarkerLineSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsWkbTypes, QgsPoint, QgsFeatureRequest


class Node(object):
	def __init__(self):
		self.variables_dic = {}
		self.scenarios = []
		self.operators_dic = {}
		self.routes_dic = {}
		self.networ_matrices = []
		self.network_link_shape_location = None
		self.network_node_shape_location = None

	def __del__(self):
		"""
		@summary: Destroys the object
		"""
		print (self.__class__.__name__, "destroyed")


	@staticmethod
	def addNodeFeatureShape(layerId, xCoordenate, yCoordenate, nodeId, name, typeNode, nodeShapeFields=None):
		"""
		@summary: Build link to Shape Network
		@param originPoint: xCoordenate
		@type originPoint: QgsPointXY
		@param destinationPoint: Layer name
		@type destinationPoint: QgsPointXY
		@param originIdNode: Origin Node
		@type originIdNode: Integer
		@destinationIdNode: Destination Node
		@type destinationIdNode: Integer
		@param twoWay: Flag to mark two-way links
		@type twoWay: Integer
		@return: Result of the layer creation
		"""
		try:
			if not nodeShapeFields:
				return False
				raise Exception("networkShapeFields is None")

			project = QgsProject.instance()
			layer = project.mapLayer(layerId)
			fields = [value.name() for value in layer.fields()]
			values = [None] * len(fields)
			values[fields.index(nodeShapeFields['id'])] = nodeId
			values[fields.index(nodeShapeFields['name'])] = name
			values[fields.index(nodeShapeFields['typeNode'])] = typeNode
			values[fields.index(nodeShapeFields['x'])] = xCoordenate
			values[fields.index(nodeShapeFields['y'])] = yCoordenate
			# print(values, "type: "+str(typeNode), "Coordenadas ", xCoordenate, yCoordenate, nodeShapeFields)
			layer.startEditing()

			geom = QgsGeometry()
			geom.addPoints([QgsPoint(QgsPointXY(float(xCoordenate), float(yCoordenate)))], QgsWkbTypes.PointGeometry)

			feat = QgsFeature()
			feat.setGeometry(geom)
			feat.setAttributes(values)
			#feat.setAttributes(values)
			layer.dataProvider().addFeature(feat)
			
			layer.commitChanges()
			
			return True
		except:
		    return False
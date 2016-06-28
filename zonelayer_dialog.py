
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *

from .scenarios_model import ScenariosModel
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'zonelayer.ui'))

class ZoneLayerDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(ZoneLayerDialog, self).__init__(parent)

        self.setupUi(self)

        self.project = parent.project

        self.base_scenario = self.findChild(QtGui.QComboBox, 'base_scenario')
        self.sectors = self.findChild(QtGui.QListWidget, 'sectors')

        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.reload_scenarios()
        
        self.layerName = self.findChild(QtGui.QLineEdit, 'layerName')
        self.expression = self.findChild(QtGui.QLineEdit, 'expression')
        self.baseScenario = self.findChild(QtGui.QComboBox, 'base_scenario')

        self.fields = self.findChild(QtGui.QComboBox, 'comboField')
        
        self.buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')
        self.buttonBox.accepted.connect(self.ready)
        #self.zones_shape_btn.clicked.connect(self.select_shape(self.select_zones_shape))
        
        self.proj = QgsProject.instance() 

        self.baseScenario.connect(self.baseScenario,SIGNAL("currentIndexChanged(int)"),self.scenarioChanged)

        #self.fill_base_scenario()
        #self.fill_sectors()
        self.__load_scenarios_combobox()
        self.__load_sectors_combobox()
        self.__load_fields_combobox()

    def scenarioChanged(self, newIndex):
        pass
#         self.fields.clear()
#         currentScenarioId = self.baseScenario.currentText()
# 
#         if currentScenarioId in self.project.indicators:
#             scenario = self.project.indicators[currentScenarioId]
#             for field in scenario.fields:  
#                 self.fields.addItem(field)
#         else:
#             print ("Error")


        
    def get_layers_group(self):
        group_name = 'QTRANUS' # self['layers_group_name'] or 'QTRANUS'
        layers_group = self.proj.layerTreeRoot().findGroup(group_name)
        if layers_group is None:
            layers_group = self.proj.layerTreeRoot().addGroup(group_name)
        return layers_group
        
        
    def ready(self):  # called when accept button is clicked

        print "ready?"
        if self.project.checkExpression(self.expression.text(), str(self.fields.currentText()), str(self.baseScenario.currentText())):
            print "yes"
            self.project.addLayer(self.layerName.text(), self.expression.text(), str(self.baseScenario.currentText()), str(self.fields.currentText()))
        else:
            print "no"
            pass

            # show some message here!
    
        # registry = QgsMapLayerRegistry.instance()
        
        # #self.lineLayer = QgsVectorLayer("LineString", name, "memory") 
        # layer = QgsVectorLayer("c:/swindon/swin-zon.shp", 'Zonas', 'memory')
        
        # pr = layer.dataProvider()
        # pr.addAttributes([QgsField("test", QVariant.Double)])
        # layer.updateFields()
        
        # iter = layer.getFeatures()
        # for feature in iter:
            # att = key
            # #feature[att] = 666
            # #print(feature.id)
            # print(feature[0])
            # value = table[str(int(feature[0]))]
            # pr.changeAttributeValues({feature.id() : {pr.fieldNameMap()[att] : value}})
            # i = i + 1
            
            
        # #layer.startEditing()            
        # #layer.addAttribute(QgsField("ComputedValue", QVariant.Double))
        # #layer.updateFields()        
        # #layer.changeAttributeValue(7, fieldIndex, value)
        
      # #  newFeature = QgsFeature()
        
        # #iter = layer.getFeatures()
        # #for feature in iter:
        # #    feature['computedValue'] = 666
            # #feature.setAttributes([feature[0], feature[1], feature[2], feature[3], 666])
            
        # #layer.commitChanges()
        # #layer.updateExtents()
            
        # iter = layer.getFeatures()    
        # for feature in iter:
            # print(str(feature[0])+"  "+str(feature[1])+"  "+str(feature[2])+"  "+str(feature[3])+" "+str(feature[key]))
            
        # #1/0
        
        
        # group = self.get_layers_group()
        # registry.addMapLayer(layer)  
        # group.insertLayer(0, layer)

    
        #shp = 
        #fields = QgsField("Atributo", QVariant.Double)
        #writer = QgsVectorFileWriter(shp, "CP1250", fields, poly_provider.geometryType(), poly_layer.crs(), "ESRI Shapefile")
        #del writer
        #layer = QgsVectorLayer(shp, "contrib_area","ogr")
        #dp = layer.dataProvider()
        #features = get10Features()
        #dp.addFeatures(features)

    
        #with open('c:/freelancerprojects/tranus/log.txt', 'a') as f:
        #    f.write('foo')

    def reload_scenarios(self):
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)

    def fill_base_scenario(self, root=None):
        if root is None:
            root = self.project.tranus_project.scenarios.root

        indicators = self.project.indicators
        if root.code not in indicators:
            return

        self.base_scenario.addItem(root.code)

        for child in root.children:
            self.fill_base_scenario(child)

    def fill_sectors(self):
        scenario = self.project.tranus_project.scenarios.get_scenario(self.base_scenario.currentText())
        self.sectors.clear()

        for sector in scenario.get_sectors():
            self.sectors.addItem(sector)
            
    def __load_scenarios_combobox(self):
        items = self.project.map_data.get_sorted_scenarios()
        self.base_scenario.addItems(items)
        
    def __load_sectors_combobox(self):
        items = self.project.map_data.get_sorted_sectors()
        self.sectors.addItems(items)
        
    def __load_fields_combobox(self):
        items = self.project.map_data.get_sorted_fields()
        self.fields.addItems(items)

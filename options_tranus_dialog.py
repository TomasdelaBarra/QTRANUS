# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OptionsTRANUSDialog
                                 A QGIS plugin
 This plugin automates the execution of TRANUS programs.
                             -------------------
        begin                : 2017-02-23
        git sha              : $Format:%H$
        copyright            : (C) 2017 by STEEP Inria
        email                : emna.jribi@inria.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import logging
import sys
from PyQt4.Qt import QMessageBox, QVariant
from PyQt4 import QtGui, uic,QtCore,Qt
from PyQt4.QtCore import QSettings
from .scenarios_model import ScenariosModel
import launch_tranus_dialog 
import inspect




FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Options_TRANUS_dialog_base.ui'))


class OptionsTRANUSDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self,project,settings,tranus_project,tranus_binaries,parent=None):
        """Constructor."""
        super(OptionsTRANUSDialog, self).__init__(parent)

        self.setupUi(self)
       
        
        self.project = project
        
        self.settings = settings
        self.tranus_project = tranus_project
        self.tranus_binaries = tranus_binaries
    
        
    
        self.help = self.findChild(QtGui.QPushButton, 'btn_help')
        self.layers_group_name = self.findChild(QtGui.QLineEdit, 'layers_group_name')
        self.tranus_workspace = self.findChild(QtGui.QLineEdit, 'tranus_workspace')
        self.tranus_workspace_btn = self.findChild(QtGui.QToolButton, 'tranus_workspace_btn')
        self.load_scenarios_btn = self.findChild(QtGui.QPushButton, 'btn_load_scenarios')
        self.tranus_bin_path = self.findChild(QtGui.QLineEdit, 'tranus_bin_path')
        self.tranus_bin_path_btn = self.findChild(QtGui.QToolButton, 'tranus_bin_path_btn')
        self.scenarios = self.findChild(QtGui.QTreeView, 'scenarios')
        self.close_btn = self.findChild(QtGui.QPushButton, 'btn_close')
        self.launch_btn = self.findChild(QtGui.QCommandLinkButton, 'btn_launch')
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

         # Control Actions
        self.help.clicked.connect(self.open_help)
        self.tranus_workspace_btn.clicked.connect(self.select_tranus_workspace)
        self.load_scenarios_btn.clicked.connect(self.load_scenarios)
        self.tranus_bin_path_btn.clicked.connect(self.select_bin_path)
        self.close_btn.clicked.connect(self.close)
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self.launch_options_TRANUS)
        
        self.checked_list = []
        self.count_check = 0
        
        self.reload_scenarios()
             

    def open_help(self):
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"help\Tranusprograms.pdf")
        os.startfile(file)
                  
    
    def save_settings(self):     
        
        self.settings.setValue("tranus_project",self.tranus_workspace.text())
        self.settings.setValue("tranus_binaries",self.tranus_bin_path.text())
    
             
    def save_layers_group_name(self):
        """
            @summary: Saves layer group name
        """
        self.project['project_name'] = self.layers_group_name.text()

    def select_tranus_workspace(self):
 
        folder = QtGui.QFileDialog.getExistingDirectory(self, "Select directory")
        if folder:
            self.tranus_project = folder
            self.tranus_workspace.setText(self.tranus_project)
            self.save_settings()
                                       
    def load_scenarios(self):
          
        if not self.project.load_tranus_folder(self.tranus_project):
            self.tranus_workspace.setText('')
            self.save_settings()
            QMessageBox.warning(None, "Invalid Tranus project", "Please select a valid workspace")
            print "Invalid Tranus project , Please select a valid workspace"
                    
        self.reload_scenarios()
        self.activate_launch_button()     
              
    def select_bin_path(self):
        
        self.tranus_binaries =  QtGui.QFileDialog.getExistingDirectory(self, "Select directory")
        if self.tranus_binaries:
            self.tranus_bin_path.setText(self.tranus_binaries)
            if not os.path.isfile(os.path.join(self.tranus_binaries,'lcal.exe')) or not os.path.isfile(os.path.join(self.tranus_binaries,'pasos.exe')) :
                QMessageBox.warning(None, "Tranus binaries error", "Tranus binaries not found in : %s"%self.tranus_binaries)
                print'Tranus binaries not found in : %s'%self.tranus_binaries
                self.tranus_bin_path.setText('')
            self.save_settings()
   
              
    def reload_scenarios(self):
        
        self.scenarios_model = ScenariosModel(self)
        self.scenarios.setModel(self.scenarios_model)
        self.scenarios.setExpanded(self.scenarios_model.indexFromItem(self.scenarios_model.root_item), True)
        
        
    def show(self):
        
        self.project.load()
        
        if self.project['project_name']:
            self.layers_group_name.setText(self.project['project_name'])
        else:
            self.layers_group_name.setText('Tranus Options')
            self.layers_group_name.selectAll() 
        if self.project.tranus_project:
            self.tranus_workspace.setText(self.project.tranus_project.path)
                 
    def reinitialise_checked_list(self):
        self.checked_list=[]   
        
    def activate_launch_button(self):
    
        model = self.scenarios.model()
        model.itemChanged.connect(self.check_configure)
        
    def launch_options_TRANUS(self):

        self.get_checked_list()
        dialog = launch_tranus_dialog.LaunchTRANUSDialog(self.checked_list,self.tranus_project,self.tranus_binaries,parent=self) 
        dialog.show()
        result = dialog.exec_()
        self.reinitialise_checked_list()
    
    def get_checked_list(self): 
             
        model = self.scenarios.model()
        checked_indexes = model.match(model.index(0, 0), QtCore.Qt.CheckStateRole,QtCore.Qt.Checked, -1,QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        
        for index in checked_indexes:
                
            item = model.itemFromIndex(index)
            item_text = item.text()
            self.checked_list.append(item_text)
        return self.checked_list
         
    def check_configure(self,item):
        
        model = self.scenarios.model()
        index = model.indexFromItem(item)
        
        if index.data(QtCore.Qt.CheckStateRole) != index.data(QtCore.Qt.UserRole + QtCore.Qt.CheckStateRole):
            if index.data(QtCore.Qt.CheckStateRole)!= QtCore.Qt.Unchecked :
                self.count_check+=1
                model.setData(index,index.data(QtCore.Qt.CheckStateRole),QtCore.Qt.UserRole + QtCore.Qt.CheckStateRole)
            else :
                self.count_check-=1
                model.setData(index,index.data(QtCore.Qt.CheckStateRole),QtCore.Qt.UserRole + QtCore.Qt.CheckStateRole)
                
        self.launch_btn.setEnabled(self.count_check>0 and self.tranus_bin_path.text() !='' and self.project.is_valid())
    
  
      
           
            
            
       
        
        
          

   

        
       
        


    
        

   
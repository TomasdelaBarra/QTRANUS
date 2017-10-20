# -*- coding: utf-8 -*-
import os
import sys
from PyQt4.Qt import QMessageBox, QPushButton, QWidget
from PyQt4 import QtGui, uic,QtCore,Qt
from .scenarios_model import ScenariosModel
from qgis.core import QgsProject
from .interface_template import InterfaceTemplateDialog
import options_tranus_dialog 
from TranusConfig import *
from LcalInterface import *
from LCALparam import *





FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'launch_interface.ui'))




class LaunchTRANUSDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self,checked_list,project_directory,tranus_bin_path,parent=None):
        """Constructor."""
       
        super(LaunchTRANUSDialog, self).__init__(parent)
        self.setupUi(self)
      
        
        self.project = parent.project
        self.proj = QgsProject.instance()
      
        self.tranus_bin_path = tranus_bin_path
        self.project_directory = project_directory
        self.project = parent.project
        self.checked_list = checked_list
        self.is_all_checked = False
        
        self.tabs = self.findChild(QtGui.QTabWidget, 'tabWidget')
      
        
        self.proj = QgsProject.instance()
        #control actions
        self.tabs.blockSignals(True) 
        self.tabs.currentChanged.connect(self.onChange) 
        self.tabs.blockSignals(False) 
            
    def put_tabs(self):
        
        for index,title in enumerate(self.checked_list ) :
            self.add_new_tab(index,title)
            
        if len(self.checked_list ) > 1:   
            tab = InterfaceTemplateDialog()
            self.tabs.addTab(tab,"All checked scenarios")
            
            tab.generate_btn.clicked.connect(self.launch_all_scenarios)
            tab.run_tranus_btn.clicked.connect(self.run_tranus_all_scenarios)
            tab.check_all_btn.clicked.connect(self.check_all_scenarios)
            tab.clear_console.clicked.connect(self.clear_history)
            tab.close_btn.clicked.connect(self.close)
       
              
          
    def add_new_tab(self,index,text):
        
        new_tab = InterfaceTemplateDialog()
        self.tabs.addTab(new_tab,text)
        self.tabs.setTabText(index,text)
        
        new_tab.generate_btn.clicked.connect(self.launch)
        new_tab.run_tranus_btn.clicked.connect(self.run_tranus)
        new_tab.check_all_btn.clicked.connect(self.check_all_scenarios)
        new_tab.clear_console.clicked.connect(self.clear_history)
        new_tab.close_btn.clicked.connect(self.close)
      
    
    def show(self):
        self.put_tabs()
       
        
    def onChange(self):
        
        index = self.tabs.currentIndex()
        tab_title = self.tabs.tabText(index)
        tab = self.tabs.currentWidget()
        
        if tab_title != "All checked scenarios":
            scenario = tab_title.split('-')[1].lstrip()
        else :
            scenario ="ALL"
            
        return [tab,scenario]
    
    def run_tranus(self):
        
        tab = self.onChange()[0]
        scenario = str(self.onChange()[1])
    
        tab.console.append("Beginning of execution of basic TRANUS programs for scenario "+scenario )
        t = TranusConfig(self.tranus_bin_path,self.project_directory,scenario)
        tab.console.append("TRANUS binaries directory                    : "+ t.tranusBinPath)
        tab.console.append("Directory where is located the .tuz file     : "+ t.workingDirectory)
        tab.console.append("ID of the scenario that we want to simulate  : "+ scenario)
        tab.console.append("Parameters file                              : "+ t.param_file)
        tab.console.append("Observations file                            : "+ t.obs_file)
        tab.console.append("Zone file                                    : "+ t.zone_file)
        tab.console.append("Convergence factor                           : "+ t.convFactor)
        
        #Creation of directory for results :
        path_scenario_result_directory = os.path.join(self.project_directory, scenario)
        if not os.path.exists(path_scenario_result_directory):
            os.makedirs(path_scenario_result_directory)
        interface = LcalInterface(t,path_scenario_result_directory)
        loopn = tab.spin_box.value()
        tab.console.append("Executing loop TRANUS for "+ `loopn` +" iterations\n")
        interface.runTranus(tab.spin_box.value()) 
        self.display_results_console(tab,interface.outRun)
                
    def display_results_console(self,tab,file):
        with open(file,"r") as fsrc: 
            lines = fsrc.readlines()
            for line in lines :
                tab.console.append(line)
               
    def launch(self):
        '''launch()
        This method is activated when clicking on the button labeled 'Generate' at the bottom of the interface and when at least one option is checked.
        It executes TRANUS with the options checked by the user.
        '''
        tab = self.onChange()[0]
        scenario = str(self.onChange()[1])
        
        if self.get_all_unchecked(tab)== True:
            QMessageBox.warning(None, "No option selected", "Please check at least one option")
            print "No option selected, Please check at least one option"
        
        else :
            
            tab.console.append("Beginning execution TRANUS ...")
            tab.console.append("Beginning of execution for scenario "+scenario)
            t = TranusConfig(self.tranus_bin_path,self.project_directory,scenario)
            tab.console.append("TRANUS binaries directory                    : "+ t.tranusBinPath)
            tab.console.append("Directory where is located the .tuz file     : "+ t.workingDirectory)
            tab.console.append("ID of the scenario that we want to simulate  : "+ scenario)
            tab.console.append("Parameters file                              : "+ t.param_file)
            tab.console.append("Observations file                            : "+ t.obs_file)
            tab.console.append("Zone file                                    : "+ t.zone_file)
            tab.console.append("Convergence factor                           : "+ t.convFactor)
        
            #Creation of directory for results :
            pathScenarioResultDirectory = os.path.join(self.project_directory, scenario)
            if not os.path.exists(pathScenarioResultDirectory):
                os.makedirs(pathScenarioResultDirectory)
            interface = LcalInterface(t,pathScenarioResultDirectory)
        
            #imploc
          
            for item in tab.imploc_extension.selectedItems():
                extension = item.text()
                
                if(tab.imploc_1.isChecked()):
                    tab.console.append("Executing Imploc -1 for scenario " +scenario)
                    interface.runImplocOption("I",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_1."+extension)         
                if(tab.imploc_2.isChecked()):
                    tab.console.append("Executing Imploc -2 for scenario " +scenario)
                    interface.runImplocOption("P",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_2."+extension)     
                if(tab.imploc_3.isChecked()):
                    tab.console.append("Executing Imploc -3 for scenario " +scenario)
                    interface.runImplocOption("Q",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_3."+extension)      
                if(tab.imploc_4.isChecked()):
                    tab.console.append("Executing Imploc -4 for scenario " +scenario)
                    interface.runImplocOption("S",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_4."+extension)       
                if(tab.imploc_5.isChecked()):
                    tab.console.append("Executing Imploc -5 for scenario " +scenario)
                    interface.runImplocOption("C",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_5."+extension)  
                if(tab.imploc_6.isChecked()):
                    tab.console.append("Executing Imploc -6 for scenario " +scenario)
                    interface.runImplocOption("T",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_6."+extension)    
                if(tab.imploc_7.isChecked()):
                    tab.console.append("Executing location indicators for scenario " +scenario)
                    interface.runImplocOption("J",extension)
                    tab.console.append("The resulting file is written in Imploc/IMPLOC_7."+extension)
            
            #imptra
            
            for item in tab.imptra_extension.selectedItems():
                extension = item.text()
                
                if(tab.imptra_1.isChecked()):
                    tab.console.append("Executing Imptra -1 for scenario " +scenario)
                    interface.runImptraOption("A",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_1."+extension)
                if(tab.imptra_2.isChecked()):
                    tab.console.append("Executing Imptra -2 for scenario " +scenario)
                    interface.runImptraOption("T",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_2."+extension)
                if(tab.imptra_3.isChecked()):
                    tab.console.append("Executing Imptra -3 for scenario " +scenario)
                    interface.runImptraOption("D",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_3."+extension)
                if(tab.imptra_4.isChecked()):
                    tab.console.append("Executing Imptra -4 for scenario " +scenario)
                    interface.runImptraOption("L",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_4."+extension)
                if(tab.imptra_5.isChecked()):
                    tab.console.append("Executing Imptra -5 for scenario " +scenario)
                    interface.runImptraOption("I",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_5."+extension)
                if(tab.imptra_6.isChecked()):
                    tab.console.append("Executing Imptra -6 for scenario " +scenario)
                    interface.runImptraOption("C",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_6."+extension)
                if(tab.imptra_7.isChecked()):
                    tab.console.append("Executing Imptra -7 for scenario " +scenario)
                    interface.runImptraOption("R",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_7."+extension)
                if(tab.imptra_9.isChecked()):
                    tab.console.append("Executing Imptra -9 for scenario " +scenario)
                    interface.runImptraOption("P",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_9."+extension)
                if(tab.imptra_10.isChecked()):
                    tab.console.append("Executing Imptra -10 for scenario " +scenario)
                    interface.runImptraOption("S",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_10."+extension)
                if(tab.imptra_11.isChecked()):
                    tab.console.append("Executing transport indicators for scenario " +scenario)
                    interface.runImptraOption("J",extension)
                    tab.console.append("The resulting file is written in Imptra/IMPTRA_11."+extension)
       
            
            #mats

            for item in tab.mats_extension.selectedItems():
                extension = item.text()
                if(tab.mats_1.isChecked()):
                    tab.console.append("Executing mats -1 for scenario " +scenario)
                    interface.runMatsOption("D",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_1."+extension)
                if(tab.mats_2.isChecked()):
                    tab.console.append("Executing mats -2 for scenario " +scenario)
                    interface.runMatsOption("M",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_2."+extension)
                if(tab.mats_3.isChecked()):
                    tab.console.append("Executing mats -3 for scenario " +scenario)
                    interface.runMatsOption("S",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_3."+extension)
                if(tab.mats_4.isChecked()):
                    tab.console.append("Executing mats -4 for scenario " +scenario)
                    interface.runMatsOption("P",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_4."+extension)
                if(tab.mats_5.isChecked()):
                    tab.console.append("Executing mats -5 for scenario " +scenario)
                    interface.runMatsOption("Q",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_5."+extension)
                if(tab.mats_6.isChecked()):
                    tab.console.append("Executing mats -6 for scenario " +scenario)
                    interface.runMatsOption("R",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_6."+extension)
                if(tab.mats_7.isChecked()):
                    tab.console.append("Executing mats -7 for scenario " +scenario)
                    interface.runMatsOption("T",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_7."+extension)
                if(tab.mats_8.isChecked()):
                    tab.console.append("Executing mats -8 for scenario " +scenario)
                    interface.runMatsOption("O",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_8."+extension)
                if(tab.mats_9.isChecked()):
                    tab.console.append("Executing mats -9 for scenario " +scenario)
                    interface.runMatsOption("E",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_9."+extension)
                if(tab.mats_10.isChecked()):
                    tab.console.append("Executing mats -10 for scenario " +scenario)
                    interface.runMatsOption("F",extension)    
                    tab.console.append("The resulting file is written in Mats/MATS_10."+extension)
                if(tab.mats_11.isChecked()):
                    tab.console.append("Executing mats -11 for scenario " +scenario)
                    interface.runMatsOption("C",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_11."+extension)
                if(tab.mats_12.isChecked()):
                    tab.console.append("Executing mats -12 for scenario " +scenario)
                    interface.runMatsOption("K",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_12."+extension)
                if(tab.mats_13.isChecked()):
                    tab.console.append("Executing mats -13 for scenario " +scenario)
                    interface.runMatsOption("X",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_13."+extension)
                if(tab.mats_14.isChecked()):
                    tab.console.append("Executing mats -14 for scenario " +scenario)
                    interface.runMatsOption("Y",extension)
                    tab.console.append("The resulting file is written in Mats/MATS_14."+extension)
            
            #matesp  
        
            nb_tr = tab.nb_transfers.text() 
            for item in tab.matesp_extension.selectedItems():
                extension = item.text()
                if(tab.matesp_1.isChecked()):
                    tab.console.append("Executing matesp -1 for scenario " +scenario)
                    interface.runMatespOption("T",extension,None)
                    tab.console.append("The resulting files are written in folder Matesp/Results/Option_1")   
                if(tab.matesp_3.isChecked()):
                    if (nb_tr.isdigit()) and (int(nb_tr) >= 1):
                        tab.console.append("Executing matesp -3 with" +nb_tr +" transfers for scenario " +scenario)
                        interface.runMatespOption("R",extension,nb_tr)
                        tab.console.append("The resulting file is written in folder Matesp/Results/Option_3")
                    else:
                        QMessageBox.warning(None, "Invalid number of transfers", "Please write a valid number of transfers")
                        print "Invalid number of transfers, Please write a valid number of transfers"
                        tab.nb_transfers.setText("1")
                if(tab.matesp_4.isChecked()):
                    tab.console.append("Executing matesp -4 for scenario " +scenario)
                    interface.runMatespOption("D",extension,None)
                    tab.console.append("The resulting files are written in folder Matesp/Results/Option_4")
                if(tab.matesp_5.isChecked()):
                    tab.console.append("Executing matesp -5 for scenario " +scenario)
                    interface.runMatespOption("M",extension,None)
                    tab.console.append("The resulting files are written in folder Matesp/Results/Option_5")
                if(tab.matesp_6.isChecked()):
                    tab.console.append("Executing matesp -6 for scenario " +scenario)
                    interface.runMatespOption("C",extension,None)
                    tab.console.append("The resulting files are written in folder Matesp/Results/Option_6")
                if(tab.matesp_7.isChecked()):
                    tab.console.append("Executing matesp -7 for scenario " +scenario)
                    interface.runMatespOption("O",extension,None)
                    tab.console.append("The resulting file is written in folder Matesp/Results/Option_7")     
                if(tab.matesp_8.isChecked()):
                    tab.console.append("Executing matesp -8 for scenario " +scenario)
                    interface.runMatespOption("S",extension,None)
                    tab.console.append("The resulting file is written in folder Matesp/Results/Option_8")
            
            #end of calculations     
            tab.console.append("Calculations complete")
    
    def check_all_scenarios(self):
        
        tab = self.onChange()[0]
        scenario = self.onChange()[1]
        
        new_state = QtCore.Qt.Unchecked
        if (self.is_all_checked == False):
            self.is_all_checked = True
            new_state = QtCore.Qt.Checked
        else :
            self.is_all_checked = QtCore.Qt.Unchecked 
            
        #imploc   
        tab.imploc_1.setCheckState(new_state)
        tab.imploc_2.setCheckState(new_state)
        tab.imploc_3.setCheckState(new_state)
        tab.imploc_4.setCheckState(new_state)
        tab.imploc_5.setCheckState(new_state)
        tab.imploc_6.setCheckState(new_state) 
        tab.imploc_7.setCheckState(new_state)  
        
        #imptra
        tab.imptra_1.setCheckState(new_state)
        tab.imptra_2.setCheckState(new_state)
        tab.imptra_3.setCheckState(new_state)
        tab.imptra_4.setCheckState(new_state)
        tab.imptra_5.setCheckState(new_state)
        tab.imptra_6.setCheckState(new_state)
        tab.imptra_7.setCheckState(new_state)
        tab.imptra_9.setCheckState(new_state)
        tab.imptra_10.setCheckState(new_state)
        tab.imptra_11.setCheckState(new_state)
        
        #mats
        tab.mats_1.setCheckState(new_state)
        tab.mats_2.setCheckState(new_state)
        tab.mats_3.setCheckState(new_state)
        tab.mats_4.setCheckState(new_state)
        tab.mats_5.setCheckState(new_state)
        tab.mats_6.setCheckState(new_state)
        tab.mats_7.setCheckState(new_state)
        tab.mats_8.setCheckState(new_state)   
        tab.mats_9.setCheckState(new_state) 
        tab.mats_10.setCheckState(new_state)
        tab.mats_11.setCheckState(new_state) 
        tab.mats_12.setCheckState(new_state)
        tab.mats_13.setCheckState(new_state)
        tab.mats_14.setCheckState(new_state)
        
        #matesp
        tab.matesp_1.setCheckState(new_state)
        tab.matesp_3.setCheckState(new_state)
        tab.matesp_4.setCheckState(new_state)
        tab.matesp_5.setCheckState(new_state)
        tab.matesp_6.setCheckState(new_state)
        tab.matesp_7.setCheckState(new_state)
        tab.matesp_8.setCheckState(new_state)
        
    def get_all_unchecked(self,tab):
        
        nb_unchecked = 0
        
        #imploc
        if tab.imploc_1.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imploc_2.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imploc_3.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imploc_4.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1    
        if tab.imploc_5.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imploc_6.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imploc_7.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
            
        #imptra
        if tab.imptra_1.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_2.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_3.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_4.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_5.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_6.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_7.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_9.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_10.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.imptra_11.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
            
        #mats
        if tab.mats_1.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_2.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_3.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_4.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_5.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_6.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_7.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_8.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_9.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_10.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_11.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_12.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_13.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.mats_14.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
               
        #matesp
        if tab.matesp_1.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.matesp_3.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.matesp_4.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.matesp_5.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.matesp_6.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.matesp_7.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
        if tab.matesp_8.checkState() == QtCore.Qt.Unchecked:
            nb_unchecked+=1
             
        if nb_unchecked == 38 : # all are unchecked
            return True
        else :
            return False

    def clear_history(self):
      
        tab = self.onChange()[0]
        tab.console.clear()
        
    def get_list_scenarios(self):
        
        list_scenarios = []
        
        for title in self.checked_list :  
            code_scenario =  title.split('-')[1].lstrip()  
            list_scenarios.append(code_scenario)
            
        return list_scenarios
                    
    def launch_all_scenarios(self):
        
        list_scenarios = self.get_list_scenarios()
        tab = self.onChange()[0]
        
        if self.get_all_unchecked(tab)== True:
            QMessageBox.warning(None, "No option selected", "Please check at least one option")
            print "No option selected, Please check at least one option"
        
        else :
        
            for scenario in list_scenarios :
            
                tab.console.append("Beginning execution TRANUS ...")
                tab.console.append("Beginning of execution for scenario "+scenario)
                t = TranusConfig(self.tranus_bin_path,self.project_directory,scenario)
                tab.console.append("TRANUS binaries directory                    : "+ t.tranusBinPath)
                tab.console.append("Directory where is located the .tuz file     : "+ t.workingDirectory)
                tab.console.append("ID of the scenario that we want to simulate  : "+ scenario)
                tab.console.append("Parameters file                              : "+ t.param_file)
                tab.console.append("Observations file                            : "+ t.obs_file)
                tab.console.append("Zone file                                    : "+ t.zone_file)
                tab.console.append("Convergence factor                           : "+ t.convFactor)
        
                #Creation of directory for results :
                pathScenarioResultDirectory = os.path.join(self.project_directory, scenario)
                if not os.path.exists(pathScenarioResultDirectory):
                    os.makedirs(pathScenarioResultDirectory)
                interface = LcalInterface(t,pathScenarioResultDirectory)
            
                #imploc
                for item in tab.imploc_extension.selectedItems():
                    extension =item.text()
        
                    if(tab.imploc_1.isChecked()):
                        tab.console.append("Executing Imploc -1 for scenario " +scenario)
                        interface.runImplocOption("I",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_1."+extension)
                    if(tab.imploc_2.isChecked()):
                        tab.console.append("Executing Imploc -2 for scenario " +scenario)
                        interface.runImplocOption("P",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_2."+extension)
                    if(tab.imploc_3.isChecked()):
                        tab.console.append("Executing Imploc -3 for scenario " +scenario)
                        interface.runImplocOption("Q",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_3."+extension)
                    if(tab.imploc_4.isChecked()):
                        tab.console.append("Executing Imploc -4 for scenario " +scenario)
                        interface.runImplocOption("S",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_4."+extension)
                    if(tab.imploc_5.isChecked()):
                        tab.console.append("Executing Imploc -5 for scenario " +scenario)
                        interface.runImplocOption("C",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_5."+extension)  
                    if(tab.imploc_6.isChecked()):
                        tab.console.append("Executing Imploc -6 for scenario " +scenario)
                        interface.runImplocOption("T",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_6."+extension)
                    if(tab.imploc_7.isChecked()):
                        tab.console.append("Executing location indicators for scenario " +scenario)
                        interface.runImplocOption("J",extension)
                        tab.console.append("The resulting file is written in Imploc/IMPLOC_7."+extension)
                
                #imptra    
                
                for item in tab.imptra_extension.selectedItems():
                    extension =item.text()
     
                    if(tab.imptra_1.isChecked()):
                        tab.console.append("Executing Imptra -1 for scenario " +scenario)
                        interface.runImptraOption("A",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_1."+extension)
                    if(tab.imptra_2.isChecked()):
                        tab.console.append("Executing Imptra -2 for scenario " +scenario)
                        interface.runImptraOption("T",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_2."+extension)
                    if(tab.imptra_3.isChecked()):
                        tab.console.append("Executing Imptra -3 for scenario " +scenario)
                        interface.runImptraOption("D",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_3."+extension)
                    if(tab.imptra_4.isChecked()):
                        tab.console.append("Executing Imptra -4 for scenario " +scenario)
                        interface.runImptraOption("L",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_4."+extension)
                    if(tab.imptra_5.isChecked()):
                        tab.console.append("Executing Imptra -5 for scenario " +scenario)
                        interface.runImptraOption("I",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_5."+extension)
                    if(tab.imptra_6.isChecked()):
                        tab.console.append("Executing Imptra -6 for scenario " +scenario)
                        interface.runImptraOption("C",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_6."+extension)
                    if(tab.imptra_7.isChecked()):
                        tab.console.append("Executing Imptra -7 for scenario " +scenario)
                        interface.runImptraOption("R",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_7."+extension)
                    if(tab.imptra_9.isChecked()):
                        tab.console.append("Executing Imptra -9 for scenario " +scenario)
                        interface.runImptraOption("P",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_9."+extension)
                    if(tab.imptra_10.isChecked()):
                        tab.console.append("Executing Imptra -10 for scenario " +scenario)
                        interface.runImptraOption("S",extension)
                        tab.console.append("The resulting file is written in Imptra/IMPTRA_10."+extension)
            
                #mats
                for item in tab.mats_extension.selectedItems():
                    extension =item.text()
                    
                    if(tab.mats_1.isChecked()):
                        tab.console.append("Executing mats -1 for scenario " +scenario)
                        interface.runMatsOption("D",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_1."+extension)
                    if(tab.mats_2.isChecked()):
                        tab.console.append("Executing mats -2 for scenario " +scenario)
                        interface.runMatsOption("M",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_2."+extension)
                    if(tab.mats_3.isChecked()):
                        tab.console.append("Executing mats -3 for scenario " +scenario)
                        interface.runMatsOption("S",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_3."+extension)
                    if(tab.mats_4.isChecked()):
                        tab.console.append("Executing mats -4 for scenario " +scenario)
                        interface.runMatsOption("P",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_4."+extension)
                    if(tab.mats_5.isChecked()):
                        tab.console.append("Executing mats -5 for scenario " +scenario)
                        interface.runMatsOption("Q",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_5."+extension)
                    if(tab.mats_6.isChecked()):
                        tab.console.append("Executing mats -6 for scenario " +scenario)
                        interface.runMatsOption("R",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_6."+extension)
                    if(tab.mats_7.isChecked()):
                        tab.console.append("Executing mats -7 for scenario " +scenario)
                        interface.runMatsOption("T",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_7."+extension)
                    if(tab.mats_8.isChecked()):
                        tab.console.append("Executing mats -8 for scenario " +scenario)
                        interface.runMatsOption("O",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_8."+extension)
                    if(tab.mats_9.isChecked()):
                        tab.console.append("Executing mats -9 for scenario " +scenario)
                        interface.runMatsOption("E",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_9."+extension)
                    if(tab.mats_10.isChecked()):
                        tab.console.append("Executing mats -10 for scenario " +scenario)
                        interface.runMatsOption("F",extension)    
                        tab.console.append("The resulting file is written in Mats/MATS_10."+extension)
                    if(tab.mats_11.isChecked()):
                        tab.console.append("Executing mats -11 for scenario " +scenario)
                        interface.runMatsOption("C",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_11."+extension)
                    if(tab.mats_12.isChecked()):
                        tab.console.append("Executing mats -12 for scenario " +scenario)
                        interface.runMatsOption("K",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_12."+extension)
                    if(tab.mats_13.isChecked()):
                        tab.console.append("Executing mats -13 for scenario " +scenario)
                        interface.runMatsOption("X",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_13."+extension)
                    if(tab.mats_14.isChecked()):
                        tab.console.append("Executing mats -14 for scenario " +scenario)
                        interface.runMatsOption("Y",extension)
                        tab.console.append("The resulting file is written in Mats/MATS_14."+extension)
                
         
                #matesp   
                for item in tab.matesp_extension.selectedItems():
                    extension =item.text()
                    
                    nb_tr = tab.nb_transfers.text()
                    if(tab.matesp_1.isChecked()):
                        tab.console.append("Executing matesp -1 for scenario " +scenario)
                        interface.runMatespOption("T",extension,None)
                        tab.console.append("The resulting files are written in folder Matesp/Results/Option_1")
                    if(tab.matesp_3.isChecked()):
                        if (nb_tr.isdigit()) and (int(nb_tr) >= 1):
                            tab.console.append("Executing matesp -3 with" +nb_tr +" transfers for scenario " +scenario)
                            interface.runMatespOption("R",extension,nb_tr)
                            tab.console.append("The resulting file is written in folder Matesp/Results/Option_3")
                        else:
                            QMessageBox.warning(None, "Invalid number of transfers", "Please write a valid number of transfers")
                            print "Invalid number of transfers, Please write a valid number of transfers"
                            tab.nb_transfers.setText("1")
                    if(tab.matesp_4.isChecked()):
                        tab.console.append("Executing matesp -4 for scenario " +scenario)
                        interface.runMatespOption("D",extension,None)
                        tab.console.append("The resulting files are written in folder Matesp/Results/Option_4")
                    if(tab.matesp_5.isChecked()):
                        tab.console.append("Executing matesp -5 for scenario " +scenario)
                        interface.runMatespOption("M",extension,None)
                        tab.console.append("The resulting files are written in folder Matesp/Results/Option_5")
                    if(tab.matesp_6.isChecked()):
                        tab.console.append("Executing matesp -6 for scenario " +scenario)
                        interface.runMatespOption("C",extension,None)
                        tab.console.append("The resulting files are written in folder Matesp/Results/Option_6")
                    if(tab.matesp_7.isChecked()):
                        tab.console.append("Executing matesp -7 for scenario " +scenario)
                        interface.runMatespOption("O",extension,None)
                        tab.console.append("The resulting file is written in folder Matesp/Results/Option_7")     
                    if(tab.matesp_8.isChecked()):
                        tab.console.append("Executing matesp -8 for scenario " +scenario)
                        interface.runMatespOption("S",extension,None)
                        tab.console.append("The resulting file is written in folder Matesp/Results/Option_8")
                
                tab.console.append("Calculations complete")
    
    def run_tranus_all_scenarios(self):
        
        tab = self.onChange()[0]
        list_scenarios = self.get_list_scenarios()
    
        for scenario in list_scenarios :
    
            tab.console.append("Beginning of execution of basic TRANUS programs for scenario "+scenario )
            t = TranusConfig(self.tranus_bin_path,self.project_directory,scenario)
            tab.console.append("TRANUS binaries directory                    : "+ t.tranusBinPath)
            tab.console.append("Directory where is located the .tuz file     : "+ t.workingDirectory)
            tab.console.append("ID of the scenario that we want to simulate  : "+ scenario)
            tab.console.append("Parameters file                              : "+ t.param_file)
            tab.console.append("Observations file                            : "+ t.obs_file)
            tab.console.append("Zone file                                    : "+ t.zone_file)
            tab.console.append("Convergence factor                           : "+ t.convFactor)
        
            #Creation of directory for results :
            path_scenario_result_directory = os.path.join(self.project_directory, scenario)
            if not os.path.exists(path_scenario_result_directory):
                os.makedirs(path_scenario_result_directory)
            interface = LcalInterface(t,path_scenario_result_directory)
            loopn = tab.spin_box.value()
            tab.console.append("Executing loop TRANUS for "+ `loopn` +" iterations\n")
            interface.runTranus(tab.spin_box.value())
            self.display_results_console(tab,interface.outRun)
     
    
    
        
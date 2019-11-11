# -*- coding: utf-8 -*-
import os, sys

from .DataBaseSqlite import DataBaseSqlite
from ..libraries.tabulate import tabulate

class BatchFiles():
    def __init__(self, tranus_folder, pluginDir, statusBar=None, programsListSelected=None, fixed_transportable=None, id_scenario=None):
        self.tranus_folder = tranus_folder
        self.statusBar = statusBar
        self.programsListSelected = programsListSelected
        self.fixed_transportable = fixed_transportable
        self.id_scenario = id_scenario
        self.plugin_dir = pluginDir
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)

          


    def listPrograms(self):
        resultScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(self.id_scenario))
        codeScenario = resultScenario[0][1]

        if resultScenario[0][3]:
            programs = {'Path Search': [f'pasos {codeScenario}'], 
                        'Location':[f'loc {codeScenario}',
                                    f'fluj {codeScenario}',
                                    f'imploc {codeScenario} -J -o transport_indicators_{codeScenario}.csv'],
                        'Assigment':[f'fluj {codeScenario} -I', 
                                    f'trans {codeScenario} -N -z',
                                    f'cost {codeScenario}',
                                    f'imptra {codeScenario} -J -o transport_indicators_{codeScenario}.csv',
                                    f'imptra {codeScenario} -S -o route_profile_{codeScenario}.csv']
                        }
        else:
            # Base Sceanario 
            programs = {'Path Search': [f'pasos {codeScenario}'], 
                        'Initial Assigment':[f'trans {codeScenario} -I', 
                                             f'cost {codeScenario}'],
                        'Location':[f'cost {codeScenario}', 
                                    f'lcal {codeScenario} %s ' % ('-f' if self.fixed_transportable else '') ,
                                    f'fluj {codeScenario}',
                                    f'imploc {codeScenario} -J -o location_indicators_{codeScenario}.csv'],
                        'Assigment':[f'fluj {codeScenario}', 
                                    f'trans {codeScenario} -N -z',
                                    f'cost {codeScenario}',
                                    f'imptra {codeScenario} -J -o transport_indicators_{codeScenario}.csv',
                                    f'imptra {codeScenario} -S -o route_profile_{codeScenario}.csv']
                        }

        resultList = []
        for value in self.programsListSelected:
            for detail in programs[value[1]]:
                resultList.append(detail)

        return resultList


    def generate_bath_file(self):
        """
            @summary: Set Scenario selected
        """
        programs = self.listPrograms()
        
        resultScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(self.id_scenario))
        codeScenario = resultScenario[0][1]
        header = self.dataBaseSqlite.selectAll(" project ")
        #filename = "{}{}.BAT".format(header[0][1], codeScenario)
        filename = "qtranus_batch.bat"
        fh = None
        
        try:
            
            fh = open("{}/{}".format(self.tranus_folder, filename), "w", encoding="utf-8")

            for program in programs:
                fh.write(f"{program}\n")
            
            self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

            return filename
        except Exception as e:
            return False
        finally:
            fh.close()
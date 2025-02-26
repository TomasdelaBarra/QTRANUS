# -*- coding: utf-8 -*-
import os, sys

from .DataBaseSqlite import DataBaseSqlite
from ..libraries.tabulate import tabulate

class BatchFiles():
    def __init__(self, project_file, pluginDir, statusBar=None, programsListSelected=None, fixed_transportable=None, id_scenario=None):
        self.project_file = project_file
        self.tranus_folder = self.uriSegmentation(project_file)
        self.statusBar = statusBar
        self.programsListSelected = programsListSelected
        self.fixed_transportable = fixed_transportable
        self.id_scenario = id_scenario
        self.plugin_dir = pluginDir
        self.dataBaseSqlite = DataBaseSqlite(self.project_file)


    def uriSegmentation(self, project_file):
        project_file_arr = project_file.split("\\")
        return "/".join(project_file_arr[:len(project_file_arr)-1])


    def listPrograms(self):
        resultScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(self.id_scenario))
        codeScenario = resultScenario[0][1]

        if resultScenario[0][3]:
            programs = {'Path Search': [f'pasos {codeScenario}', f'impas {codeScenario} -P -M -o {codeScenario}\path_{codeScenario}.csv'], 
                        'Location':[f'loc {codeScenario}',
                                    f'fluj {codeScenario}',
                                    f'imploc {codeScenario} -J -o location_indicators_{codeScenario}.csv',
                                    f'imploc {codeScenario} -C -o unit_consumption_{codeScenario}.csv',
                                    f'imploc {codeScenario} -T -o total_consumption_{codeScenario}.csv'],
                        'Assignment':[f'fluj {codeScenario} -I', 
                                    f'trans {codeScenario} -N -z',
                                    f'cost {codeScenario}',
                                    f'imptra {codeScenario} -J -o transport_indicators_{codeScenario}.csv',
                                    f'imptra {codeScenario} -S -o route_profile_{codeScenario}.csv',
                                    f'imptra {codeScenario} -A -k -f 3 -o Assignment_{codeScenario}.csv',
                                    f'mats {codeScenario} -Q -o trip_matrix_{codeScenario}_i.csv']
                        }
        else:
            # Base Sceanario 
            programs = {'Path Search': [f'pasos {codeScenario}', f'impas {codeScenario} -P -M -o {codeScenario}\path_{codeScenario}.csv'], 
                        'Initial Assignment':[f'trans {codeScenario} -I', 
                                             f'cost {codeScenario}'],
                        'Location':[f'cost {codeScenario}', 
                                    f'lcal {codeScenario} %s ' % ('-f' if self.fixed_transportable else '') ,
                                    f'fluj {codeScenario}',
                                    f'imploc {codeScenario} -J -o location_indicators_{codeScenario}.csv',
                                    f'imploc {codeScenario} -C -o unit_consumption_{codeScenario}.csv',
                                    f'imploc {codeScenario} -T -o total_consumption_{codeScenario}.csv'],
                        'Assignment':[f'fluj {codeScenario}', 
                                    f'trans {codeScenario} -N -z',
                                    f'cost {codeScenario}',
                                    f'imptra {codeScenario} -J -o transport_indicators_{codeScenario}.csv',
                                    f'imptra {codeScenario} -S -o route_profile_{codeScenario}.csv',
                                    f'imptra {codeScenario} -A -k -f 3 -o Assignment_{codeScenario}.csv',
                                    f'mats {codeScenario} -Q -o trip_matrix_{codeScenario}_i.csv']
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
            file = os.path.join(self.tranus_folder, filename)
            with open(file, "w", encoding="utf-8") as fh:
                for program in programs:
                    fh.write(f"{program}\n")
                
                self.statusBar.showMessage("File: {}/{}".format(self.tranus_folder, filename))

                return filename
        except Exception as e:
            return False
        finally:
            fh.close()


    def validate_generate_assignment(self):
        
        for value in self.programsListSelected:
            print(value, value[1])
            if value[1]=='Assignment':
                a = ''
        return 


    def read_assignments(self):
        resultScenario = self.dataBaseSqlite.selectAll(' scenario ', ' where id = {}'.format(self.id_scenario))
        codeScenario = resultScenario[0][1]

        self.tranus_folder = ""

        fh = open("%s/%s" % (self.tranus_folder, f"assignment_{codeScenario}_tmp.csv"), "r", encoding="utf-8")

        return 
import os, sys, csv, re

class Paths(object):
    def __init__(self, tranus_folder, scenario_code):
        """
            @summary: Constructor
        """
        self.tranus_folder = tranus_folder
        self.scenario_code = scenario_code
        self.result_data_return = []
    
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print(self.__class__.__name__, "destroyed")    
    

    def load_paths(self):
        """
            @summary: Load Path by scenario files scenarios
        """
        regex_paths_data = r'[\s{2,}\d]\s\w+\s.*\n\s+-?\d:\s+\d+\s+>\s+-?\d.*'
        # regex_paths_data = r'([\s{2,}\d]\s\w+\s.*\n(\s+-?\d:\s+\d+\s+>\s+-?\d.*\n){1,})'        
        result_dict = dict()
        result_data_return = []
        filename = os.path.join(self.tranus_folder, self.scenario_code, f"path_{self.scenario_code}.csv")
        try:
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    file = file.read()
                    result = re.findall(regex_paths_data, file)
                    # print("TODOOOO")
                    # print(result)
                    for index, value in enumerate(result):
                        result_data = value[index].split('\n')[0]
                        result_data = result_data.split('\n')[0].split('    ')
                        # print(result_data)
                        if result_data[0] != '':
                            desutilities_data = dict()
                            desutilities_data['orig'] = result_data[0]
                            desutilities_data['dest'] = result_data[1]
                            desutilities_data['mode'] = result_data[2] 
                            desutilities_data['path'] = result_data[4]
                            desutilities_data['dist'] = result_data[5]
                            desutilities_data['lnktme'] = result_data[6]
                            desutilities_data['waittme'] = result_data[7]
                            desutilities_data['moncos'] = result_data[8]
                            desutilities_data['chargs'] = result_data[9]
                            desutilities_data['uchrgs'] = result_data[10]
                            desutilities_data['gencost'] = result_data[11]
                        else:
                            paths_data = [value.split(":") for value in data[1].split(">")]
                        
                        result_data_return.append((desutilities_data, paths_data))
                return result_data_return    
            else:
                return False
        except Exception as e:
            print("Error: Reading paths file", e)

    
    def find_paths(self, id_origin, id_destination, scenario_code):
        result = self.load_paths()
        values = []
        for value in result:            
            if int(value[0]['orig']) == int(id_origin) and int(value[0]['dest']) == int(id_destination):
               values.append(value) 
        # print("Estos don ")
        # print(values)       
        return values
        
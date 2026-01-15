# -*- coding: utf-8 -*-
import re
import os

class Helpers(object):

    def indent(self, elem, level=0):
        """
        @summary: Indent element in XML File
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def strToList(self, string):
        string = string.replace("[","").replace("]","").replace("'","")
        return string.split(',')


    @staticmethod
    def expressionToList(expression):
        expression = str(expression)
        expression = expression.replace("[","").replace("]","").replace("'","")
        return expression.split(',')


    @staticmethod
    def decimalFormat(num):
        import re 
        
        return re.sub("\.0$","",num)


    @staticmethod
    def screenResolution(percent=0):
        try:
            from win32api import GetSystemMetrics
        except:
            return dict(width=400, height=320)
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)

        if percent:
            width = (percent/100)*width
            height = (percent/100)*height

        return dict(width=int(width), height=int(height))

    @staticmethod
    def method_x_varible(variable):
        if variable == "StVeh/Cap":
            return "Color"
        if variable == "StVeh":
            return "Color"
        if variable == "TotVeh":
            return "Color"
        if variable == "ServLev":
            return "Size"
        if variable == "Demand":
            return "Size"
        if variable == "Dem/Cap":
            return "Color"
        if variable == "FinSpeed":
            return "Color"
        if variable == "FinWait":
            return  "Color"
        if variable == "Energy":
            return "Color"

    @staticmethod
    def hex_to_RGB(hex):
            ''' "#FFFFFF" -> [255,255,255] '''
            # Pass 16 to the integer function for change of base
            return [int(hex[i:i+2], 16) for i in range(1,6,2)]

    @staticmethod
    def RGB_to_hex(RGB):
        ''' [255,255,255] -> "#FFFFFF" '''
        # Components need to be integers for hex to make sense
        RGB = [int(x) for x in RGB]
        return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                "{0:x}".format(v) for v in RGB])

    @staticmethod
    def linear_gradient(startRgb, finishRgb, n=8):
        ''' returns a gradient list of (n) colors between
        two RGB colors. '''

        def color_dict(gradient):
            ''' Takes in a list of RGB sub-lists and returns dictionary of
            colors in RGB and hex form for use in a graphing function
            defined later on '''
            return {"r":[RGB[0] for RGB in gradient],
            "g":[RGB[1] for RGB in gradient],
            "b":[RGB[2] for RGB in gradient]}

        s = startRgb
        f = finishRgb
        # Initilize a list of the output colors with the starting color
        RGB_list = [s]
        # Calcuate a color at each evenly spaced value of t from 1 to n
        for t in range(1, n):
            # Interpolate RGB vector for color at the current value of t
            curr_vector = [
              int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
              for j in range(3)
            ]
            # Add it to our list of output colors
            RGB_list.append(curr_vector)

        return color_dict(RGB_list)

    @staticmethod
    def union_elements_by_column(list_a, list_b, column=1):
        '''
        Add list_a to the missing elements that are in list_b
        '''
        def find_element(value, links_list):
            for data in links_list:
                if data[column] == value:
                    return True
            return False

        for data_b in list_b:
            if not find_element(data_b[column], list_a):
                list_a.append(data_b)
        return list_a

    
   
    @staticmethod
    def transform_trips_matrix(scenario_cod, tranus_folder):
        try:
            regex_cat_line = "\d+-(\s\d+|\d+)-\d\d\d\d\s+\d+:\d+"
            regex_cat_id = "\s{3,}"
            regex_zone_id = r"\d+\s\b[A-Za-z0-9 .]+\b\s+\d+.\d+"
            read_file = os.path.join(tranus_folder, f"trip_matrix_{scenario_cod}_i.csv")
            write_file = os.path.join(tranus_folder, f"trip_matrices_{scenario_cod}.csv")
            zones = []

            with open(read_file, 'r' ) as reader:
                for line in reader:
                    if re.search(regex_zone_id, line):
                        tmp = [values.strip() for values in line.split("\t")]
                        if not tmp[0] in zones:
                            zones.append(tmp[0])
            zones.insert(0, '')
            with open( read_file, 'r' ) as reader, open( write_file, 'w' ) as writer:
                writer.write("OrZonId,OrZonName,DeZonId,DeZonName,CatId,CatName,Trips\n")
                category = []
                for line in reader:
                    if re.search(regex_cat_line, line):
                        category = re.split(regex_cat_id, line)
                    if re.search(regex_zone_id, line) and category:
                        arr = [values.strip() for values in re.split("\t", line)]
                        for index in range(1, len(arr)-1):
                            if index:
                                OrZon = arr[0].split(" ")
                                Cat = category[0].strip().split(" ")
                                writer.write(f"{OrZon[0]},{OrZon[1]},{zones[index].split(' ')[0]},{zones[index].split(' ')[1]},{Cat[0]},{Cat[1]},{arr[index]}\n")
            return True
        except:
            return False

    @staticmethod   
    def get_diff_arrays(list_a, list_b):
        """
        @summary: 
        Compares two lists of tuples and returns the elements of list_a whose first two values ​​do not exist in list_b.

        Arguments:

        list_a -- Main list of tuples.
        list_b -- Reference list for comparison.
        """
        
        # Step 1: Create a set with the identifiers (index 0 and 1) from list b.
        # This optimizes the search from O(n) to O(1) for each element.
        keys_in_b = {(item[0], item[1]) for item in list_b}
        
        # Step 2: Filter elements from list_a.
        # Keep the entire tuple if its first two values are not in the set.
        difference = [
            item for item in list_a 
            if (item[0], item[1]) not in keys_in_b
        ]
        
        return difference


class ExceptionGeometryType(Exception):
    """
    @summary: Exception for type geometry of the shapes
    """
    def __init__(self, shape):
        super(ExceptionGeometryType, self).__init__()
        self.shape = shape

    def __str__(self):
        return f"Incorrect Geometry for shape {self.shape}"


class ExceptionFormatID(Exception):
    """
    @summary: Exception for type geometry of the shapes
    """
    def __init__(self, idFile, typeFile=None):
        super(ExceptionFormatID, self).__init__()
        self.idFile = idFile
        self.typeFile = typeFile

    def __str__(self):
        return f"{self.typeFile} \nIncorrect Format ID {self.idFile}" if self.typeFile else f"Incorrect Format ID {self.typeFile}"


class ExceptionWrongDataType(Exception):
    """
    @summary: Exception for data type 
    """
    def __init__(self, _id, _field, message="Data type is wrong"):
        self._id = _id
        self._field = _field
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Field: {self._field}  id: {self._id} data type is wrong'


class ExceptionNullValue(Exception):
    """
    @summary: Exception for data type 
    """
    def __init__(self, _id, _field, message="Data type is wrong"):
        self._id = _id
        self._field = _field
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Field: {self._field}  id: {self._id} value is null'
         
                
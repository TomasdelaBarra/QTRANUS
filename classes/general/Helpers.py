# -*- coding: utf-8 -*-

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

        return dict(width=width, height=height)

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
    
                
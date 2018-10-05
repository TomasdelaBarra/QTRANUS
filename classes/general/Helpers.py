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
        
            
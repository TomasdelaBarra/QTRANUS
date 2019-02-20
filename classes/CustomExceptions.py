# -*- coding: utf-8 -*-

class InputFileSourceError(Exception):
    """Error while load Source File."""
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}
    


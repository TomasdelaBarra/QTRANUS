from GeneralObject import GeneralObject

""" TripMtrix Class """
class TripMatrix(GeneralObject):
    def __init__(self):
        """
            @summary: Constructor
        """
        GeneralObject.__init__(self)
        self.tripMatrix = None
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
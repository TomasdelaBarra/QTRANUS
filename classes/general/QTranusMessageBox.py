# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4.Qt import QMessageBox

""" QTranusMessageBox Class """
class QTranusMessageBox(object):

    @staticmethod
    def set_new_message_box(messageIcon, windowTitle, message, windowIcon, qparent, buttons):
        """
            @summary: Constructor
        """
        messagebox = QtGui.QMessageBox(messageIcon, windowTitle, message, buttons, parent = qparent)
        messagebox.setWindowIcon(QtGui.QIcon(windowIcon))
        
        return messagebox
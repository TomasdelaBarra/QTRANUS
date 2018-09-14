# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
from PyQt5.Qt import QMessageBox

__ALL__ = ['QTranusMessageBox']
""" QTranusMessageBox Class """
class QTranusMessageBox(object):

    @staticmethod
    def set_new_message_box(messageIcon, windowTitle, message, windowIcon, qparent, buttons):
        """
            @summary: Constructor
        """
        messagebox = QtWidgets.QMessageBox(messageIcon, windowTitle, message, buttons, parent = qparent)
        messagebox.setWindowIcon(QtGui.QIcon(windowIcon))
        
        return messagebox
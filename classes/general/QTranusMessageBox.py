# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QSize
from PyQt5.Qt import QMessageBox

__ALL__ = ['QTranusMessageBox']
""" QTranusMessageBox Class """
class QTranusMessageBox(object):

    @staticmethod
    def set_new_message_box(messageIcon, windowTitle, message, windowIcon, qparent, buttons, detailedText = None):
        """
            @summary: Constructor
        """
        messagebox = QtWidgets.QMessageBox(messageIcon, windowTitle, message, buttons, parent = qparent)
        messagebox.setWindowIcon(QtGui.QIcon(windowIcon))
        messagebox.resize(1200, 1200)
        if detailedText:
            messagebox.setDetailedText(detailedText)
        
        return messagebox
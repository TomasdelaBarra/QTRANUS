# -*- coding: utf-8 -*-
from PyQt5 import QtGui
from PyQt5 import QtCore

def validatorExpr(_type='alphaNum',limit=None):
	exp = ''
	if _type=='alphaNum':
		exp = '^[A-Za-z0-9]+$'
	if _type=='decimal':
		exp = '^(\d*\.)?\d+$'
	if _type=='alphaNum' and limit!=None:
		exp = '^[A-Za-z0-9]{%s}$' % limit
	if _type=='integer':
		exp = '[0-9]+' 

	regExpretion = QtCore.QRegExp(exp)
	
	return QtGui.QRegExpValidator(regExpretion)
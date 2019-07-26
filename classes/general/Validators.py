# -*- coding: utf-8 -*-
import re
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
	if _type=='any':
		exp = '.{%s}' % limit

	regExpretion = QtCore.QRegExp(exp)
	
	return QtGui.QRegExpValidator(regExpretion)


def validatorRegex(value, _type='real',limit=None):
	exp = ''
	if _type=='real':
		exp = '^\d*\.?\d*$'
	if _type=='real-negative':
		exp = '^(\d|-)*\.?\d*$'

	result = re.match(exp, value)
	if result: 
		return True
	else:
		return False
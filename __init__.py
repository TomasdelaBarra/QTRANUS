# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OptionsTRANUS
                                 A QGIS plugin
 This plugin automates the execution of TRANUS programs.
                             -------------------
        begin                : 2017-02-23
        copyright            : (C) 2017 by STEEP Inria
        email                : emna.jribi@inria.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OptionsTRANUS class from file OptionsTRANUS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Options_TRANUS import OptionsTRANUS
    return OptionsTRANUS(iface)

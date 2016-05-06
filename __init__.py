# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QTranus
                                 A QGIS plugin
 qtranus
                             -------------------
        begin                : 2015-07-20
        copyright            : (C) 2015 by qtranus
        email                : pedroburonv@gmail.com
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
    """Load QTranus class from file QTranus.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qtranus import QTranus
    return QTranus(iface)

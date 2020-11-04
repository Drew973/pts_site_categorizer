# -*- coding: utf-8 -*-
"""
/***************************************************************************
 site_categoriser
                                   *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load site_categoriser class from file site_categoriser.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .site_categoriser import site_categoriser
    return site_categoriser(iface)

"""
.. module: horseradish.plugins.base
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from __future__ import absolute_import, print_function

from horseradish.plugins.base.manager import PluginManager
from horseradish.plugins.base.v1 import *  # noqa

plugins = PluginManager()
register = plugins.register
unregister = plugins.unregister

"""
.. module: horseradish.plugins.bases.export
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from horseradish.plugins.base import Plugin


class ExportPlugin(Plugin):
    """
    This is the base class from which all supported
    exporters will inherit from.
    """

    type = "export"
    requires_key = True

    def export(self, body, chain, key, options, **kwargs):
        raise NotImplementedError

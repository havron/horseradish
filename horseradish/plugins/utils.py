"""
.. module: horseradish.plugins.utils
    :platform: Unix

    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>

"""


def get_plugin_option(name, options):
    """
    Retrieve option name from options dict.
    :param options:
    :return:
    """
    for o in options:
        if o.get("name") == name:
            return o.get("value", o.get("default"))


def set_plugin_option(name, value, options):
    """
    Set value for option name for options dict.
    :param options:
    """
    for o in options:
        if o.get("name") == name:
            o.update({"value": value})

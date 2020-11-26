"""
.. module: horseradish.plugins.bases.notification
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from horseradish.plugins.base import Plugin


class NotificationPlugin(Plugin):
    """
    This is the base class from which all of the supported
    issuers will inherit from.
    """

    type = "notification"

    def send(self, notification_type, message, targets, options, **kwargs):
        raise NotImplementedError


class ExpirationNotificationPlugin(NotificationPlugin):
    """
    This is the base class for all expiration notification plugins.
    It contains some default options that are needed for all expiration
    notification plugins.
    """

    default_options = [
        {
            "name": "interval",
            "type": "int",
            "required": True,
            "validation": "^\d+$",
            "helpMessage": "Number of days to be alert before expiration.",
        },
        {
            "name": "unit",
            "type": "select",
            "required": True,
            "validation": "",
            "available": ["days", "weeks", "months"],
            "helpMessage": "Interval unit",
        },
    ]

    @property
    def options(self):
        return self.default_options + self.additional_options

    def send(self, notification_type, message, targets, options, **kwargs):
        raise NotImplementedError

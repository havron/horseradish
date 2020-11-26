"""
.. module: horseradish.exceptions
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from flask import current_app


class HorseradishException(Exception):
    def __init__(self, *args, **kwargs):
        current_app.logger.exception(self)


class DuplicateError(HorseradishException):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return repr("Duplicate found! Could not create: {0}".format(self.key))


class InvalidListener(HorseradishException):
    def __str__(self):
        return repr(
            "Invalid listener, ensure you select a certificate if you are using a secure protocol"
        )


class AttrNotFound(HorseradishException):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return repr("The field '{0}' is not sortable or filterable".format(self.field))


class InvalidConfiguration(Exception):
    pass


class InvalidAuthority(Exception):
    pass


class UnknownProvider(Exception):
    pass

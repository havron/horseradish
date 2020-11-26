"""
.. module: horseradish
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>

"""

import time
from flask import g, request
from horseradish import factory

from horseradish.auth.views import mod as auth_bp
from horseradish.users.views import mod as users_bp
from horseradish.roles.views import mod as roles_bp

# from horseradish.practice.views import mod as practice_bp

from horseradish.__about__ import (
    __author__,
    __copyright__,
    __email__,
    __license__,
    __summary__,
    __title__,
    __uri__,
    __version__,
)

__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
]

HORSERADISH_BLUEPRINTS = (
    auth_bp,
    users_bp,
    roles_bp,
    # practice_bp,
)


def create_app(config_path=None):
    app = factory.create_app(
        app_name=__name__, blueprints=HORSERADISH_BLUEPRINTS, config=config_path
    )

    configure_hook(app)
    return app


def configure_hook(app):
    """
    :param app:
    :return:
    """

    from flask import jsonify
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code

        app.logger.exception(e)
        return jsonify(error=str(e)), code

    @app.before_request
    def before_request():
        g.request_start_time = time.time()

    @app.after_request
    def after_request(response):
        # Return early if we don't have the start time
        if not hasattr(g, "request_start_time"):
            return response

        # Get elapsed time in milliseconds
        # elapsed = time.time() - g.request_start_time
        # elapsed = int(round(1000 * elapsed)

        # metrics could be sent here
        return response

"""
.. module: horseradish.factory
    :platform: Unix
    :synopsis: This module contains all the needed functions to allow
    the factory app creation.
    :copyright: (c) 2020 by Sam Havron. see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>

"""

import os
import importlib
import errno
import pkg_resources
import socket

from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_replicated import FlaskReplicated
import logmatic

from horseradish.common.health import mod as health
from horseradish.extensions import db, migrate, principal, metrics, sentry, cors

DEFAULT_BLUEPRINTS = (health,)

API_VERSION = 1


def create_app(app_name=None, blueprints=None, config=None):
    """
    Horseradish application factory

    :param config:
    :param app_name:
    :param blueprints:
    :return:
    """
    if not blueprints:
        blueprints = DEFAULT_BLUEPRINTS
    else:
        blueprints = blueprints + DEFAULT_BLUEPRINTS

    if not app_name:
        app_name = __name__

    app = Flask(app_name)
    configure_app(app, config)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_database(app)

    @app.teardown_appcontext
    def teardown(exception=None):
        if db.session:
            db.session.remove()

    return app


def from_file(file_path, silent=False):
    """
    Updates the values in the config from a Python file.  This function
    behaves as if the file was imported as module with the

    :param file_path:
    :param silent:
    """
    module_spec = importlib.util.spec_from_file_location("config", file_path)
    d = importlib.util.module_from_spec(module_spec)

    try:
        with open(file_path) as config_file:
            exec(  # nosec: config file safe
                compile(config_file.read(), file_path, "exec"), d.__dict__
            )
    except IOError as e:
        if silent and e.errno in (errno.ENOENT, errno.EISDIR):
            return False
        e.strerror = "Unable to load configuration file (%s)" % e.strerror
        raise
    return d


def configure_app(app, config=None):
    """
    Different ways of configuration

    :param app:
    :param config:
    :return:
    """
    # respect the config first
    if config and config != "None":
        app.config["CONFIG_PATH"] = config
        app.config.from_object(from_file(config))
    else:
        try:
            app.config.from_envvar("HORSERADISH_CONF")
        except RuntimeError:
            # look in default paths
            if os.path.isfile(os.path.expanduser("~/.horseradish/horseradish.conf.py")):
                app.config.from_object(
                    from_file(os.path.expanduser("~/.horseradish/horseradish.conf.py"))
                )
            else:
                app.config.from_object(
                    from_file(
                        os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            "default.conf.py",
                        )
                    )
                )

    # we don't use this
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def configure_extensions(app):
    """
    Attaches and configures any needed flask extensions
    to our app.

    :param app:
    """
    db.init_app(app)
    migrate.init_app(app, db)
    principal.init_app(app)
    # smtp_mail.init_app(app)
    # metrics.init_app(app)
    sentry.init_app(app)

    if app.config["CORS"]:
        app.config["CORS_HEADERS"] = "Content-Type"
        cors.init_app(
            app,
            resources=r"/api/*",
            headers="Content-Type",
            origin="*",
            supports_credentials=True,
        )


def configure_blueprints(app, blueprints):
    """
    We prefix our APIs with their given version so that we can support
    multiple concurrent API versions.

    :param app:
    :param blueprints:
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix="/api/{0}".format(API_VERSION))


def configure_database(app):
    if app.config.get("SQLALCHEMY_ENABLE_FLASK_REPLICATED"):
        FlaskReplicated(app)


def configure_logging(app):
    """
    Sets up application wide logging.

    :param app:
    """
    handler = RotatingFileHandler(
        app.config.get("LOG_FILE", "horseradish.log"),
        maxBytes=10000000,
        backupCount=100,
    )

    handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )

    if app.config.get("LOG_JSON", False):
        handler.setFormatter(
            logmatic.JsonFormatter(extra={"hostname": socket.gethostname()})
        )

    handler.setLevel(app.config.get("LOG_LEVEL", "DEBUG"))
    app.logger.setLevel(app.config.get("LOG_LEVEL", "DEBUG"))
    app.logger.addHandler(handler)

    stream_handler = StreamHandler()
    stream_handler.setLevel(app.config.get("LOG_LEVEL", "DEBUG"))
    app.logger.addHandler(stream_handler)

    if app.config.get("DEBUG_DUMP", False):
        pass

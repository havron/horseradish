"""
.. module: horseradish.common.health
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from flask import Blueprint
from horseradish.database import db
from horseradish.extensions import sentry

mod = Blueprint("healthCheck", __name__)


@mod.route("/healthcheck")
def health():
    try:
        if healthcheck(db):
            return "ok"
    except Exception:
        sentry.captureException()
        return "db check failed"


def healthcheck(db):
    with db.engine.connect() as connection:
        connection.execute("SELECT 1;")
    return True

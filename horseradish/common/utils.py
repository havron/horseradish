"""
.. module: lemur.common.utils
    :platform: Unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>
"""

import base64
import string
import random

import sqlalchemy
from flask_restful.reqparse import RequestParser
from sqlalchemy import and_, func

from horseradish.exceptions import InvalidConfiguration

paginated_parser = RequestParser()

paginated_parser.add_argument("count", type=int, default=10, location="args")
paginated_parser.add_argument("page", type=int, default=1, location="args")
paginated_parser.add_argument("sortDir", type=str, dest="sort_dir", location="args")
paginated_parser.add_argument("sortBy", type=str, dest="sort_by", location="args")
paginated_parser.add_argument("filter", type=str, location="args")
paginated_parser.add_argument("owner", type=str, location="args")


def base64encode(string):
    # Performs Base64 encoding of string to string using the base64.b64encode() function
    # which encodes bytes to bytes.
    return base64.b64encode(string.encode()).decode()


def get_psuedo_random_string():
    """
    Create a random and strongish challenge.
    """
    challenge = "".join(random.choice(string.ascii_uppercase) for x in range(6))  # noqa
    challenge += "".join(random.choice("~!@#$%^&*()_+") for x in range(6))  # noqa
    challenge += "".join(random.choice(string.ascii_lowercase) for x in range(6))
    challenge += "".join(random.choice(string.digits) for x in range(6))  # noqa
    return challenge


def validate_conf(app, required_vars):
    """
    Ensures that the given fields are set in the applications conf.
    :param app:
    :param required_vars: list
    """
    for var in required_vars:
        if var not in app.config:
            raise InvalidConfiguration(
                "Required variable '{var}' is not set in Horseradish's conf.".format(
                    var=var
                )
            )


# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/WindowedRangeQuery
def column_windows(session, column, windowsize):
    """Return a series of WHERE clauses against
    a given column that break it into windows.
    Result is an iterable of tuples, consisting of
    ((start, end), whereclause), where (start, end) are the ids.
    Requires a database that supports window functions,
    i.e. Postgresql, SQL Server, Oracle.
    Enhance this yourself !  Add a "where" argument
    so that windows of just a subset of rows can
    be computed.
    """

    def int_for_range(start_id, end_id):
        if end_id:
            return and_(column >= start_id, column < end_id)
        else:
            return column >= start_id

    q = session.query(
        column, func.row_number().over(order_by=column).label("rownum")
    ).from_self(column)

    if windowsize > 1:
        q = q.filter(sqlalchemy.text("rownum %% %d=1" % windowsize))

    intervals = [id for id, in q]

    while intervals:
        start = intervals.pop(0)
        if intervals:
            end = intervals[0]
        else:
            end = None
        yield int_for_range(start, end)


def windowed_query(q, column, windowsize):
    """"Break a Query into windows on a given column."""

    for whereclause in column_windows(q.session, column, windowsize):
        for row in q.filter(whereclause).order_by(column):
            yield row


def truthiness(s):
    """If input string resembles something truthy then return True, else False."""

    return s.lower() in ("true", "yes", "on", "t", "1")

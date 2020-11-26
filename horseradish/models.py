"""
.. module: horseradish.models
    :platform: Unix
    :synopsis: This module contains all of the associative tables
    that help define the many to many relationships established in Horseradish

    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from sqlalchemy import Column, Integer, ForeignKey, Index, UniqueConstraint

from horseradish.database import db

roles_users = db.Table(
    "roles_users",
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

Index("roles_users_ix", roles_users.c.user_id, roles_users.c.role_id)

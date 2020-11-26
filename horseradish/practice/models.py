"""
.. module: horseradish.practice.models
    :platform: unix
    :synopsis: This module contains all of the models need to create a user within
    horseradish
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Column, Boolean

from sqlalchemy_utils.types.arrow import ArrowType

from horseradish.database import db
from horseradish.models import roles_users

from horseradish.extensions import bcrypt


class Practice(db.Model):
    __tablename__ = "practice"
    id = Column(Integer, primary_key=True)
    user = relationship(
        "User",
        # secondary=users_practice,
        passive_deletes=True,
        lazy="dynamic",
    )

"""
.. module: horseradish.roles.models
    :platform: unix
    :synopsis: This module contains all of the models need to create a role within Horseradish

    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>

"""
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey

from horseradish.database import db
from horseradish.utils import Vault
from horseradish.models import (
    roles_users,
)


class Role(db.Model):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    username = Column(String(128))
    password = Column(Vault)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    third_party = Column(Boolean)
    users = relationship(
        "User", secondary=roles_users, passive_deletes=True, backref="role"
    )

    sensitive_fields = ("password",)

    def __repr__(self):
        return "Role(name={name})".format(name=self.name)

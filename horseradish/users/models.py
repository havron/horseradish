"""
.. module: horseradish.users.models
    :platform: unix
    :synopsis: This module contains all of the models need to create a user within
    horseradish
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Column, Boolean
from sqlalchemy.event import listen

from sqlalchemy_utils.types.arrow import ArrowType

from horseradish.database import db
from horseradish.models import roles_users

from horseradish.extensions import bcrypt


def hash_password(mapper, connect, target):
    """
    Helper function that is a listener and hashes passwords before
    insertion into the database.

    :param mapper:
    :param connect:
    :param target:
    """
    target.hash_password()


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    password = Column(String(128))
    active = Column(Boolean())
    confirmed_at = Column(ArrowType())
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(128), unique=True)
    profile_picture = Column(String(255))
    roles = relationship(
        "Role",
        secondary=roles_users,
        passive_deletes=True,
        backref=db.backref("user"),
        lazy="dynamic",
    )

    sensitive_fields = ("password",)

    def check_password(self, password):
        """
        Hash a given password and check it against the stored value
        to determine its validity.

        :param password:
        :return:
        """
        if self.password:
            return bcrypt.check_password_hash(self.password, password)

    def hash_password(self):
        """
        Generate the secure hash for the password.

        :return:
        """
        if self.password:
            self.password = bcrypt.generate_password_hash(self.password).decode("utf-8")

    @property
    def is_admin(self):
        """
        Determine if the current user has the 'admin' role associated
        with it.

        :return:
        """
        for role in self.roles:
            if role.name == "admin":
                return True

    def __repr__(self):
        return "User(username={username})".format(username=self.username)


listen(User, "before_insert", hash_password)

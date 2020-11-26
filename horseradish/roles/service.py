"""
.. module: service
    :platform: Unix
    :synopsis: This module contains all of the services level functions used to
    administer roles in Horseradish

    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from horseradish import database
from horseradish.roles.models import Role
from horseradish.users.models import User


def update(role_id, name, description, users):
    """
    Update a role

    :param role_id:
    :param name:
    :param description:
    :param users:
    :return:
    """
    role = get(role_id)
    role.name = name
    role.description = description
    role.users = users
    database.update(role)
    return role


def set_third_party(role_id, third_party_status=False):
    """
    Sets a role to be a third party role. A user should pretty much never
    call this directly.

    :param role_id:
    :param third_party_status:
    :return:
    """
    role = get(role_id)
    role.third_party = third_party_status
    database.update(role)
    return role


def create(
    name, password=None, description=None, username=None, users=None, third_party=False
):
    """
    Create a new role

    :param name:
    :param users:
    :param description:
    :param username:
    :param password:
    :return:
    """
    role = Role(
        name=name,
        description=description,
        username=username,
        password=password,
        third_party=third_party,
    )

    if users:
        role.users = users

    return database.create(role)


def get(role_id):
    """
    Retrieve a role by ID

    :param role_id:
    :return:
    """
    return database.get(Role, role_id)


def get_by_name(role_name):
    """
    Retrieve a role by its name

    :param role_name:
    :return:
    """
    return database.get(Role, role_name, field="name")


def delete(role_id):
    """
    Remove a role

    :param role_id:
    :return:
    """
    return database.delete(get(role_id))


def render(args):
    """
    Helper that filters subsets of roles depending on the parameters
    passed to the REST Api

    :param args:
    :return:
    """
    query = database.session_query(Role)
    filt = args.pop("filter")
    user_id = args.pop("user_id", None)
    authority_id = args.pop("authority_id", None)

    if user_id:
        query = query.filter(Role.users.any(User.id == user_id))

    if authority_id:
        query = query.filter(Role.authority_id == authority_id)

    if filt:
        terms = filt.split(";")
        query = database.filter(query, Role, terms)

    return database.sort_and_page(query, Role, args)

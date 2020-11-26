"""
.. module: horseradish.auth.permissions
    :platform: Unix
    :synopsis: This module defines all the permission used within Horseradish
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from functools import partial
from collections import namedtuple

from flask import current_app
from flask_principal import Permission, RoleNeed

# Permissions
operator_permission = Permission(RoleNeed("operator"))
admin_permission = Permission(RoleNeed("admin"))
admin_or_operator_permission = admin_permission.union(operator_permission)


class ApiKeyCreatorPermission(Permission):
    def __init__(self):
        super(ApiKeyCreatorPermission, self).__init__(RoleNeed("admin"))


RoleMember = namedtuple("role", ["method", "value"])
RoleMemberNeed = partial(RoleMember, "member")


class RoleMemberPermission(Permission):
    def __init__(self, role_id):
        needs = [RoleNeed("admin"), RoleMemberNeed(role_id)]
        super(RoleMemberPermission, self).__init__(*needs)

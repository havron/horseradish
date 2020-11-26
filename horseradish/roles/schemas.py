"""
.. module: horseradish.roles.schemas
    :platform: unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from marshmallow import fields
from horseradish.users.schemas import UserNestedOutputSchema
from horseradish.common.schema import HorseradishInputSchema, HorseradishOutputSchema
from horseradish.schemas import AssociatedUserSchema


class RoleInputSchema(HorseradishInputSchema):
    id = fields.Integer()
    name = fields.String(required=True)
    username = fields.String()
    password = fields.String()
    description = fields.String()
    users = fields.Nested(AssociatedUserSchema, many=True)


class RoleOutputSchema(HorseradishOutputSchema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    third_party = fields.Boolean()
    users = fields.Nested(UserNestedOutputSchema, many=True)


class RoleNestedOutputSchema(HorseradishOutputSchema):
    __envelope__ = False
    id = fields.Integer()
    name = fields.String()
    description = fields.String()


role_input_schema = RoleInputSchema()
role_output_schema = RoleOutputSchema()
roles_output_schema = RoleOutputSchema(many=True)

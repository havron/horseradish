"""
.. module: horseradish.users.schemas
    :platform: unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>
"""
from marshmallow import fields

from horseradish.common.schema import HorseradishInputSchema, HorseradishOutputSchema
from horseradish.schemas import (
    AssociatedRoleSchema,
)


class UserInputSchema(HorseradishInputSchema):
    id = fields.Integer()
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String()  # TODO add complexity requirements
    active = fields.Boolean()
    roles = fields.Nested(AssociatedRoleSchema, many=True, missing=[])


class UserOutputSchema(HorseradishOutputSchema):
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    active = fields.Boolean()
    roles = fields.Nested(AssociatedRoleSchema, many=True)
    profile_picture = fields.String()


user_input_schema = UserInputSchema()
user_output_schema = UserOutputSchema()
users_output_schema = UserOutputSchema(many=True)


class UserNestedOutputSchema(HorseradishOutputSchema):
    __envelope__ = False
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    active = fields.Boolean()

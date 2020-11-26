"""
.. module: horseradish.schemas
    :platform: unix
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Sam Havron <havron@hey.com>

"""
from sqlalchemy.orm.exc import NoResultFound

from marshmallow import fields, post_load, pre_load, post_dump
from marshmallow.exceptions import ValidationError

from horseradish.common import validators
from horseradish.common.schema import (
    HorseradishSchema,
    HorseradishInputSchema,
    HorseradishOutputSchema,
)

from horseradish.plugins import plugins
from horseradish.plugins.utils import get_plugin_option
from horseradish.roles.models import Role
from horseradish.users.models import User


def validate_options(options):
    """
    Ensures that the plugin options are valid.
    :param options:
    :return:
    """
    interval = get_plugin_option("interval", options)
    unit = get_plugin_option("unit", options)

    if not interval and not unit:
        return

    if unit == "month":
        interval *= 30

    elif unit == "week":
        interval *= 7

    if interval > 90:
        raise ValidationError(
            "Notification cannot be more than 90 days into the future."
        )


def get_object_attribute(data, many=False):
    if many:
        ids = [d.get("id") for d in data]
        names = [d.get("name") for d in data]

        if None in ids:
            if None in names:
                raise ValidationError("Associated object require a name or id.")
            else:
                return "name"
        return "id"
    else:
        if data.get("id"):
            return "id"
        elif data.get("name"):
            return "name"
        else:
            raise ValidationError("Associated object require a name or id.")


def fetch_objects(model, data, many=False):
    attr = get_object_attribute(data, many=many)

    if many:
        values = [v[attr] for v in data]
        items = model.query.filter(getattr(model, attr).in_(values)).all()
        found = [getattr(i, attr) for i in items]
        diff = set(values).symmetric_difference(set(found))

        if diff:
            raise ValidationError(
                "Unable to locate {model} with {attr} {diff}".format(
                    model=model, attr=attr, diff=",".join(list(diff))
                )
            )

        return items

    else:
        try:
            return model.query.filter(getattr(model, attr) == data[attr]).one()
        except NoResultFound:
            raise ValidationError(
                "Unable to find {model} with {attr}: {data}".format(
                    model=model, attr=attr, data=data[attr]
                )
            )


class AssociatedRoleSchema(HorseradishInputSchema):
    id = fields.Int()
    name = fields.String()

    @post_load
    def get_object(self, data, many=False):
        return fetch_objects(Role, data, many=many)


class AssociatedUserSchema(HorseradishInputSchema):
    id = fields.Int()
    name = fields.String()

    @post_load
    def get_object(self, data, many=False):
        return fetch_objects(User, data, many=many)


class PluginInputSchema(HorseradishInputSchema):
    plugin_options = fields.List(fields.Dict(), validate=validate_options)
    slug = fields.String(required=True)
    title = fields.String()
    description = fields.String()

    @post_load
    def get_object(self, data, many=False):
        try:
            data["plugin_object"] = plugins.get(data["slug"])

            # parse any sub-plugins
            for option in data.get("plugin_options", []):
                if "plugin" in option.get("type", []):
                    sub_data, errors = PluginInputSchema().load(option["value"])
                    option["value"] = sub_data

            return data
        except Exception as e:
            raise ValidationError(
                "Unable to find plugin. Slug: {0} Reason: {1}".format(data["slug"], e)
            )


class PluginOutputSchema(HorseradishOutputSchema):
    id = fields.Integer()
    label = fields.String()
    description = fields.String()
    active = fields.Boolean()
    options = fields.List(fields.Dict(), dump_to="pluginOptions")
    slug = fields.String()
    title = fields.String()


plugins_output_schema = PluginOutputSchema(many=True)
plugin_output_schema = PluginOutputSchema


class BaseExtensionSchema(HorseradishSchema):
    @pre_load(pass_many=True)
    def preprocess(self, data, many):
        return self.under(data, many=many)

    @post_dump(pass_many=True)
    def post_process(self, data, many):
        if data:
            data = self.camel(data, many=many)
        return data

"""
.. module: horseradish.auth.service
    :platform: Unix
    :synopsis: This module contains all of the authentication duties for
    horseradish
    :copyright: (c) 2020 by Sam Havron, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Sam Havron <havron@hey.com>

"""
import jwt
import json
import binascii

from functools import wraps
from datetime import datetime, timedelta

from flask import g, current_app, jsonify, request

from flask_restful import Resource
from flask_principal import identity_loaded, RoleNeed, UserNeed

from flask_principal import Identity, identity_changed

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from horseradish.users import service as user_service
from horseradish.roles import service as role_service
from horseradish.api_keys import service as api_key_service
from horseradish.auth.permissions import RoleMemberNeed


def idp_groups_to_roles(profile):
    """
    Squarespace/shavron: Maps identity-provider defined groups in profile
    information to Horseradish roles.

    :param profile:
    :yield: Horseradish role that is allowed for the user
    """
    idp_groups_to_roles = current_app.config.get("IDP_GROUPS_TO_ROLES")
    idp_groups_key = current_app.config.get("IDP_GROUPS_KEY")

    if not idp_groups_to_roles or not idp_groups_key or idp_groups_key not in profile:
        return

    for idp_group_name, role_name in idp_groups_to_roles.items():
        role = role_service.get_by_name(role_name)

        if not role or idp_group_name not in profile[idp_groups_key]:
            continue

        current_app.logger.info(
            'Role {0} is available to user {1}, who is in the "{2}" IDP group'.format(
                role, profile["email"], idp_group_name
            )
        )

        if not role.third_party:
            role = role_service.set_third_party(role.id, third_party_status=True)
        yield role


def get_rsa_public_key(n, e):
    """
    Retrieve an RSA public key based on a module and exponent as provided by the JWKS format.

    :param n:
    :param e:
    :return: a RSA Public Key in PEM format
    """
    n = int(binascii.hexlify(jwt.utils.base64url_decode(bytes(n, "utf-8"))), 16)
    e = int(binascii.hexlify(jwt.utils.base64url_decode(bytes(e, "utf-8"))), 16)

    pub = RSAPublicNumbers(e, n).public_key(default_backend())
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def create_token(user, aid=None, ttl=None):
    """
    Create a valid JWT for a given user/api key, this token is then used to authenticate
    sessions until the token expires.

    :param user:
    :return:
    """
    expiration_delta = timedelta(
        days=int(current_app.config.get("HORSERADISH_TOKEN_EXPIRATION", 1))
    )
    payload = {"iat": datetime.utcnow(), "exp": datetime.utcnow() + expiration_delta}

    # Handle Just a User ID & User Object.
    if isinstance(user, int):
        payload["sub"] = user
    else:
        payload["sub"] = user.id
    if aid is not None:
        payload["aid"] = aid
    # Custom TTLs are only supported on Access Keys.
    if ttl is not None and aid is not None:
        # Tokens that are forever until revoked.
        if ttl == -1:
            del payload["exp"]
        else:
            payload["exp"] = ttl
    token = jwt.encode(payload, current_app.config["HORSERADISH_TOKEN_SECRET"])
    return token.decode("unicode_escape")


def login_required(f):
    """
    Validates the JWT and ensures that is has not expired and the user is still active.

    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get("Authorization"):
            response = jsonify(message="Missing authorization header")
            response.status_code = 401
            return response

        try:
            token = request.headers.get("Authorization").split()[1]
        except Exception as e:
            return dict(message="Token is invalid"), 403

        try:
            payload = jwt.decode(token, current_app.config["HORSERADISH_TOKEN_SECRET"])
        except jwt.DecodeError:
            return dict(message="Token is invalid"), 403
        except jwt.ExpiredSignatureError:
            return dict(message="Token has expired"), 403
        except jwt.InvalidTokenError:
            return dict(message="Token is invalid"), 403

        if "aid" in payload:
            access_key = api_key_service.get(payload["aid"])
            if access_key.revoked:
                return dict(message="Token has been revoked"), 403
            if access_key.ttl != -1:
                current_time = datetime.utcnow()
                expired_time = datetime.fromtimestamp(
                    access_key.issued_at + access_key.ttl
                )
                if current_time >= expired_time:
                    return dict(message="Token has expired"), 403

        user = user_service.get(payload["sub"])

        if not user.active:
            return dict(message="User is not currently active"), 403

        g.current_user = user

        if not g.current_user:
            return dict(message="You are not logged in"), 403

        # Tell Flask-Principal the identity changed
        identity_changed.send(
            current_app._get_current_object(), identity=Identity(g.current_user.id)
        )

        return f(*args, **kwargs)

    return decorated_function


def fetch_token_header(token):
    """
    Fetch the header out of the JWT token.

    :param token:
    :return: :raise jwt.DecodeError:
    """
    token = token.encode("utf-8")
    try:
        signing_input, crypto_segment = token.rsplit(b".", 1)
        header_segment, payload_segment = signing_input.split(b".", 1)
    except ValueError:
        raise jwt.DecodeError("Not enough segments")

    try:
        return json.loads(jwt.utils.base64url_decode(header_segment).decode("utf-8"))
    except TypeError as e:
        current_app.logger.exception(e)
        raise jwt.DecodeError("Invalid header padding")


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    """
    Sets the identity of a given option, assigns additional permissions based on
    the role that the user is a part of.

    :param sender:
    :param identity:
    """
    # load the user
    user = user_service.get(identity.id)

    # add the UserNeed to the identity
    identity.provides.add(UserNeed(identity.id))

    # identity with the roles that the user provides
    if hasattr(user, "roles"):
        for role in user.roles:
            identity.provides.add(RoleNeed(role.name))
            identity.provides.add(RoleMemberNeed(role.id))

    # apply ownership for authorities
    # if hasattr(user, "authorities"):
    #    for authority in user.authorities:
    #        identity.provides.add(AuthorityCreatorNeed(authority.id))

    g.user = user


class AuthenticatedResource(Resource):
    """
    Inherited by all resources that need to be protected by authentication.
    """

    method_decorators = [login_required]

    def __init__(self):
        super(AuthenticatedResource, self).__init__()

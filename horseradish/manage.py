#!/usr/bin/env python
from __future__ import unicode_literals  # at top of module

import os
import sys
import base64

# import requests
# import json

from gunicorn.config import make_settings

from cryptography.fernet import Fernet

from flask import current_app
from flask_script import Manager, Command, Option, prompt_pass
from flask_migrate import Migrate, MigrateCommand, stamp
from flask_script.commands import ShowUrls, Clean, Server

from horseradish import database
from horseradish.users import service as user_service
from horseradish.roles import service as role_service
from horseradish.common.utils import validate_conf

from horseradish import create_app

# Import models for SQLAlchemy
""" implement later """

from sqlalchemy.sql import text

manager = Manager(create_app)
manager.add_option("-c", "--config", dest="config_path", required=False)

migrate = Migrate(create_app)

REQUIRED_VARIABLES = [
    "SQLALCHEMY_DATABASE_URI",
]

KEY_LENGTH = 40
DEFAULT_CONFIG_PATH = "~/.horseradish/horseradish.conf.py"
DEFAULT_SETTINGS = "horseradish.conf.server"
SETTINGS_ENVVAR = "HORSERADISH_CONF"

CONFIG_TEMPLATE = """
import os
_basedir = os.path.abspath(os.path.dirname(__file__))

THREADS_PER_PAGE = 8

# General

# These will need to be set to `True` if you are developing locally
CORS = False
debug = False

# this is the secret key used by flask session management
SECRET_KEY = '{flask_secret_key}'

# You should consider storing these separately from your config
HORSERADISH_TOKEN_SECRET = '{secret_token}'
HORSERADISH_ENCRYPTION_KEYS = '{encryption_key}'

# Logging
LOG_LEVEL = "DEBUG"
LOG_FILE = "horseradish.log"
LOG_UPGRADE_FILE = "db_upgrade.log"

# Database
# modify this if you are not using a local database
SQLALCHEMY_DATABASE_URI = 'postgresql://horseradish:horseradish@localhost:5432/horseradish'
"""


@MigrateCommand.command
def create():
    database.db.engine.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    database.db.create_all()
    stamp(revision="head")


@MigrateCommand.command
def drop_all():
    database.db.drop_all()


@manager.shell
def make_shell_context():
    """
    Creates a python REPL with several default imports
    in the context of the current_app
    :return:
    """
    return dict(current_app=current_app)


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """
    output = CONFIG_TEMPLATE.format(
        # we use Fernet.generate_key to make sure that the key length is
        # compatible with Fernet
        encryption_key=Fernet.generate_key().decode("utf-8"),
        secret_token=base64.b64encode(os.urandom(KEY_LENGTH)).decode("utf-8"),
        flask_secret_key=base64.b64encode(os.urandom(KEY_LENGTH)).decode("utf-8"),
    )

    return output


class InitializeApp(Command):
    """
    This command will bootstrap our database.
    """

    option_list = (Option("-p", "--password", dest="password"),)

    def run(self, password):
        create()
        user = user_service.get_by_username("horseradish")

        admin_role = role_service.get_by_name("admin")

        if admin_role:
            sys.stdout.write("[-] Admin role already created, skipping...!\n")
        else:
            # we create an admin role
            admin_role = role_service.create(
                "admin", description="This is the Horseradish administrator role."
            )
            sys.stdout.write("[+] Created 'admin' role\n")

        read_only_role = role_service.get_by_name("read-only")

        if read_only_role:
            sys.stdout.write("[-] Read only role already created, skipping...!\n")
        else:
            # we create an read only role
            read_only_role = role_service.create(
                "read-only", description="This is the Horseradish read only role."
            )
            sys.stdout.write("[+] Created 'read-only' role\n")

        if not user:
            if not password:
                sys.stdout.write("We need to set Horseradish's password to continue!\n")
                password = prompt_pass("Password")
                password1 = prompt_pass("Confirm Password")

                if password != password1:
                    sys.stderr.write("[!] Passwords do not match!\n")
                    sys.exit(1)

            user_service.create(
                "horseradish",
                password,
                "horseradish@nobody.com",
                True,
                None,
                [admin_role],
            )
            sys.stdout.write(
                "[+] Created the user 'horseradish' and granted it the 'admin' role!\n"
            )

        else:
            sys.stdout.write(
                "[-] Default user has already been created, skipping...!\n"
            )

        sys.stdout.write("[/] Done!\n")


class CreateUser(Command):
    """
    This command allows for the creation of a new user within Horseradish.
    """

    option_list = (
        Option("-u", "--username", dest="username", required=True),
        Option("-e", "--email", dest="email", required=True),
        Option("-a", "--active", dest="active", default=True),
        Option("-r", "--roles", dest="roles", action="append", default=[]),
        Option("-p", "--password", dest="password", default=None),
    )

    def run(self, username, email, active, roles, password):
        role_objs = []
        for r in roles:
            role_obj = role_service.get_by_name(r)
            if role_obj:
                role_objs.append(role_obj)
            else:
                sys.stderr.write("[!] Cannot find role {0}\n".format(r))
                sys.exit(1)

        if not password:
            password1 = prompt_pass("Password")
            password2 = prompt_pass("Confirm Password")
            password = password1

            if password1 != password2:
                sys.stderr.write("[!] Passwords do not match!\n")
                sys.exit(1)

        user_service.create(username, password, email, active, None, role_objs)
        sys.stdout.write("[+] Created new user: {0}\n".format(username))


class ResetPassword(Command):
    """
    This command allows you to reset a user's password.
    """

    option_list = (Option("-u", "--username", dest="username", required=True),)

    def run(self, username):
        user = user_service.get_by_username(username)

        if not user:
            sys.stderr.write("[!] No user found for username: {0}\n".format(username))
            sys.exit(1)

        sys.stderr.write("[+] Resetting password for {0}\n".format(username))
        password1 = prompt_pass("Password")
        password2 = prompt_pass("Confirm Password")

        if password1 != password2:
            sys.stderr.write("[!] Passwords do not match\n")
            sys.exit(1)

        user.password = password1
        user.hash_password()
        database.commit()


class CreateRole(Command):
    """
    This command allows for the creation of a new role within Horseradish
    """

    option_list = (
        Option("-n", "--name", dest="name", required=True),
        Option("-u", "--users", dest="users", default=[]),
        Option("-d", "--description", dest="description", required=True),
    )

    def run(self, name, users, description):
        user_objs = []
        for u in users:
            user_obj = user_service.get_by_username(u)
            if user_obj:
                user_objs.append(user_obj)
            else:
                sys.stderr.write("[!] Cannot find user {0}".format(u))
                sys.exit(1)
        role_service.create(name, description=description, users=users)
        sys.stdout.write("[+] Created new role: {0}".format(name))


class HorseradishServer(Command):
    """
    This is the main Horseradish server, it runs the flask app with gunicorn and
    uses any configuration options passed to it.
    You can pass all standard gunicorn flags to this command as if you were
    running gunicorn itself.
    For example:
    horseradish start -w 4 -b 127.0.0.0:8002
    Will start gunicorn with 4 workers bound to 127.0.0.0:8002
    """

    description = "Run the app within Gunicorn"

    def get_options(self):
        settings = make_settings()
        options = []
        for setting, klass in settings.items():
            if klass.cli:
                if klass.action:
                    if klass.action == "store_const":
                        options.append(
                            Option(*klass.cli, const=klass.const, action=klass.action)
                        )
                    else:
                        options.append(Option(*klass.cli, action=klass.action))
                else:
                    options.append(Option(*klass.cli))

        return options

    def run(self, *args, **kwargs):
        from gunicorn.app.wsgiapp import WSGIApplication

        app = WSGIApplication()

        # run startup tasks on an app like object
        validate_conf(current_app, REQUIRED_VARIABLES)

        app.app_uri = 'horseradish:create_app(config_path="{0}")'.format(
            current_app.config.get("CONFIG_PATH")
        )

        return app.run()


@manager.command
def create_config(config_path=None):
    """
    Creates a new configuration file if one does not already exist
    """
    if not config_path:
        config_path = DEFAULT_CONFIG_PATH

    config_path = os.path.expanduser(config_path)
    dir = os.path.dirname(config_path)

    if not os.path.exists(dir):
        os.makedirs(dir)

    config = generate_settings()
    with open(config_path, "w") as f:
        f.write(config)

    sys.stdout.write("[+] Created a new configuration file {0}\n".format(config_path))


@manager.command
def lock(path=None):
    """
    Encrypts a given path. This directory can be used to store secrets needed for normal
    Horseradish operation. This is especially useful for storing secrets needed for communication
    with third parties (e.g. external certificate authorities).

    Horseradish does not assume anything about the contents of the directory and will attempt to
    encrypt all files contained within. Currently this has only been tested against plain
    text files.

    Path defaults ~/.horseradish/keys

    :param: path
    """
    if not path:
        path = os.path.expanduser("~/.horseradish/keys")

    dest_dir = os.path.join(path, "encrypted")
    sys.stdout.write("[!] Generating a new key...\n")

    key = Fernet.generate_key()

    if not os.path.exists(dest_dir):
        sys.stdout.write("[+] Creating encryption directory: {0}\n".format(dest_dir))
        os.makedirs(dest_dir)

    for root, dirs, files in os.walk(os.path.join(path, "decrypted")):
        for f in files:
            source = os.path.join(root, f)
            dest = os.path.join(dest_dir, f + ".enc")
            with open(source, "rb") as in_file, open(dest, "wb") as out_file:
                f = Fernet(key)
                data = f.encrypt(in_file.read())
                out_file.write(data)
                sys.stdout.write(
                    "[+] Writing file: {0} Source: {1}\n".format(dest, source)
                )

    sys.stdout.write("[+] Keys have been encrypted with key {0}\n".format(key))


@manager.command
def unlock(path=None):
    """
    Decrypts all of the files in a given directory with provided password.
    This is most commonly used during the startup sequence of Horseradish
    allowing it to go from source code to something that can communicate
    with external services.

    Path defaults ~/.horseradish/keys

    :param: path
    """
    key = prompt_pass("[!] Please enter the encryption password")

    if not path:
        path = os.path.expanduser("~/.horseradish/keys")

    dest_dir = os.path.join(path, "decrypted")
    source_dir = os.path.join(path, "encrypted")

    if not os.path.exists(dest_dir):
        sys.stdout.write("[+] Creating decryption directory: {0}\n".format(dest_dir))
        os.makedirs(dest_dir)

    for root, dirs, files in os.walk(source_dir):
        for f in files:
            source = os.path.join(source_dir, f)
            dest = os.path.join(dest_dir, ".".join(f.split(".")[:-1]))
            with open(source, "rb") as in_file, open(dest, "wb") as out_file:
                f = Fernet(key)
                data = f.decrypt(in_file.read())
                out_file.write(data)
                sys.stdout.write(
                    "[+] Writing file: {0} Source: {1}\n".format(dest, source)
                )

    sys.stdout.write("[+] Keys have been unencrypted!\n")


def main():
    manager.add_command("start", HorseradishServer())
    manager.add_command("runserver", Server(host="127.0.0.1", threaded=True))
    manager.add_command("clean", Clean())
    manager.add_command("show_urls", ShowUrls())
    manager.add_command("db", MigrateCommand)
    manager.add_command("init", InitializeApp())
    manager.add_command("create_user", CreateUser())
    manager.add_command("reset_password", ResetPassword())
    manager.add_command("create_role", CreateRole())
    manager.run()


if __name__ == "__main__":
    main()

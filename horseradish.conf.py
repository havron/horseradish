import os

_basedir = os.path.abspath(os.path.dirname(__file__))

THREADS_PER_PAGE = 8

# General

# These will need to be set to `True` if you are developing locally
CORS = False
debug = False

# this is the secret key used by flask session management
SECRET_KEY = "n0VZQAG3DxopW5G5wv/a7cUfbYhjx5xX9HNPfYlfnrS7v6dypx0tFA=="

# You should consider storing these separately from your config
HORSERADISH_TOKEN_SECRET = "HnAip3t0FzLsQRL1s+6clioGqQFJt5ydupQqQ2cptsJbHqLyldWsGg=="
HORSERADISH_ENCRYPTION_KEYS = "faieHLYEOndlOmTH3JiouzvnhM0rQ1u4ZFboYpIwfDI="

# Logging
LOG_LEVEL = "DEBUG"
LOG_FILE = "horseradish.log"
LOG_UPGRADE_FILE = "db_upgrade.log"

# Database
# modify this if you are not using a local database
SQLALCHEMY_DATABASE_URI = (
    "postgresql://horseradish:horseradish@localhost:5432/horseradish"
)

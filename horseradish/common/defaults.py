import re
import unicodedata

from flask import current_app

from horseradish.extensions import sentry


def text_to_slug(value, joiner="-"):
    """
    Normalize a string to a "slug" value, stripping character accents and removing non-alphanum characters.
    A series of non-alphanumeric characters is replaced with the joiner character.
    """

    # Strip all character accents: decompose Unicode characters and then drop combining chars.
    value = "".join(
        c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)
    )

    # Replace all remaining non-alphanumeric characters with joiner string. Multiple characters get collapsed into a
    # single joiner. Except, keep 'xn--' used in IDNA domain names as is.
    value = re.sub(r"[^A-Za-z0-9.]+(?<!xn--)", joiner, value)

    # '-' in the beginning or end of string looks ugly.
    return value.strip(joiner)

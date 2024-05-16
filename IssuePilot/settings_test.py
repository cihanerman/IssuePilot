import os

from .settings import * # noqa

DATABASES["default"].update(
    {
        "NAME": os.getenv("DB_NAME", default="test_pilot"),
        "USER": os.getenv("DB_USER", default="postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", default="password"),
        "HOST": os.getenv("DB_HOST", default="localhost"),
        "PORT": os.getenv("DB_PORT", default="5432"),
    }
)

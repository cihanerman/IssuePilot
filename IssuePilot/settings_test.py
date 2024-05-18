import os

from .settings import *  # noqa

DATABASES["default"].update(  # noqa
    {
        "NAME": os.getenv("DB_NAME", default="test_pilot"),
        "USER": os.getenv("DB_USER", default="postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", default="password"),
        "HOST": os.getenv("DB_HOST", default="localhost"),
        "PORT": os.getenv("DB_PORT", default="5432"),
    }
)

CELERY_TASK_ALWAYS_EAGER = True
DEBUG = False

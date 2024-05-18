import os

from celery import Celery

from IssuePilot.beat_schedule import CELERY_BEAT_SCHEDULE

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IssuePilot.settings")

app = Celery("IssuePilot")
app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

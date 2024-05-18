from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check_repositories_update": {
        "task": "pilot.tasks.check_users_repositories_update",
        "schedule": crontab(minute="*/1"),
    }
}

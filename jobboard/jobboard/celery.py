import os
from celery import Celery
"""
Celery Configuration for the Job Board Project.

This module sets up Celery to work with Django.
Purpose:
- To send email notifications asynchronously.
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobboard.settings")

app = Celery("jobboard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

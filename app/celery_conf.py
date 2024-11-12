import os

from celery import Celery

celery_app = Celery(
    'main',
    broker=os.getenv("CELERY_BROKER_URL", "amqp://guest@localhost//"),
    backend=os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379/0"),
    include=['app.services.tasks']
)
celery_app.autodiscover_tasks()
celery_app.conf.hostname = 'localhost'
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.task_track_started = True

from celery import Celery
from core.config import config

celery_app = Celery(
    "documind",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    include=["tasks.indexing"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)
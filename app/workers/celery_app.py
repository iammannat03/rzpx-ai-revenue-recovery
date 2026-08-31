from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery("revenue_recovery", broker=settings.celery_broker_url)
celery_app.conf.task_ignore_result = (
    True  # results written to Postgres directly, not via Celery
)

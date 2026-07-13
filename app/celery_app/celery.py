from celery import Celery

from app.core.config import settings

celery_app = Celery("support", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

import app.celery_app.tasks  

from django.conf import settings
from celery import Celery
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pingApi.settings')
app = Celery('pingApi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.broker_url = settings.BASE_REDIS_URL
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
app.conf.timezone = settings.TIME_ZONE

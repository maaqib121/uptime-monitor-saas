from django.conf import settings
from celery import Celery
from celery.schedules import crontab
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pingApi.settings')
app = Celery('pingApi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.broker_url = settings.BASE_REDIS_URL
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
app.conf.timezone = settings.TIME_ZONE
app.conf.beat_schedule = {
    'ping': {
        'task': 'tasks.ping',
        'schedule': crontab(minute=0, hour='*/1')
    },
    'get_domain_uptime_results': {
        'task': 'tasks.get_domain_uptime_results',
        'schedule': crontab()
    },
    'sync_google_analytics_domains': {
        'task': 'tasks.sync_google_analytics',
        'schedule': crontab(minute=0, hour='*/1')
    }
}

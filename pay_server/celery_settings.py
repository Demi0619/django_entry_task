import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pay_server.settings')

app = Celery('pay_server', broker='pyamqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
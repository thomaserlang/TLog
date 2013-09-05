from celery import Celery
from celery.task import periodic_task
from celery.task.schedules import crontab
from tlog.config import Config



celery = Celery('tasks', broker='amqp://guest@localhost//', backend='amqp://guest@localhost//')

@celery.task
def add(x, y):
    return x + y

@periodic_task(
    run_every=crontab(minute='*'),
)
def check_filter_warnings():
    pass
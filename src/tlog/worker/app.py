import logging
import os
from tlog.config import Config
Config.load()
from celery.signals import setup_logging
from tlog.logger import logger
from celery import Celery
from celery.loaders.base import BaseLoader

def init_logging(*arg, **kwargs):
    logger.set_logger('worker.log')
    return logging.getLogger()

setup_logging.connect(init_logging)

celery = Celery(
    'tlog.worker.app',
    broker=Config.data['celery']['broker'],
    backend=Config.data['celery']['backend'],
    include=[
        'tlog.worker.receiver',
    ],
)

def main():
    celery.start()

if __name__ == '__main__':
    main()
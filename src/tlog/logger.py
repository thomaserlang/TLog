import logging
import logging.handlers
import os
from tlog.config import Config

class logger(object):

    @classmethod
    def set_logger(cls, filename):
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, Config.data['logging']['level'].upper()))
        if Config.data['logging']['path']:
            channel = logging.handlers.RotatingFileHandler(
                filename=os.path.join(Config.data['logging']['path'], filename),
                maxBytes=Config.data['logging']['max_size'],
                backupCount=Config.data['logging']['num_backups']
            )
            channel.setFormatter(logging.Formatter('[%(levelname)s %(asctime)s.%(msecs)d %(module)s:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            logger.addHandler(channel)
        if not logger.handlers:# send to console instead of file
            channel = logging.StreamHandler()
            channel.setFormatter(logging.Formatter('[%(levelname)s %(asctime)s.%(msecs)d %(module)s:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            logger.addHandler(channel)
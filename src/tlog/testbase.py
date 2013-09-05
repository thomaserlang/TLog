import os
from unittest2 import TestCase
from tlog.config import Config
from tlog import migrate
from tlog.connections import database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tlog.logger import logger

class Testbase(TestCase):
    def setUp(self):
        Config.load()
        Config.data['logging']['path'] = None
        Config.data['celery']['enabled'] = False
        logger.set_logger('test.log')
        super(Testbase, self).setUp()
        engine = create_engine(Config.data['database']['url'], convert_unicode=True, echo=False)
        connection = engine.connect()
        self.trans = connection.begin()
        database.session = sessionmaker(bind=connection)

    def tearDown(self):
        self.trans.rollback()
        super(Testbase, self).tearDown()
import alembic.config
import logging
import os
from alembic import context
from tlog.config import Config
from alembic import command

def get_config():
    logging.info('Trying to locate alembic.ini in {}'.format(os.path.dirname(os.path.abspath(__file__))+'/../../alembic.ini'))
    cfg = alembic.config.Config(os.path.dirname(os.path.abspath(__file__))+'/../../alembic.ini')
    cfg.set_main_option('script_location', 'tlog:migrations')
    cfg.set_main_option('url', Config.data['database']['url'])
    return cfg

def upgrade():
    cfg = get_config()
    command.upgrade(cfg, 'head')

if __name__ == '__main__':
    Config.load()
    upgrade()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tlog.config import Config

class Database:
    def __init__(self):
        self.engine = create_engine(
            Config.data['database']['url'],
            convert_unicode=True,
            echo=False,
            pool_recycle=3600,
        )
        self.session = sessionmaker(
            bind=self.engine,
        )

database = Database()
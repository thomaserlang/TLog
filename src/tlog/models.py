from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, Numeric, ForeignKey, event, TIMESTAMP, Date, SmallInteger, CHAR
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

base = declarative_base()

class Log(base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(32), nullable=False, unique=True)
    hostname = Column(String(45))
    received = Column(TIMESTAMP)
    message_hash = Column(String(40))
    level = Column(Integer, nullable=False)
    data = Column(Text)
    log_group_id = Column(Integer, ForeignKey('log_group.id'))

class User(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45))
    email = Column(String(45), nullable=False, unique=True)
    password = Column(CHAR(60))
    notification_types = Column(Text)

class User_team(base):
    __tablename__ = 'user_teams'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, autoincrement=False)
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True, autoincrement=False)

class Team(base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), unique=True)

class Log_group(base):
    __tablename__ = 'log_group'
    id = Column(Integer, autoincrement=True, primary_key=True)
    message = Column(String(200))
    message_hash = Column(String(40), unique=True)
    first_seen = Column(TIMESTAMP, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP, index=True)
    last_log_id = Column(Integer)
    times_seen = Column(Integer, server_default='0')
    level = Column(Integer)
    score = Column(Integer, index=True)
    status = Column(Integer, index=True, server_default='0')
    reopened = Column(TIMESTAMP)

class Log_group_event(base):
    __tablename__ = 'log_group_events'
    id = Column(Integer, autoincrement=True, primary_key=True)
    log_group_id = Column(Integer, ForeignKey('log_group.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String(200))
    time = Column(TIMESTAMP)

class Log_group_server(base):
    __tablename__ = 'log_group_servers'
    name = Column(String(45), primary_key=True)
    log_group_id = Column(Integer, ForeignKey('log_group.id'), primary_key=True, autoincrement=False)
    count = Column(Integer, server_default='0')

class Times_seen_by_minute(base):
    __tablename__ = 'times_seen_by_minute'
    time = Column(DateTime, primary_key=True, autoincrement=False)
    log_group_id = Column(DateTime, ForeignKey('log_group.id'), primary_key=True, autoincrement=False)
    filter_id = Column(DateTime, ForeignKey('filters.id'), primary_key=True, autoincrement=False)
    times_seen = Column(Integer, server_default='0')

class Filter(base):
    __tablename__ = 'filters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, server_default='1')
    name = Column(String(45))
    data = Column(Text)

class Filter_version(base):
    __tablename__ = 'filter_versions'
    filter_id = Column(Integer, primary_key=True, autoincrement=False)
    version = Column(Integer, primary_key=True, autoincrement=False)
    data = Column(Text)

class Filter_team(base):
    __tablename__ = 'filter_teams'
    filter_id = Column(Integer, primary_key=True)
    team_id = Column(Integer, primary_key=True)

class Filter_log_group(base):
    __tablename__ = 'filter_log_groups'
    filter_id = Column(Integer, ForeignKey('filters.id'), primary_key=True, autoincrement=False)
    filter_version = Column(Integer, primary_key=True, autoincrement=False)
    log_group_id = Column(Integer, ForeignKey('log_group.id'), primary_key=True, autoincrement=False)
    
class Web_session(base):
    __tablename__ = 'web_sessions'
    session = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', onupdate="cascade", ondelete="cascade"))
    expires = Column(TIMESTAMP)

class Filter_notification_last_sent(base):
    __tablename__ = 'filter_notification_last_sent'
    filter_id = Column(Integer, ForeignKey('filters.id'), primary_key=True)
    last_sent = Column(TIMESTAMP)

class Log_group_notification_last_sent(base):
    __tablename__ = 'log_group_notification_last_sent'
    log_group_id = Column(Integer, ForeignKey('log_group.id'), primary_key=True)
    last_sent = Column(TIMESTAMP)

class Watchdog(base):
    __tablename__ = 'watchdog'
    id = Column(Integer, primary_key=True, autoincrement=True)
    heartbeat = Column(TIMESTAMP)
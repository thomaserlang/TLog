import socket
from tlog.config import Config
from tlog import models
from tlog.decorators import new_session
from datetime import datetime, timedelta

class Watchdog(object):

    @classmethod
    def ping(cls):
        '''
        Sends a "ping" to the TLog server by sending a UDP message.

        The idea is that the UDP message will go through the system like any other log message.
        '''
        sock = socket.socket(
            socket.AF_INET, # Internet
            socket.SOCK_DGRAM, # UDP
        )
        sock.sendto('TLOG_HEARTBEAT', (Config.data['heartbeat']['target_ip'], Config.data['heartbeat']['target_port']))

    @classmethod
    def pong(cls):
        '''
        When receiving a ping, we have to respond with a pong.
        We do this by inserting a heartbeat in the database with a timestamp.

        The ping sender can then check the database for the heartbeat and send an alert if it didn't came through.
        '''
        with new_session() as session:
            heartbeat = models.Watchdog(
                id=1,
                heartbeat=datetime.utcnow(),
            )
            session.merge(heartbeat)
            session.commit()

    @classmethod
    def check(cls, max_minutes):
        '''
        Checks that there has been a heartbeat in the last `max_minutes`.
        Returns true if a heartbeat was found.

        :param max_minutes: int
            The maximum number of minutes since the last heartbeat.
        :returns: boolean
        '''
        with new_session() as session:
            query = session.query(
                models.Watchdog,
            ).filter(
                models.Watchdog.heartbeat >= datetime.utcnow() - timedelta(minutes=max_minutes),
            ).first()
            if not query:
                return False
            return True
import time
import logging
from tlog.base.watchdog import Watchdog
from tlog.config import Config
from tlog.logger import logger
from tlog.mail import Mail
from tlog.pushover import Pushover
from tlog.constants import SYSLOG_SEVERITY

def main():
    logger.set_logger('watchdog.log')
    down = False
    while True:
        try:
            Watchdog.ping()
            logging.info('Ping sent')
            time.sleep(60)
            check = Watchdog.check(
                max_minutes=Config.data['heartbeat']['wait_time'],
            )
            if not check:
                logging.info('No heartbeat was detected.')
                if not down:
                    title = '{}: No heartbeat was detected'.format(SYSLOG_SEVERITY[0])
                    message = 'The patient might be dead. Please check on TLog.'
                    Mail.send(
                        recipients=Config.data['admin_emails'],
                        subject=title,
                        message=message,
                    )
                    for user_key in Config.data['admin_pushover']: 
                        Pushover.send(
                            user_key=user_key,
                            title=title,
                            message=message,
                            severity_level=0,
                        )
            else:
                logging.info('Heartbeat was detected.')
                if down:
                    title = '{}: Heartbeat was detected'.format(SYSLOG_SEVERITY[6])
                    message = 'Good job. TLog is running again.'
                    Mail.send(
                        recipients=Config.data['admin_emails'],
                        subject=title,
                        message=message,
                    )
                    for user_key in Config.data['admin_pushover']:
                        Pushover.send(
                            user_key=user_key,
                            title=title,
                            message=message,
                            severity_level=6,
                        )
            down = not check
        except Exception as e:
            logging.error(u'Watchdog failed with error: {}'.format(send_type, unicode(e)))



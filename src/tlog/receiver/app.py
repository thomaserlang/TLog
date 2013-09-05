import logging
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from tlog.worker import receiver
from tlog.logger import logger
from tlog.config import Config

class Echo(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        logging.info('Received: '+data)
        try:
            if Config.data['celery']['enabled']:
                receiver.receive.delay(data)
            else:
                receiver.receive(data)
        except Exception as e:
            logging.error(unicode(e))            

def main():
    try:
        logger.set_logger('receiver.log')
        reactor.listenUDP(514, Echo())
        reactor.run()
    except Exception as e:
        logging.error(unicode(e))      
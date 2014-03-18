import logging
try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    pass
from twisted.internet.protocol import DatagramProtocol, Protocol, Factory
from twisted.internet import reactor
from tlog.worker import receiver
from tlog.logger import logger
from tlog.config import Config

def message_received(data):
    logging.info('Received: {}'.format(data))
    try:
        if Config.data['celery']['enabled']:
            receiver.receive.delay(data)
        else:
            receiver.receive(data)
    except Exception as e:
        logging.exception('Error doing message storing')  

class UDP_received(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        message_received(data)

class TCP_received(Protocol):

    def dataReceived(self, data):
        message_received(data)

def main():
    try:
        logger.set_logger('receiver.log')
        reactor.listenUDP(Config.data['receiver']['port'], UDP_received())
        factory = Factory()
        factory.protocol = TCP_received
        reactor.listenTCP(Config.data['receiver']['port'], factory)
        reactor.run()
    except Exception as e:
        logging.exception('Exception doing receiver startup.')   
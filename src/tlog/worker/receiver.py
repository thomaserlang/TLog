from app import celery
from tlog.receiver.receiver import Receiver

@celery.task(name='tlog.worker.receiver.receive')
def receive(data):
    '''
    :param data: string
    '''
    Receiver.add(data)
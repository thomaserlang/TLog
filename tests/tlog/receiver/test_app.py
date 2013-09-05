import nose
import unittest2
from tlog.receiver.app import Echo

class test_app(unittest2.TestCase):

    def test_add(self):
        pass
        #server = Echo()

        #result = server.datagramReceived('this is a test', ('127.0.0.1', 5555))
        #self.assertEqual(result, 2)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
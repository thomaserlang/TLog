# coding=UTF-8
import nose
import mock
from tlog.testbase import Testbase
from tlog.base.watchdog import Watchdog

class test_watchdog(Testbase):

    def test(self):
        Watchdog.ping()
        Watchdog.pong()
        self.assertTrue(Watchdog.check(max_minutes=1))

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
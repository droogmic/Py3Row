import unittest
import time
from pyrow.ergmanager import *
from pyrow import simpyrow


class TestErgManager(unittest.TestCase):
    def setUp(self):
        self.erg_count = 0
        self.update_count = 0
        self.update_last = None
        def new_erg_callback(*args):
            self.erg_count += 1
        def update_erg_callback(*args):
            self.update_count += 1
            self.update_last = args
        self.ergman = ErgManager(simpyrow,
                                 add_callback=new_erg_callback,
                                 update_callback=update_erg_callback,
                                 update_rate=0.5)
        time.sleep(0.5)

    def test_got_ergs(self):
        self.assertTrue(self.erg_count>0)

    def test_got_updates(self):
        self.assertTrue(self.update_count>0)

    def tearDown(self):
        self.ergman.stop()

if __name__ == '__main__':
    unittest.main()

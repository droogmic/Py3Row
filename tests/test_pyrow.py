import unittest
from tests.basetest_pyrow import *
from pyrow import pyrow
from usb.core import NoBackendError


class TestFind(unittest.TestCase):
    def test_noerror(self):
        testfind_noerror(self, pyrow)


valid_env = True
try:
    ergs = pyrow.find()
except NoBackendError:
    valid_env = False
valid_env = valid_env and len(list(pyrow.find()))>0
@unittest.skipIf(not valid_env, "Skipping tests, no ergs")
class TestPyErg(unittest.TestCase):
    def setUp(self):
        testpyerg_setUp(self, pyrow)

    def test_get_monitor(self):
        testpyerg_get_monitor(self, pyrow)

    def test_get_forceplot(self):
        testpyerg_get_forceplot(self, pyrow)

    def test_get_workout(self):
        testpyerg_get_workout(self, pyrow)

if __name__ == '__main__':
    unittest.main()

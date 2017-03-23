import unittest
from tests.basetest_pyrow import *
from pyrow import pyrow


class TestFind(unittest.TestCase):
    def test_noerror(self):
        testfind_noerror(self, pyrow)


@unittest.skipIf(len(list(pyrow.find()))==0, "Skipping tests, no ergs")
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

import unittest
from tests.basetest_pyrow import *
from pyrow import simpyrow as pyrow


class TestFind(unittest.TestCase):
    def test_noerror(self):
        testfind_noerror(self, pyrow)


class TestPyRow(unittest.TestCase):
    def setUp(self):
        testpyrow_setUp(self, pyrow)

    def test_get_monitor(self):
        testpyrow_get_monitor(self, pyrow)

    def test_get_forceplot(self):
        testpyrow_get_forceplot(self, pyrow)

    def test_get_workout(self):
        testpyrow_get_workout(self, pyrow)

if __name__ == '__main__':
    unittest.main()

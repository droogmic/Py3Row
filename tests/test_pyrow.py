import unittest

from pyrow import pyrow

class TestFind(unittest.TestCase):
    def test_noerror(self):
        try:
            pyrow.find()
        except Exception as e:
            self.fail("pyrow.find() raised the following exception unexpectedly: {}".format(e))


class TestPyRow(unittest.TestCase):
    def test_noerror(self):
        ergs = list(pyrow.find())
        if len(ergs) == 0:
            self.fail("pyrow.find() returned no ergs")
        print("Connected to erg.")
        try:
            erg = pyrow.PyRow(ergs[0])
        except Exception as e:
            self.fail("pyrow.PyRow() raised the following exception unexpectedly: {}".format(e))


if __name__ == '__main__':
    unittest.main()

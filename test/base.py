import os.path
import unittest

class Test(unittest.TestCase):

    def setUp(self):
        self.testdata_dir = os.path.join(os.path.dirname(__file__), 'testdata')

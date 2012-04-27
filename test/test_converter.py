import os.path

import unittest

from mvc.video import VideoFile
from mvc import converter

testdata_path = os.path.join(os.path.dirname(__file__),
                              'testdata')

class TestConverterManager(unittest.TestCase):

    def setUp(self):
        self.manager = converter.ConverterManager()

    def test_load_converters(self):
        self.manager.load_converters(os.path.join(testdata_path, '*.py'))
        self.assertEqual(len(self.manager.converters), 1)


class TestConverterInfo(unittest.TestCase):

    def setUp(self):
        test_filename = os.path.join(testdata_path, 'converter.py')
        global_dict = {}
        execfile(test_filename, global_dict)
        self.converter_info = global_dict['converters'][0]
        self.video = VideoFile(os.path.join(testdata_path, 'mp4-0.mp4'))

    def test_identifer(self):
        self.assertEqual(self.converter_info.identifier,
                         'testconverter')

    def test_get_output_filename(self):
        self.assertEqual(self.converter_info.get_output_filename(self.video),
                         'mp4-0.testconverter.test')

    def test_get_output_size_guess(self):
        self.assertEqual(self.converter_info.get_output_size_guess(self.video),
                         self.video.duration * self.converter_info.bitrate / 8)


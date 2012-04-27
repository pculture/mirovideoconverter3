import os.path

from mvc.video import VideoFile
from mvc import converter

import base

class TestConverterInfo(converter.ConverterInfo):
    media_type = 'video'
    extension = 'test'
    bitrate = 10000

    def get_executable(self):
        return '/bin/true'

    def get_arguments(self, video, output):
        return [video.filename, output]

    def process_status_line(self, line):
        return {'finished': True}


TEST_CONVERTER = TestConverterInfo('Test Converter')


class ConverterManagerTest(base.Test):

    def setUp(self):
        base.Test.setUp(self)
        self.manager = converter.ConverterManager()

    def test_startup(self):
        self.manager.startup()
        self.assertTrue(self.manager.converters)

    def test_add_converter(self):
        self.manager.add_converter(TEST_CONVERTER)
        self.assertEqual(len(self.manager.converters), 1)

    def test_list_converters(self):
        self.manager.add_converter(TEST_CONVERTER)
        self.assertEqual(list(self.manager.list_converters()),
                         [TEST_CONVERTER])

    def test_get_by_id(self):
        self.manager.add_converter(TEST_CONVERTER)
        self.assertEqual(self.manager.get_by_id('testconverter'),
                         TEST_CONVERTER)
        self.assertRaises(KeyError, self.manager.get_by_id,
                          'doesnotexist')


class ConverterInfoTest(base.Test):

    def setUp(self):
        base.Test.setUp(self)
        self.converter_info = TEST_CONVERTER
        self.video = VideoFile(os.path.join(self.testdata_dir, 'mp4-0.mp4'))

    def test_identifer(self):
        self.assertEqual(self.converter_info.identifier,
                         'testconverter')

    def test_get_output_filename(self):
        self.assertEqual(self.converter_info.get_output_filename(self.video),
                         'mp4-0.testconverter.test')

    def test_get_output_size_guess(self):
        self.assertEqual(self.converter_info.get_output_size_guess(self.video),
                         self.video.duration * self.converter_info.bitrate / 8)


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


class ConverterInfoTestMixin(object):

    def setUp(self):
        self.video = VideoFile(os.path.join(self.testdata_dir, 'mp4-0.mp4'))

    def assertStatusLineOutput(self, line, **output):
        if not output:
            output = None
        self.assertEqual(self.converter_info.process_status_line(self.video,
                                                                 line),
                         output)

    def test_get_executable(self):
        self.assertTrue(self.converter_info.get_executable())

    def test_get_arguments(self):
        output = str(id(self))
        arguments = self.converter_info.get_arguments(self.video, output)

        self.assertTrue(arguments)
        self.assertTrue(self.video.filename in arguments)
        self.assertTrue(output in arguments)


class FFmpegConverterInfoTest(ConverterInfoTestMixin, base.Test):

    def setUp(self):
        base.Test.setUp(self)
        ConverterInfoTestMixin.setUp(self)
        self.converter_info = converter.FFmpegConverterInfo('FFmpeg Test',
                                                            1024, 768)
        self.converter_info.parameters = '{ssize}'

    def test_get_extra_arguments(self):
        output = str(id(self))
        self.assertEqual(
            self.converter_info.get_extra_arguments(self.video, output),
            ['640x480'])

    def test_get_extra_arguments_rescales_size(self):
        self.video.width = 800
        self.video.height = 600
        output = str(id(self))
        self.assertEqual(
            self.converter_info.get_extra_arguments(self.video, output),
            ['800x600'])

    def test_process_status_line_nothing(self):
        self.assertStatusLineOutput(
            '  built on Mar 31 2012 09:58:16 with gcc 4.6.3')


    def test_process_status_line_duration(self):
        self.assertStatusLineOutput(
            '  Duration: 00:00:01.07, start: 0.000000, bitrate: 128 kb/s',
            duration=1.07)

    def test_process_status_line_progress(self):
        self.assertStatusLineOutput(
            'size=    2697kB time=00:02:52.59 bitrate= 128.0kbits/s ',
            progress=172.59)

    def test_process_status_line_progress_with_frame(self):
        self.assertStatusLineOutput(
            'frame=  257 fps= 45 q=27.0 size=    1033kB time=00:00:08.70 '
            'bitrate= 971.4kbits/s ',
            progress=8.7)

    def test_process_status_line_finished(self):
        self.assertStatusLineOutput(
            'frame=16238 fps= 37 q=-1.0 Lsize=  110266kB time=00:11:16.50 '
            'bitrate=1335.3kbits/s dup=16 drop=0',
            finished=True)

    def test_process_status_line_error(self):
        line = ('Error while opening encoder for output stream #0:1 - '
                'maybe incorrect parameters such as bit_rate, rate, width or '
                'height')
        self.assertStatusLineOutput(line,
                                    finished=True,
                                    error=line)

    def test_process_status_line_unknown(self):
        # XXX haven't actually seen this line
        line = 'Unknown error'
        self.assertStatusLineOutput(line,
                                    finished=True,
                                    error=line)

    def test_process_status_line_error_decoding(self):
        # XXX haven't actually seen this line
        line = 'Error while decoding stream: something'
        self.assertStatusLineOutput(line)

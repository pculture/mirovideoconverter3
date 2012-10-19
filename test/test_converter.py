import argparse
import os.path

from mvc.video import VideoFile
from mvc import converter
from mvc import settings

import base
import mock

def make_ffmpeg_arg_parser():
    """Make an args.ArgumentParser for ffmpeg args that we use
    """
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    # command line options that require an argument after
    arguments = [
        "-ab",
        "-ac",
        "-acodec",
        "-aq",
        "-ar",
        "-b",
        "-b:v",
        "-bufsize",
        "-crf",
        "-cpu-used",
        "-deadline",
        "-f",
        '-g',
        "-i",
        "-lag-in-frames",
        "-level",
        "-maxrate",
        "-preset",
        "-profile:v",
        "-r",
        "-s",
        "-slices",
        "-strict",
        "-threads",
        "-qmin",
        "-qmax",
        "-vb",
        "-vcodec",
        "-vprofile",
    ]
    # arguments that set flags
    flags = [
        '-vn',
    ]
    for name in arguments:
        parser.add_argument(name)
    for name in flags:
        parser.add_argument(name, action='store_const', const=True)

    parser.add_argument("output_file")
    return parser

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

    def run_get_target_size(self, (src_width, src_height),
                            (dest_width, dest_height),
                            dont_upsize=True):
        """Create a converter run get_target_size() on a video.
        """
        mock_video = mock.Mock(width=src_width, height=src_height)
        converter_info = converter.FFmpegConverterInfo(
            'FFmpeg Test', dest_width, dest_height)
        converter_info.dont_upsize = dont_upsize
        return converter_info.get_target_size(mock_video)

    def test_get_target_size(self):
        self.assertEqual(self.run_get_target_size((1024, 768), (640, 480)),
                         (640, 480))

    def test_get_target_size_rescale(self):
        # Test get_target_size() rescaling an image.  It should ensure that
        # both dimensions fit inside the target image, and that the aspect
        # ratio is unchanged.
        self.assertEqual(self.run_get_target_size((1024, 768), (800, 500)),
                         (666, 500))

    def test_get_target_size_dont_upsize(self):
        # Test that get_target_size only upsizes when dont_upsize is True
        self.assertEqual(self.run_get_target_size((640, 480), (800, 600)),
                         (640, 480))
        self.assertEqual(self.run_get_target_size((640, 480), (800, 600),
                                                  dont_upsize=False),
                         (800, 600))

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

class TestConverterDefinitions(base.Test):
    def setUp(self):
        base.Test.setUp(self)
        self.manager = converter.ConverterManager()
        self.manager.startup()

    def get_converter_arguments(self, converter_obj):
        """Given a converter, get the arguments to that converter

        :returns: dict of arguments that were set
        """

        output_path = '#output_path#'
        video_file = mock.Mock()
        # Note: we purposely use weird width/height values here to ensure that
        # they are different from the default size
        video_file.width = 542
        video_file.height = 320
        video_file.filename = '#input_path#'
        video_file.container = '#container_name#'

        cmdline_args = converter_obj.get_arguments(video_file, output_path)
        return vars(make_ffmpeg_arg_parser().parse_args(cmdline_args))



        parser = make_ffmpeg_arg_parser()
        args = vars(parser.parse_args(cmdline_args))
        return dict((k, args[k]) for k in args
                    if args[k] != parser.get_default(k))

    def check_ffmpeg_arguments(self, converter_id, correct_arguments):
        """Check the arguments of a ffmpeg-based converter."""
        converter = self.manager.converters[converter_id]
        self.assertEquals(converter.get_executable(),
                          settings.get_ffmpeg_executable_path())

        self.assertEquals(self.get_converter_arguments(converter),
                          correct_arguments)

    def check_size(self, converter_id, width, height):
        converter = self.manager.converters[converter_id]
        self.assertEquals(converter.width, width)
        self.assertEquals(converter.height, height)
        self.assertEquals(converter.dont_upsize, True)
        self.assertEquals(converter.audio_only, False)

    def check_uses_input_size(self, converter_id):
        converter = self.manager.converters[converter_id]
        self.assertEquals(converter.width, None)
        self.assertEquals(converter.height, None)
        self.assertEquals(converter.dont_upsize, True)
        self.assertEquals(converter.audio_only, False)

    def check_audio_only(self, converter_id):
        converter = self.manager.converters[converter_id]
        self.assertEquals(converter.audio_only, True)

    def test_all_converters_checked(self):
        for converter_id in self.manager.converters.keys():
            if not hasattr(self, "test_%s" % converter_id):
                raise AssertionError("No test for converter: %s" %
                                     converter_id)

    def test_droid(self):
        self.check_ffmpeg_arguments('droid', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('droid', 854, 480)

    def test_proresingest720p(self):
        self.check_ffmpeg_arguments('proresingest720p', {
            'acodec': 'pcm_s16be',
            'ar': '48000',
            'f': 'mov',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'profile:v': '2',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'prores',
        })
        self.check_uses_input_size('proresingest720p')

    def test_droidx2(self):
        self.check_ffmpeg_arguments('droidx2', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('droidx2', 1280, 720)

    def test_sensation(self):
        self.check_ffmpeg_arguments('sensation', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('sensation', 960, 540)

    def test_avcintra1080p(self):
        self.check_ffmpeg_arguments('avcintra1080p', {
            'acodec': 'pcm_s16be',
            'ar': '48000',
            'f': 'mov',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'profile:v': '2',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'prores',
        })
        self.check_uses_input_size('avcintra1080p')

    def test_mp4(self):
        self.check_ffmpeg_arguments('mp4', {
            'ab': '96k',
            'acodec': 'aac',
            'crf': '22',
            'f': 'mp4',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'preset': 'slow',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'libx264',
        })
        self.check_uses_input_size('mp4')

    def test_ipodtouch4(self):
        self.check_ffmpeg_arguments('ipodtouch4', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('ipodtouch4', 960, 640)

    def test_mp3(self):
        self.check_ffmpeg_arguments('mp3', {
            'ac': '2',
            'f': 'mp3',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'strict': 'experimental',
        })
        self.check_audio_only('mp3')

    def test_proresingest1080p(self):
        self.check_ffmpeg_arguments('proresingest1080p', {
            'acodec': 'pcm_s16be',
            'ar': '48000',
            'f': 'mov',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'profile:v': '2',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'prores',
        })
        self.check_uses_input_size('proresingest1080p')

    def test_galaxyinfuse(self):
        self.check_ffmpeg_arguments('galaxyinfuse', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxyinfuse', 1280, 800)

    def test_ipodnanoclassic(self):
        self.check_ffmpeg_arguments('ipodnanoclassic', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('ipodnanoclassic', 480, 320)

    def test_oggvorbis(self):
        self.check_ffmpeg_arguments('oggvorbis', {
            'acodec': 'libvorbis',
            'aq': '60',
            'f': 'ogg',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'strict': 'experimental',
            'vn': True,
        })
        self.check_audio_only('oggvorbis')

    def test_wildfire(self):
        self.check_ffmpeg_arguments('wildfire', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '320x188',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('wildfire', 320, 240)

    def test_ipad(self):
        self.check_ffmpeg_arguments('ipad', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('ipad', 1024, 768)

    def test_galaxyadmire(self):
        self.check_ffmpeg_arguments('galaxyadmire', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxyadmire', 480, 320)

    def test_droidincredible(self):
        self.check_ffmpeg_arguments('droidincredible', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('droidincredible', 800, 480)

    def test_sameformat(self):
        self.check_ffmpeg_arguments('sameformat', {
            'acodec': 'copy',
            'i': '#input_path#',
            'output_file': '#output_path#',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'copy',
        })
        self.check_uses_input_size('sameformat')

    def test_zio(self):
        self.check_ffmpeg_arguments('zio', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('zio', 800, 480)

    def test_galaxycharge(self):
        self.check_ffmpeg_arguments('galaxycharge', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxycharge', 800, 480)

    def test_large1080p(self):
        self.check_ffmpeg_arguments('large1080p', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('large1080p', 1920, 1080)

    def test_appletv(self):
        self.check_ffmpeg_arguments('appletv', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('appletv', 1280, 720)

    def test_playstationportable(self):
        self.check_ffmpeg_arguments('playstationportable', {
            'ab': '64000',
            'ar': '24000',
            'b': '512000',
            'f': 'psp',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'r': '29.97',
            's': '542x320',
            'strict': 'experimental',
        })
        self.check_uses_input_size('playstationportable')

    def test_rezound(self):
        self.check_ffmpeg_arguments('rezound', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('rezound', 1280, 720)

    def test_large720p(self):
        self.check_ffmpeg_arguments('large720p', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('large720p', 1280, 720)

    def test_iphone(self):
        self.check_ffmpeg_arguments('iphone', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('iphone', 640, 480)

    def test_galaxyy(self):
        self.check_ffmpeg_arguments('galaxyy', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '320x188',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxyy', 320, 240)

    def test_webmhd(self):
        self.check_ffmpeg_arguments('webmhd', {
            'ab': '112k',
            'acodec': 'libvorbis',
            'ar': '44100',
            'b:v': '2M',
            'cpu_used': '0',
            'deadline': 'good',
            'f': 'webm',
            'g': '120',
            'i': '#input_path#',
            'lag_in_frames': '16',
            'output_file': '#output_path#',
            'qmax': '51',
            'qmin': '11',
            's': '542x320',
            'slices': '4',
            'strict': 'experimental',
            'vcodec': 'libvpx',
            'vprofile': '0',
        })
        self.check_uses_input_size('webmhd')

    def test_galaxytab101(self):
        self.check_ffmpeg_arguments('galaxytab101', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxytab101', 1280, 800)

    def test_galaxynexus(self):
        self.check_ffmpeg_arguments('galaxynexus', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxynexus', 1280, 720)

    def test_galaxysiii(self):
        self.check_ffmpeg_arguments('galaxysiii', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxysiii', 1280, 720)

    def test_desire(self):
        self.check_ffmpeg_arguments('desire', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('desire', 800, 480)

    def test_galaxynoteii(self):
        self.check_ffmpeg_arguments('galaxynoteii', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxynoteii', 1920, 1080)

    def test_thunderbolt(self):
        self.check_ffmpeg_arguments('thunderbolt', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('thunderbolt', 800, 480)

    def test_xoom(self):
        self.check_ffmpeg_arguments('xoom', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('xoom', 1280, 800)

    def test_normal800x480(self):
        self.check_ffmpeg_arguments('normal800x480', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('normal800x480', 800, 480)

    def test_galaxyepic(self):
        self.check_ffmpeg_arguments('galaxyepic', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxyepic', 800, 480)

    def test_avcintra720p(self):
        self.check_ffmpeg_arguments('avcintra720p', {
            'acodec': 'pcm_s16be',
            'ar': '48000',
            'f': 'mov',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'profile:v': '2',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'prores',
        })
        self.check_uses_input_size('avcintra720p')

    def test_dnxhd720p(self):
        self.check_ffmpeg_arguments('dnxhd720p', {
            'acodec': 'pcm_s16be',
            'ar': '48000',
            'b:v': '175M',
            'f': 'mov',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'r': '23.976',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'dnxhd',
        })
        self.check_uses_input_size('dnxhd720p')

    def test_iphone5(self):
        self.check_ffmpeg_arguments('iphone5', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('iphone5', 1920, 1080)

    def test_webmsd(self):
        self.check_ffmpeg_arguments('webmsd', {
            'ab': '112k',
            'acodec': 'libvorbis',
            'ar': '44100',
            'b:v': '768k',
            'cpu_used': '0',
            'deadline': 'good',
            'f': 'webm',
            'g': '120',
            'i': '#input_path#',
            'lag_in_frames': '16',
            'output_file': '#output_path#',
            'qmax': '53',
            'qmin': '0',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'libvpx',
            'vprofile': '0',
        })
        self.check_uses_input_size('webmsd')

    def test_galaxymini(self):
        self.check_ffmpeg_arguments('galaxymini', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '320x188',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxymini', 320, 240)

    def test_onex(self):
        self.check_ffmpeg_arguments('onex', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('onex', 1280, 720)

    def test_oggtheora(self):
        self.check_ffmpeg_arguments('oggtheora', {
            'acodec': 'libvorbis',
            'aq': '60',
            'f': 'ogg',
            'i': '#input_path#',
            'output_file': '#output_path#',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'libtheora',
        })
        self.check_uses_input_size('oggtheora')

    def test_ipad3(self):
        self.check_ffmpeg_arguments('ipad3', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('ipad3', 1920, 1080)

    def test_galaxyssiisplus(self):
        self.check_ffmpeg_arguments('galaxyssiisplus', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxyssiisplus', 800, 480)

    def test_kindlefire(self):
        self.check_ffmpeg_arguments('kindlefire', {
            'ab': '96k',
            'acodec': 'aac',
            'crf': '22',
            'f': 'mp4',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'preset': 'slow',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'libx264',
        })
        self.check_uses_input_size('kindlefire')

    def test_galaxyace(self):
        self.check_ffmpeg_arguments('galaxyace', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxyace', 480, 320)

    def test_dnxhd1080p(self):
        self.check_ffmpeg_arguments('dnxhd1080p', {
            'acodec': 'pcm_s16be',
            'ar': '48000',
            'b:v': '175M',
            'f': 'mov',
            'i': '#input_path#',
            'output_file': '#output_path#',
            'r': '23.976',
            's': '542x320',
            'strict': 'experimental',
            'vcodec': 'dnxhd',
        })
        self.check_uses_input_size('dnxhd1080p')

    def test_small480x320(self):
        self.check_ffmpeg_arguments('small480x320', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('small480x320', 480, 320)

    def test_iphone4(self):
        self.check_ffmpeg_arguments('iphone4', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('iphone4', 960, 640)

    def test_razr(self):
        self.check_ffmpeg_arguments('razr', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('razr', 960, 540)

    def test_ipodtouch(self):
        self.check_ffmpeg_arguments('ipodtouch', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('ipodtouch', 640, 480)

    def test_galaxytab(self):
        self.check_ffmpeg_arguments('galaxytab', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('galaxytab', 1024, 600)

    def test_appleuniversal(self):
        self.check_ffmpeg_arguments('appleuniversal', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vb': '1200k',
            'vcodec': 'libx264',
        })
        self.check_size('appleuniversal', 1280, 720)

    def test_evo4g(self):
        self.check_ffmpeg_arguments('evo4g', {
            'ab': '160k',
            'ac': '2',
            'acodec': 'aac',
            'bufsize': '10000000',
            'f': 'mp4',
            'i': '#input_path#',
            'level': '30',
            'maxrate': '10000000',
            'output_file': '#output_path#',
            'preset': 'slow',
            'profile:v': 'baseline',
            's': '542x320',
            'strict': 'experimental',
            'threads': '0',
            'vcodec': 'libx264',
        })
        self.check_size('evo4g', 800, 480)

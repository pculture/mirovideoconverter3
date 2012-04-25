import os, os.path
import unittest

from mvc import video

class TestGetMediaInfo(unittest.TestCase):

    def runTest(self):
        testdata_dir = os.path.join(os.path.dirname(__file__), 'testdata')
        for name in os.listdir(testdata_dir):
            verify_name = os.path.splitext(name)[0].replace('-', '_')
            try:
                func = getattr(self, 'verify_%s' % verify_name)
            except AttributeError:
                raise AssertionError(
                    "could not find verification function for %r" % (
                        verify_name,))
            full_path = os.path.join(testdata_dir, name)
            output = video.get_media_info(full_path)
            func(output)


    def verify_mp3_0(self, output):
        self.assertEqual(output,
                         {'container': 'mp3',
                          'audio_codec': 'mp3'})

    def verify_mp3_1(self, output):
        self.assertEqual(output,
                         {'container': 'mp3',
                          'audio_codec': 'mp3'})

    def verify_mp3_2(self, output):
        self.assertEqual(output,
                         {'container': 'mp3',
                          'audio_codec': 'mp3'})

    def verify_theora_with_ogg_extension(self, output):
        self.assertEqual(output,
                         {'container': 'ogg',
                          'video_codec': 'theora',
                          'width': 320,
                          'height': 240})

    def verify_webm_0(self, output):
        self.assertEqual(output,
                         {'container': ['matroska', 'webm'],
                          'video_codec': 'vp8',
                          'width': 1920,
                          'height': 912})

    def verify_mp4_0(self, output):
        self.assertEqual(output,
                         {'container': ['mov',
                                        'mp4',
                                        'm4a',
                                        '3gp',
                                        '3g2',
                                        'mj2',
                                        'isom',
                                        'mp41'],
                          'video_codec': 'h264',
                          'audio_codec': 'aac',
                          'width': 640,
                          'height': 480})

    def verify_nuls(self, output):
        self.assertEqual(output,
                         {'container': 'mp3'})


    def verify_drm(self, output):
        self.assertEqual(output,
                         {'container': ['mov',
                                        'mp4',
                                        'm4a',
                                        '3gp',
                                        '3g2',
                                        'mj2',
                                        'M4V',
                                        'M4V ',
                                        'mp42',
                                        'isom'],
                          'video_codec': 'none',
                          'audio_codec': 'aac',
                          'has_drm': ['audio', 'video'],
                          'width': 640,
                          'height': 480})



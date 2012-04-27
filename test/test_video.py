import os, os.path
import unittest

from mvc import video

class TestGetMediaInfo(unittest.TestCase):

    def setUp(self):
        self.testdata_dir = os.path.join(os.path.dirname(__file__), 'testdata')

    def assertEqualOutput(self, filename, expected):
        full_path = os.path.join(self.testdata_dir, filename)
        output = video.get_media_info(full_path)
        self.assertEqual(output, expected)

    def test_mp3_0(self):
        self.assertEqualOutput('mp3-0.mp3',
                               {'container': 'mp3',
                                'audio_codec': 'mp3',
                                'title': 'Invisible Walls',
                                'artist': 'Revolution Void',
                                'album': 'Increase The Dosage',
                                'track': '1',
                                'genre': 'Blues',
                                'duration': 1.07})

    def test_mp3_1(self):
        self.assertEqualOutput('mp3-1.mp3',
                               {'container': 'mp3',
                                'audio_codec': 'mp3',
                                'title': 'Race Lieu',
                                'artist': 'Ckz',
                                'album': 'The Heart EP',
                                'track': '2/5',
                                'duration': 1.07})

    def test_mp3_2(self):
        self.assertEqualOutput('mp3-2.mp3',
                               {'container': 'mp3',
                                'audio_codec': 'mp3',
                                'artist': 'This American Life',
                                'genre': 'Podcast',
                                'title': '#426: Tough Room 2011',
                                'duration': 1.09})

    def test_theora_with_ogg_extension(self):
        self.assertEqualOutput('theora_with_ogg_extension.ogg',
                               {'container': 'ogg',
                                'video_codec': 'theora',
                                'width': 320,
                                'height': 240,
                                'duration': 0.1})

    def test_webm_0(self):
        self.assertEqualOutput('webm-0.webm',
                               {'container': ['matroska', 'webm'],
                                'video_codec': 'vp8',
                                'width': 1920,
                                'height': 912,
                                'duration': 0.43})

    def test_mp4_0(self):
        self.assertEqualOutput('mp4-0.mp4',
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
                                'height': 480,
                                'title': 'Africa: Cash for Climate Change?',
                                'duration': 312.37})

    def test_nuls(self):
        self.assertEqualOutput('nuls.mp3',
                               {'container': 'mp3',
                                'title': 'Invisible'})


    def test_drm(self):
        self.assertEqualOutput('drm.m4v',
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
                                'height': 480,
                                'title': 'Thinkers',
                                'artist': 'The Most Extreme',
                                'album': 'The Most Extreme',
                                'track': '10',
                                'genre': 'Nonfiction',
                                'duration': 2668.8})



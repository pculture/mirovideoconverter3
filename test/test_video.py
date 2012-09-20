import os, os.path
import tempfile
import threading
import unittest

from mvc import video

import base

class GetMediaInfoTest(base.Test):

    def assertClose(self, output, expected):
        diff = output - expected
        self.assertTrue(diff ** 2 < 0.04, # abs(diff) < 0.2
                        "%s != %s" % (output, expected))

    def assertEqualOutput(self, filename, expected):
        full_path = os.path.join(self.testdata_dir, filename)
        try:
            output = video.get_media_info(full_path)
        except Exception, e:
            raise AssertionError(
                'Error parsing %r\nException: %r\nOutput: %s' % (
                    filename, e, video.get_ffmpeg_output(full_path)))
        duration_output = output.pop('duration', None)
        duration_expected = expected.pop('duration', None)
        if duration_output is not None and duration_expected is not None:
            self.assertClose(duration_output, duration_expected)
        else:
            # put them back in, let assertEqual handle the difference
            output['duration'] = duration_output
            expected['duration'] = duration_expected
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

    def test_theora(self):
        self.assertEqualOutput('theora.ogv',
                               {'container': 'ogg',
                                'video_codec': 'theora',
                                'audio_codec': 'vorbis',
                                'width': 400,
                                'height': 304,
                                'duration': 5.0})

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

    @unittest.skip('inconsistent parsing of DRMed files')
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



class GetThumbnailTest(base.Test):

    def setUp(self):
        base.Test.setUp(self)
        self.video_path = os.path.join(self.testdata_dir,
                                       'theora.ogv')
        self.temp_path = tempfile.NamedTemporaryFile(
            suffix='.png')

    def generate_thumbnail(self, width, height):
        ev = threading.Event()

        def completion(path):
            ev.set()
            self.assertEqual(path, self.temp_path.name)

        video.get_thumbnail(self.video_path, width, height,
                            self.temp_path.name, completion,
                            skip=0)
        ev.wait(10)
        if not ev.is_set():
            self.assertTrue(None, 'timed out generating thumbnail image')

        thumbnail = video.VideoFile(self.temp_path.name)
        return thumbnail

    def test_original_size(self):
        thumbnail = self.generate_thumbnail(-1, -1)
        self.assertEqual(thumbnail.width, 400)
        self.assertEqual(thumbnail.height, 304)

    def test_height_resize(self):
        thumbnail = self.generate_thumbnail(200, -1)
        self.assertEqual(thumbnail.width, 200)
        self.assertEqual(thumbnail.height, 152)

    def test_width_resize(self):
        thumbnail = self.generate_thumbnail(-1, 152)
        self.assertEqual(thumbnail.width, 200)
        self.assertEqual(thumbnail.height, 152)

    def test_both_resize(self):
        thumbnail = self.generate_thumbnail(100, 100)
        self.assertEqual(thumbnail.width, 100)
        self.assertEqual(thumbnail.height, 100)

class VideoFileTest(base.Test):

    def setUp(self):
        base.Test.setUp(self)
        self.video_path = os.path.join(self.testdata_dir,
                                       'theora.ogv')
        self.video = video.VideoFile(self.video_path)
        self.video.thumbnails = {}

    def get_thumbnail_from_video(self, **kwargs):
        ev = threading.Event()

        def completion():
            ev.set()

        path = self.video.get_thumbnail(completion, **kwargs)
        if not path:
            ev.wait(10)
            if not ev.is_set():
                self.assertTrue(None, 'timed out generating thumbnail')
            path = self.video.get_thumbnail(completion, **kwargs)
        self.assertNotEqual(path, None, 'thumbnail not created')
        return video.VideoFile(path)

    def test_get_thumbnail_original_size(self):
        thumbnail = self.get_thumbnail_from_video()
        self.assertEqual(thumbnail.width, 400)
        self.assertEqual(thumbnail.height, 304)

    def test_get_thumbnail_scaled_width(self):
        thumbnail = self.get_thumbnail_from_video(width=200)
        self.assertEqual(thumbnail.width, 200)
        self.assertEqual(thumbnail.height, 152)

    def test_get_thumbnail_scaled_height(self):
        thumbnail = self.get_thumbnail_from_video(height=152)
        self.assertEqual(thumbnail.width, 200)
        self.assertEqual(thumbnail.height, 152)

    def test_get_thumbnail_scaled_both(self):
        thumbnail = self.get_thumbnail_from_video(width=100, height=100)
        self.assertEqual(thumbnail.width, 100)
        self.assertEqual(thumbnail.height, 100)

    def test_get_thumbnail_cache(self):
        thumbnail = self.get_thumbnail_from_video()
        thumbnail2 = self.get_thumbnail_from_video()
        self.assertEqual(thumbnail.filename,
                         thumbnail2.filename)

    def test_get_thumbnail_audio(self):
        audio_path = os.path.join(self.testdata_dir, 'mp3-0.mp3')
        audio = video.VideoFile(audio_path)
        def complete():
            pass
        self.assertEqual(audio.get_thumbnail(complete), None)
        self.assertEqual(audio.get_thumbnail(complete, 90, 70), None)

# Default Device Conversion Parameters
import os

class TestData(object):
    _UNITTESTFILES = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","..",'testdata'))
    _SIKTESTFILES = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'testdata'))

    _FILES = {
                'mp3-0.mp3':   {
                                'testdir': _UNITTESTFILES,
                                'container': 'mp3',
                                'audio_codec': 'mp3',
                                'title': 'Invisible Walls',
                                'artist': 'Revolution Void',
                                'album': 'Increase The Dosage',
                                'track': '1',
                                'genre': 'Blues',
                                'duration': 1.07
                               },
               'mp3-1.mp3':
                              {
                                'testdir': _UNITTESTFILES,
                                'container': 'mp3',
                                'audio_codec': 'mp3',
                                'title': 'Race Lieu',
                                'artist': 'Ckz',
                                'album': 'The Heart EP',
                                'track': '2/5',
                                'duration': 1.07
                              },

               'mp3-2.mp3':
                               {
                                'testdir': _UNITTESTFILES,
                                'container': 'mp3',
                                'audio_codec': 'mp3',
                                'artist': 'This American Life',
                                'genre': 'Podcast',
                                'title': '#426: Tough Room 2011',
                                'duration': 1.09
                               },

               'theora_with_ogg_extension.ogg':
                               {
                                'testdir': _UNITTESTFILES,
                                'container': 'ogg',
                                'video_codec': 'theora',
                                'width': 320,
                                'height': 240,
                                'duration': 0.1},

               'webm-0.webm':
                               {'testdir': _UNITTESTFILES,
                                'container': ['matroska', 'webm'],
                                'video_codec': 'vp8',
                                'width': 1920,
                                'height': 912,
                                'duration': 0.43},

               'mp4-0.mp4':
                               {'testdir': _UNITTESTFILES,
                                'container': ['mov',
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
                                'duration': 312.37},


               'nuls.mp3':
                               {
                                'testdir': _UNITTESTFILES,
                                'container': 'mp3',
                                'title': 'Invisible'},

               'drm.m4v':
                               {
                                'testdir': _UNITTESTFILES,
                                'container': ['mov',
                                              'mp4',
                                              'm4a',
                                              '3gp',
                                              '3g2',
                                              'mj2',
                                              'M4V',
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
                                'duration': 2668.8},

                'baby_block.m4v': 
                               {
                                'testdir': _SIKTESTFILES,
                                'container': 'm4v',
                                'video_codec': 'h264',
                                'audio_codec': 'aac',
                                'width': 960,
                                'height': 540,
                               },
                'fake_video.mp4': # this is a fake mp4 file it is a pdf file renamed to an mp4 extension and should fail conversion
                               {
                                'testdir': _SIKTESTFILES,
                                'container': 'mp4',
                                'video_codec': None,
                                'audio_codec': None,
                                'width': None,
                                'height': None,
                               },
                'story_stuff.mov': 
                               {'testdir': _SIKTESTFILES,
                                'container': 'mov',
                                'video_codec': 'h264',
                                'audio_codec': 'mp3',
                                'width': 320,
                                'height': 180,
                               }

                 }

    def testfile_attr(self, testfile, default):
        try:
            return self._FILES[testfile][default]
        except:
            return None

    def directory_list(self, testdir):
        files_list = []
        for k, v in self._FILES.iteritems():
            if v.has_key('testdir') and testdir in v['testdir']:
                files_list.append(k)
        return files_list

    def test_data(self, many=True, new=False):
        """Grab a subset of the test files.
   
        Default selection is to use the unittest files, 
        but, if I need extra files, getting them from the sikuli test files dir.
        """
        DEFAULT_UNITTESTFILES = ['mp4-0.mp4', 'webm-0.webm']
        DEFAULT_SIKTESTFILES = ['baby_block.m4v', 'story_styff.mov']
        if new:
            TESTFILES = DEFAULT_SIKTESTFILES
        else:
            TESTFILES = DEFAULT_UNITTESTFILES

        DATADIR = self.testfile_attr(TESTFILES[0], 'testdir')

        if not many:
            TESTFILES = TESTFILES[:1]

        print TESTFILES
        return DATADIR, TESTFILES


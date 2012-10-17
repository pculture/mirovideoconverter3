import logging
import re

from mvc.converter import FFmpegConverterInfoBase
from mvc.utils import rescale_video

class SimpleFFmpegConverterInfo(FFmpegConverterInfoBase):
    def get_extra_arguments(self, video, output):
        return list(self.parameters)

class SimpleFFmpegConverterInfoWithSize(SimpleFFmpegConverterInfo):
    def __init__(self, name, width=None, height=None, dont_upsize=True):
        try:
            self.width, self.height = self.parse_size_parameter()
        except StandardError, e:
            logging.warn("%s: %s parsing size parameter (%s)",
                         self, e, self.parameters)
	    self.width = self.height = None
        self.dont_upsize = dont_upsize
        super(SimpleFFmpegConverterInfoWithSize, self).__init__(name)

    def parse_size_parameter(self):
        try:
            size_index = self.parameters.index('-s')
        except ValueError:
            # This converter doesn't have a preset size.  It will use the
            # input size
            return (None, None)
        size_param = self.parameters[size_index+1]
        # try matching against predefined size strings
        known_sizes = {
            'hd1080': (1920, 1080),
            'hd720': (1080, 720),
            'hd480': (720, 480),
        }
        if size_param in known_sizes:
            return known_sizes[size_param]
        # use a regex to match <width>x<height>
        generic_match = re.match(r'(\d+)x(\d+)$', size_param)
        if generic_match is not None:
            return int(generic_match.group(1)), int(generic_match.group(2))
        # no match
        logging.warn("%s: Unknown size parameter: %s", self,
                     size_param)
        return None, None

    def get_extra_arguments(self, video, output):
        arguments = super(SimpleFFmpegConverterInfoWithSize,
                          self).get_extra_arguments(video, output)
        if self.width and self.height:
            width, height = self.get_target_size(video)
            arguments.extend(('-s', '%ix%i' % (width, height)))
        return arguments

class WebM_HD(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'webm'
    parameters = ('-f webm -s hd720 -vcodec libvpx -g 120 -lag-in-frames 16 '
                  '-deadline good -cpu-used 0 -vprofile 0 -qmax 51 -qmin 11 '
                  '-slices 4 -b:v 2M -acodec libvorbis -ab 112k '
                  '-ar 44100').split()

class WebM_SD(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'webm'
    parameters = ('-f webm -s hd480 -vcodec libvpx -g 120 -lag-in-frames 16 '
                  '-deadline good -cpu-used 0 -vprofile 0 -qmax 53 -qmin 0 '
                  '-b:v 768k -acodec libvorbis -ab 112k '
                  '-ar 44100').split()

class MP4(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mp4'
    parameters = ('-acodec aac -ab 96k -vcodec libx264 -preset slow '
                  '-f mp4 -crf 22').split()

class MP3(SimpleFFmpegConverterInfo):
    media_type = 'format'
    extension = 'mp3'
    parameters = '-f mp3 -ac 2'.split()

class OggVorbis(SimpleFFmpegConverterInfo):
    media_type = 'format'
    extension = 'ogg'
    parameters = '-f ogg -vn -acodec libvorbis -aq 60'.split()

class OggTheora(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'ogv'
    parameters = '-f ogg -vcodec libtheora -acodec libvorbis -aq 60'.split()

class DNxHD_1080(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-r 23.976 -f mov -s hd1080 -vcodec dnxhd -b:v '
                  '175M -acodec pcm_s16be -ar 48000').split()

class DNxHD_720(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-r 23.976 -f mov -s hd720 -vcodec dnxhd -b:v '
                  '175M -acodec pcm_s16be -ar 48000').split()

class PRORES_720(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-s hd720 -f mov -vcodec prores -profile 2 '
                  '-acodec pcm_s16be -ar 48000').split()

class PRORES_1080(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-s hd1080 -f mov -vcodec prores -profile 2 '
                  '-acodec pcm_s16be -ar 48000').split()

class AVC_INTRA_1080(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-s hd1080 -f mov  -vcodec libx264 -pix_fmt yuv422p '
                  '-crf 0 -intra -b:v 100M -acodec pcm_s16be -ar 48000').split()

class AVC_INTRA_720(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-s hd720 -f mov  -vcodec libx264 -pix_fmt yuv422p '
                  '-crf 0 -intra -b:v 100M -acodec pcm_s16be -ar 48000').split()

class NullConverter(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = None
    parameters = ('-vcodec copy -acodec copy').split()

    def get_extra_arguments(self, video, output):
        args = SimpleFFmpegConverterInfoWithSize.get_extra_arguments(self,
                                                                     video,
                                                                     output)
        # Never None
        container = video.container if video.container else ''
        # XXX: mov,mp4,m4a,3gp,3g2,mj2
        if isinstance(container, list):
            container = 'mp4'
        args.extend(('-f', container))
        return args

mp3 = MP3('MP3')
ogg_vorbis = OggVorbis('Ogg Vorbis')

audio_formats = ('Audio', [mp3, ogg_vorbis])

webm_hd = WebM_HD('WebM HD')
webm_sd = WebM_SD('WebM SD')
mp4 = MP4('MP4')
theora = OggTheora('Ogg Theora')

video_formats = ('Video', [webm_hd, webm_sd, mp4, theora])

dnxhd_1080 = DNxHD_1080('DNxHD 1080p')
dnxhd_720 = DNxHD_720('DNxHD 720p')
prores_1080 = PRORES_1080('Prores Ingest 1080p')
prores_720 = PRORES_720('Prores Ingest 720p')
avc_intra_1080 = PRORES_1080('AVC Intra 1080p')
avc_intra_720 = PRORES_720('AVC Intra 720p')

ingest_formats = ('Ingest Formats', [dnxhd_1080, dnxhd_720, prores_1080,
                                     prores_720, avc_intra_1080, avc_intra_720])

null_converter = NullConverter('Same Format')

converters = [video_formats, audio_formats, ingest_formats, null_converter]

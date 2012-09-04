from mvc.converter import FFmpegConverterInfoBase
from mvc.utils import rescale_video

class SimpleFFmpegConverterInfo(FFmpegConverterInfoBase):

    def get_extra_arguments(self, video, output):
        return list(self.parameters)


class SimpleFFmpegConverterInfoWithSize(SimpleFFmpegConverterInfo):

    def __init__(self, name, width=None, height=None, dont_upsize=True):
        self.width, self.height = width, height
        self.dont_upsize = dont_upsize
        super(SimpleFFmpegConverterInfoWithSize, self).__init__(name)

    def get_extra_arguments(self, video, output):
        arguments = super(SimpleFFmpegConverterInfoWithSize,
                          self).get_extra_arguments(video, output)
        if self.width and self.height:
            width, height = rescale_video((video.width, video.height),
                                          (self.width, self.height),
                                          dont_upsize=self.dont_upsize)
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

class OggTheora(SimpleFFmpegConverterInfo):
    media_type = 'format'
    extension = 'ogv'
    parameters = '-f ogg -vcodec libtheora -acodec libvorbis -aq 60'.split()


webm_hd = WebM_HD('WebM HD')
webm_sd = WebM_SD('WebM SD')
mp4 = MP4('MP4')
mp3 = MP3('MP3')
ogg_vorbis = OggVorbis('Ogg Vorbis')
theora = OggTheora('Ogg Theora')

converters = [mp4, mp3, ogg_vorbis, theora, webm_hd, webm_sd]

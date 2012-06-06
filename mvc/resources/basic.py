from mvc.converter import FFmpegConverterInfoBase, FFmpeg2TheoraConverterInfo
from mvc.utils import rescale_video

class SimpleFFmpegConverterInfo(FFmpegConverterInfoBase):

    def get_extra_arguments(self, video, output):
        return list(self.parameters)


class SimpleFFmpegConverterInfoWithSize(SimpleFFmpegConverterInfo):

    def __init__(self, name, width=None, height=None):
        self.width, self.height = width, height
        super(SimpleFFmpegConverterInfoWithSize, self).__init__(name)

    def get_extra_arguments(self, video, output):
        arguments = super(SimpleFFmpegConverterInfoWithSize,
                          self).get_extra_arguments(video, output)
        if self.width and self.height:
            width, height = rescale_video((video.width. video.height),
                                          (self.width, self.height))
            arguments.extend(('-s', '%ix%i' % (self.width, self.height)))
        return arguments


class WebM(SimpleFFmpegConverterInfoWithSize):
    media_type = 'format'
    extension = 'webm'
    parameters = ('-f webm -vcodec libvpx '
                  '-acodec libvorbis -ab 160000 -sameq').split()


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


webm = WebM('WebM (VP8)')
mp4 = MP4('MP4')
mp3 = MP3('MP3')
ogg_vorbis = OggVorbis('Ogg Vorbis')
theora = FFmpeg2TheoraConverterInfo('Ogg Theora')

converters = [mp4, mp3, ogg_vorbis, theora, webm]

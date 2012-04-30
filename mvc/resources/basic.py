from mvc.converter import FFmpegConverterInfoBase, FFmpeg2TheoraConverterInfo


class SimpleFFmpegConverterInfo(FFmpegConverterInfoBase):

    def get_extra_arguments(self, video, output):
        return list(self.parameters)


class WebM(SimpleFFmpegConverterInfo):
    media_type = 'video'
    bitrate = 1200000
    extension = 'webm'
    parameters = ('-f webm -vcodec libvpx '
                  '-acodec libvorbis -ab 160000 -sameq').split()


class MP4(SimpleFFmpegConverterInfo):
    media_type = 'video'
    bitrate = 700000
    extension = 'mp4'
    parameters = ('-acodec aac -ab 96k -vcodec libx264 -preset slow '
                  '-f mp4 -crf 22').split()

    def get_extra_arguments(self, video, output):
        return self.parameters


class MP3(SimpleFFmpegConverterInfo):
    media_type = 'audio'
    bitrate = 160000
    extension = 'mp3'
    parameters = '-f mp3 -ac 2'.split()


class OggVorbis(SimpleFFmpegConverterInfo):
    media_type = 'audio'
    bitrate = 300000
    extension = 'ogg'
    parameters = '-f ogg -vn -acodec libvorbis -aq 60'.split()


webm = WebM('WebM (VP8)')
mp4 = MP4('MP4')
mp3 = MP3('MP3')
ogg_vorbis = OggVorbis('Ogg Vorbis')
theora = FFmpeg2TheoraConverterInfo('Ogg Theora')

converters = [mp4, mp3, ogg_vorbis, theora, webm]

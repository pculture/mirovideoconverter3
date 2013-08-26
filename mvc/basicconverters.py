import logging
import re

from mvc import converter

class WebM_HD(converter.FFmpegConverterInfo720p):
    media_type = 'format'
    extension = 'webm'
    parameters = ('-f webm -vcodec libvpx -g 120 -lag-in-frames 16 '
                  '-deadline good -cpu-used 0 -vprofile 0 -qmax 51 -qmin 11 '
                  '-slices 4 -b:v 2M -acodec libvorbis -ab 112k '
                  '-ar 44100')

class WebM_SD(converter.FFmpegConverterInfo480p):
    media_type = 'format'
    extension = 'webm'
    parameters = ('-f webm -vcodec libvpx -g 120 -lag-in-frames 16 '
                  '-deadline good -cpu-used 0 -vprofile 0 -qmax 53 -qmin 0 '
                  '-b:v 768k -acodec libvorbis -ab 112k '
                  '-ar 44100')

class MP4(converter.FFmpegConverterInfo):
    media_type = 'format'
    extension = 'mp4'
    parameters = ('-acodec aac -ab 96k -vcodec libx264 -preset slow '
                  '-f mp4 -crf 22')

class MP3(converter.FFmpegConverterInfo):
    media_type = 'format'
    extension = 'mp3'
    parameters = '-f mp3 -ac 2'
    audio_only = True

class OggVorbis(converter.FFmpegConverterInfo):
    media_type = 'format'
    extension = 'ogg'
    parameters = '-f ogg -vn -acodec libvorbis -aq 60'
    audio_only = True

class OggTheora(converter.FFmpegConverterInfo):
    media_type = 'format'
    extension = 'ogv'
    parameters = '-f ogg -codec:v libtheora -qscale:v 7 -codec:a libvorbis -qscale:a 5'

class DNxHD_1080(converter.FFmpegConverterInfo1080p):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-r 23.976 -f mov -vcodec dnxhd -b:v '
                  '175M -acodec pcm_s16be -ar 48000')

class DNxHD_720(converter.FFmpegConverterInfo720p):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-r 23.976 -f mov -vcodec dnxhd -b:v '
                  '175M -acodec pcm_s16be -ar 48000')

class PRORES_720(converter.FFmpegConverterInfo720p):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-f mov -vcodec prores -profile 2 '
                  '-acodec pcm_s16be -ar 48000')

class PRORES_1080(converter.FFmpegConverterInfo1080p):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-f mov -vcodec prores -profile 2 '
                  '-acodec pcm_s16be -ar 48000')

class AVC_INTRA_1080(converter.FFmpegConverterInfo1080p):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-f mov  -vcodec libx264 -pix_fmt yuv422p '
                  '-crf 0 -intra -b:v 100M -acodec pcm_s16be -ar 48000')

class AVC_INTRA_720(converter.FFmpegConverterInfo720p):
    media_type = 'format'
    extension = 'mov'
    parameters = ('-f mov  -vcodec libx264 -pix_fmt yuv422p '
                  '-crf 0 -intra -b:v 100M -acodec pcm_s16be -ar 48000')

class NullConverter(converter.FFmpegConverterInfo):
    media_type = 'format'
    extension = None

    def get_parameters(self, video):
        params = []
        if not video.audio_only and self.should_copy_video_size(video):
            # -vcodec copy copies the video data exactly.  Only use it if the
            # output video is the same size as the input video (#19664)
            params.extend(['-vcodec', 'copy'])
        params.extend(['-acodec', 'copy'])
        return params

    def should_copy_video_size(self, video):
        if self.width is None or self.height is None:
            return True
        return (video.width == self.width and video.height == self.height)

    def get_extra_arguments(self, video, output):
        if not video.container:
            logging.warn("sameformat: video.container is None.  Using mp4")
            container = 'mp4'
        elif isinstance(video.container, list):
            # XXX: special case mov,mp4,m4a,3gp,3g2,mj2
            container = 'mp4'
        else:
            container = video.container
        return ['-f', container]

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

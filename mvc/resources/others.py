from mvc.resources.basic import SimpleFFmpegConverterInfo

class PlaystationPortable(SimpleFFmpegConverterInfo):
    media_type = 'video'
    bitrate = 600000
    extension = 'mp4'
    parameters = ('-s 320x240 -b 512000 -ar 24000 -ab 64000 '
                  '-f psp -r 29.97').split()


class KindleFire(SimpleFFmpegConverterInfo):
    media_type = 'video'
    bitrate = 700000
    extension = 'mp4'
    parameters = ('-acodec aac -ab 96k -vcodec libx264 '
                  '-preset slow -f mp4 -crf 22').split()


psp = PlaystationPortable('Playstation Portable (PSP)')
kindle_fire = KindleFire('Kindle Fire')

converters = [psp, kindle_fire]

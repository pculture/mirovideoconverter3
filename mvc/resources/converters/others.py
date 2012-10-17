from mvc.converter import FFmpegConverterInfo

class PlaystationPortable(FFmpegConverterInfo):
    media_type = 'other'
    extension = 'mp4'
    parameters = ('-s 320x240 -b 512000 -ar 24000 -ab 64000 '
                  '-f psp -r 29.97').split()


class KindleFire(FFmpegConverterInfo):
    media_type = 'other'
    extension = 'mp4'
    parameters = ('-acodec aac -ab 96k -vcodec libx264 '
                  '-preset slow -f mp4 -crf 22').split()


psp = PlaystationPortable('Playstation Portable')
kindle_fire = KindleFire('Kindle Fire')

converters = [psp, kindle_fire]

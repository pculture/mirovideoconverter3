from mvc.converter import FFmpegConverterInfo

from mvc.resources.basic import MP4

class AppleConversion(FFmpegConverterInfo):
    media_type = 'apple'
    extension = 'mp4'
    parameters = ('-acodec aac -ac 2 -ab 160k -s {ssize} '
                  '-vcodec libx264 -preset slow -profile:v baseline -level 30 '
                  '-maxrate 10000000 -bufsize 10000000 -vb 1200k -f mp4 '
                  '-threads 0')
    simple = MP4


DEFAULT_SIZE = (480, 320)

iphone = AppleConversion('iPhone', *DEFAULT_SIZE)
ipod_touch = AppleConversion('iPod Touch', *DEFAULT_SIZE)
ipod_nano = AppleConversion('iPod Nano', *DEFAULT_SIZE)
ipod_classic = AppleConversion('iPod Classic', *DEFAULT_SIZE)
ipad_iphone_g4 = AppleConversion('iPad / iPhone G4', 640, 480)
iphone_4 = AppleConversion('iPhone 4 / iPod Touch 4', 640, 480)
ipad = AppleConversion('iPad', 1024, 768)
universal = AppleConversion('Apple Universal', 1280, 720)

converters = [iphone, ipod_touch, ipod_nano, ipod_classic, ipad_iphone_g4,
              iphone_4, ipad, universal]


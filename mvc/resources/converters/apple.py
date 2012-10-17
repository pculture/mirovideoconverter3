from mvc.converter import FFmpegConverterInfo
from mvc.basicconverters import MP4

class AppleConversion(FFmpegConverterInfo):
    media_type = 'apple'
    extension = 'mp4'
    parameters = ('-acodec aac -ac 2 -ab 160k  '
                  '-vcodec libx264 -preset slow -profile:v baseline -level 30 '
                  '-maxrate 10000000 -bufsize 10000000 -vb 1200k -f mp4 '
                  '-threads 0')
    simple = MP4


DEFAULT_SIZE = (480, 320)

ipod = AppleConversion('iPod Nano/Classic', *DEFAULT_SIZE)
ipod_touch = AppleConversion('iPod Touch', 640, 480)
ipod_retina = AppleConversion('iPod Touch 4+', 960, 640)
iphone = AppleConversion('iPhone', 640, 480)
iphone_retina = AppleConversion('iPhone 4+', 960, 640)
iphone_5 = AppleConversion('iPhone 5', 1920, 1080)
ipad = AppleConversion('iPad', 1024, 768)
ipad_retina = AppleConversion('iPad 3', 1920, 1080)
apple_tv = AppleConversion('Apple TV', 1280, 720)
universal = AppleConversion('Apple Universal', 1280, 720)

converters = [ipod, ipod_touch, ipod_retina, iphone, iphone_retina, iphone_5,
	ipad, ipad_retina, apple_tv, universal]

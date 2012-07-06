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

ipod = AppleConversion('iPod Nano/Classic', *DEFAULT_SIZE)
iphone_ipod = AppleConversion('iPhone/iPod Touch', 640, 480)
iphone_ipod_retina = AppleConversion('iPhone/iPod Touch (with retina display)',
                                     960, 640)
ipad = AppleConversion('iPad', 1024, 768)
ipad_retina = AppleConversion('iPad (with retina display)', 1920, 1080)
apple_tv = AppleConversion('Apple TV', 1280, 720)
universal = AppleConversion('Apple Universal', 1280, 720)

converters = [ipod, iphone_ipod, iphone_ipod_retina, ipad,
              ipad_retina, apple_tv, universal]

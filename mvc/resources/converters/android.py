from mvc.converter import FFmpegConverterInfo
from mvc.basicconverters import MP4

class AndroidConversion(FFmpegConverterInfo):
    media_type = 'android'
    extension = 'mp4'
    parameters = ('-acodec aac -ac 2 -ab 160k -s {ssize} '
                  '-vcodec libx264 -preset slow -profile:v baseline -level 30 '
                  '-maxrate 10000000 -bufsize 10000000 -f mp4 -threads 0 ')
    simple = MP4

g2 = AndroidConversion('G2', 800, 480)
nexus_one = AndroidConversion('Nexus One', 800, 400)
dream_g1 = AndroidConversion('Dream / G1', 480, 320)
magic = AndroidConversion('Magic / myTouch', 480, 320)
droid = AndroidConversion('Droid', 854, 480)
eris = AndroidConversion('Eris / Desire', 480, 320)
hero = AndroidConversion('Hero', 480, 320)
cliq = AndroidConversion('Cliq / DEXT', 480, 320)
behold = AndroidConversion('Behold II', 480, 320)
galaxy_tab = AndroidConversion('Galaxy Tab', 1024, 800)
epic = AndroidConversion('Epic', 800, 480)
xoom = AndroidConversion('Xoom', 1280, 800)

converters = [g2, nexus_one, dream_g1, magic, droid, eris, hero, cliq,
              behold, galaxy_tab, epic, xoom]

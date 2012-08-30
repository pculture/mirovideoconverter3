from mvc.converter import FFmpegConverterInfo
from mvc.basicconverters import MP4

class AndroidConversion(FFmpegConverterInfo):
    media_type = 'android'
    extension = 'mp4'
    parameters = ('-acodec aac -ac 2 -ab 160k -s {ssize} '
                  '-vcodec libx264 -preset slow -profile:v baseline -level 30 '
                  '-maxrate 10000000 -bufsize 10000000 -f mp4 -threads 0 ')
    simple = MP4

y = AndroidConversion('Galaxy Y', 320, 240)
mini = AndroidConversion('Galaxy Mini', 320, 240)
ace = AndroidConversion('Galaxy Ace', 480, 320)
admire = AndroidConversion('Galaxy Admire', 480, 320)
charge = AndroidConversion('Galaxy Charge', 800, 480)
s = AndroidConversion('Galaxy S / SII / S Plus', 800, 480)
siii = AndroidConversion('Galaxy S / SII / S Plus', 1280, 720)
nexus = AndroidConversion('Galaxy Nexus', 1280, 720)
tab = AndroidConversion('Galaxy Tab', 1024, 600)
tab_10 = AndroidConversion('Galaxy Tab 10.1', 1280, 800)
note = AndroidConversion('Galaxy Note', 1280, 800)
infuse = AndroidConversion('Galaxy Infuse', 1280, 800)
epic = AndroidConversion('Galaxy Epic', 800, 480)

samsung_devices = ('Samsung', [y, mini, ace, admire, charge, s, siii, nexus,
                               tab, tab_10, note, infuse, epic])

wildfire = AndroidConversion('Wildfire', 320, 240)
desire = AndroidConversion('Desire', 800, 480)
incredible = AndroidConversion('Droid Incredible', 800, 480)
thunderbolt = AndroidConversion('Thunderbolt', 800, 480)
evo = AndroidConversion('Evo 4G', 800, 480)
sensation = AndroidConversion('Sensation', 960, 540)
rezound = AndroidConversion('Rezound', 1280, 720)

htc_devices = ('HTC', [wildfire, desire, incredible, thunderbolt, evo, 
                       sensation, rezound])

droid = AndroidConversion('Droid', 854, 480)
droid_x2 = AndroidConversion('Droid X2', 1280, 720)
razr = AndroidConversion('RAZR', 960, 540)
xoom = AndroidConversion('XOOM', 1280, 800)

motorola_devices = ('Motorola', [droid, droid_x2, razr, xoom])

zio = AndroidConversion('Zio', 800, 480)

sanyo_devices = ('Sanyo', [zio])

small = AndroidConversion('Small screen (320x480)', 480, 320)
normal = AndroidConversion('Normal screen (480x800)', 800, 480)
large720 = AndroidConversion('Large screen (720p)', 1280, 720)
large1080 = AndroidConversion('Large screen (1080p)', 1920, 1080)

more_devices = ('More Devices', [small, normal, large720, large1080])

converters = [samsung_devices, htc_devices, motorola_devices, sanyo_devices,
              more_devices]

# Default Device Conversion Parameters

_DEVICES = {
                      'Xoom':  {
                                'group': 'Android', 
                                'width': '1280',
                                'height': '800',
                               },

                      'Droid': {'group': 'Android',
                                'width': '854',
                                'height': '480',
                               },

                      'G2':    {
                               'group': 'Android',
                               'width': '800',
                               'height': '480',
                               },

                      'Dream': {
                               'group': 'Android',
                               'width': '480',
                               'height': '320',
                                },

                     'Galaxy Tab': { 
                               'group': 'Android',
                               'width': '1024',
                               'height': '800',
                                },

                      'Epic':  {
                                'group': 'Android',
                                'width': '800',
                                'height': '480',
                               },

                      'KindleFire':  {
                                'group': 'Other',
                                'width': '1024',
                                'height': '600',
                                },
                      'Playstation':  {
                                'group': 'Other',
                                'width': '320',
                                'height': '480',
                                },

                      'iPhone':  {
                                'group': 'Apple',
                                'width': '480',
                                'height': '320',
                                },
                      'iPhone 4':  {
                                'group': 'Apple',
                                'width': '640',
                                'height': '480',
                                },
                      'iPad':  {
                                'group': 'Apple',
                                'width': '1024',
                                'height': '768',
                                },
                      'Apple Universal':  {
                                'group': 'Apple',
                                'width': '1280',
                                'height': '720',
                                },
                      'MP4':   {
                                'group': 'Format',
                                'width': None,
                                'height': None,
                                },
                      'MP3':   {
                                'group': 'Format',
                                'width': None,
                                'height': None,
                                },
                      'Ogg Theora':   {
                                'group': 'Format',
                                'width': None,
                                'height': None,
                                },
                      'Ogg Vorbis':   {
                                'group': 'Format',
                                'width': None,
                                'height': None,
                                },
                      'WebM':   {
                                'group': 'Format',
                                'width': None,
                                'height': None,
                                }
                      }
    

def dev_attr(device, default):
    return _DEVICES[device][default]

def devices(group):
    device_list = []
    for k, v in _DEVICES.iteritems():
        if group in v['group']:
            device_list.append(k)
    return device_list

# Dream, Magic, Eris, Hero Cliq are all the same
# iphone, ipod touch, ipod nano, ipod classic are all the same

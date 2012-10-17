import logging
import os
import sys

if sys.platform == 'darwin':
    import osx as plat
    from .osx import widgetset
else:
    import gtk as plat
    from .gtk import widgetset

attach_menubar = plat.attach_menubar
mainloop_start = plat.mainloop_start
mainloop_stop = plat.mainloop_stop
idle_add = plat.idle_add
idle_remove = plat.idle_remove
reveal_file = plat.reveal_file
get_conversion_directory = plat.get_conversion_directory

def get_conversion_directory():
    return os.path.join(plat.get_conversion_directory(), 'Miro Video Converter')

def initialize(app):
    try:
        os.makedirs(get_conversion_directory())
    except EnvironmentError, e:
        logging.info('os.makedirs: %s', str(e))
    if app:
        plat.initialize(app)

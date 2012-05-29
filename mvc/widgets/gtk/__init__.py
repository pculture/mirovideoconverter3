import gtk
import gobject

from .window import *
from .layout import *
from .controls import *
from .table import *
from .tablecells import *
from .dialogs import *
from .image import *
from .drawing import *

from gtk import DEST_DEFAULT_ALL
from gtk.gdk import ACTION_COPY

def initialize():
    pass

def mainloop_start():
    gtk.main()

def mainloop_stop():
    gtk.main_quit()

def idle_add(callback):
    def wrapper():
        callback()
        return True

    return gobject.idle_add(wrapper)

def idle_remove(id_):
    gobject.source_remove(id_)


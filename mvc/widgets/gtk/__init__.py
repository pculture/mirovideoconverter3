import gtk
import gobject

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


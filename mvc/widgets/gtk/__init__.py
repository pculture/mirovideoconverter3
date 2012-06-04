import os
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

def check_kde():
    return os.environ.get("KDE_FULL_SESSION", None) != None

def open_file_linux(filename):
    if check_kde():
        os.spawnlp(os.P_NOWAIT, "kfmclient", "kfmclient",
                   "exec", "file://" + filename)
    else:
        os.spawnlp(os.P_NOWAIT, "gnome-open", "gnome-open", filename)

def reveal_file(filename):
    if hasattr(os, 'startfile'): # Windows
        os.startfile(filename)
    else:
        open_file_linux(filename)

import sys

from AppKit import NSApplication, NSApplicationMain, NSWorkspace
from objc import nil

from PyObjCTools import AppHelper

size_request_manager = None

def initialize():
    global size_request_manager
    NSApplication.sharedApplication()
    from mvc.widgets.osx.widgetupdates import SizeRequestManager
    size_request_manager = SizeRequestManager()

def mainloop_start():
    NSApplicationMain(sys.argv)

def mainloop_stop():
    NSApplication.sharedApplication().terminate_(nil)

def idle_add(callback, periodic=None):
    def wrapper():
        callback()
        if periodic is not None:
            AppHelper.callLater(periodic, wrapper)
    if periodic is not None and periodic < 0:
        raise ValueError('periodic cannot be negative')
    AppHelper.callLater(periodic, wrapper)

def idle_remove(id_):
    pass

def reveal_file(filename):
    NSWorkspace.sharedWorkspace().selectFile_inFileViewerRootedAtPath_(
        filename, nil)

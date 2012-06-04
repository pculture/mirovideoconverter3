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
    NSApplicationMain([])

def mainloop_stop():
    NSApplication.sharedApplication().terminate_(nil)

def idle_add(callback):
    def wrapper():
        callback()
        AppHelper.callLater(1, wrapper)
    AppHelper.callLater(1, wrapper)

def idle_remove(id_):
    pass

def reveal_file(filename):
    NSWorkspace.sharedWorkspace().selectFile_inFileViewerRootedAtPath_(
        filename, nil)

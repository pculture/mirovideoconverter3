import sys

from AppKit import NSApplication, NSApplicationMain, NSWorkspace, NSObject
from objc import nil

from PyObjCTools import AppHelper

size_request_manager = None

class AppController(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        from mvc.widgets.osx.osxmenus import MenuBar
        self.portableApp.menubar = MenuBar()
        self.portableApp.startup()
        self.portableApp.run()

    def setPortableApp_(self, portableApp):
        self.portableApp = portableApp

    def handleMenuActivate_(self, menu_item):
        from mvc.widgets.osx import osxmenus
        osxmenus.handle_menu_activate(menu_item)

def initialize(app):
    nsapp = NSApplication.sharedApplication()
    delegate = AppController.alloc().init()
    delegate.setPortableApp_(app)
    nsapp.setDelegate_(delegate)

    global size_request_manager
    from mvc.widgets.osx.widgetupdates import SizeRequestManager
    size_request_manager = SizeRequestManager()

    NSApplicationMain(sys.argv)

def attach_menubar():
    pass

def mainloop_start():
    pass

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

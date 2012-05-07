from AppKit import NSApplication, NSApplicationMain
from objc import nil

from PyObjCTools import AppHelper

from .window import Window
from .layout import VBox, HBox
from .controls import OptionMenu, Button, FileChooserButton
from .table import TableModel, TableView

def initialize():
    NSApplication.sharedApplication()

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

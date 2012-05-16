from AppKit import NSApplication, NSApplicationMain
from objc import nil

from PyObjCTools import AppHelper

from .window import *
from .layout import *
from .controls import *
from .table import *

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


from AppKit import *
from objc import YES, NO, nil

from .base import Widget, FlippedView


class Window(Widget):

    SIGNAL_MAP = {
        'destroy': 'NSWindowWillCloseNotification'
        }

    def __init__(self, title):
        rect = NSMakeRect(200.0, 200.0, 800.0, 300.0)
        self.view = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSTitledWindowMask | NSClosableWindowMask |
            NSMiniaturizableWindowMask | NSResizableWindowMask,
            NSBackingStoreBuffered, NO)
        self.view.setTitle_(title)
        self.content_view = FlippedView.alloc().initWithFrame_(rect)
        self.view.setContentView_(self.content_view)
        self.content_widget = None
        super(Window, self).__init__()

    def add(self, widget):
        if self.content_widget:
            self.content_widget.remove_viewport()
        self.content_widget = widget
        rect = self.view.contentRectForFrameRect_(self.view.frame())
        widget.place(NSRect(NSPoint(0, 0), rect.size),
                     self.content_view)

    def show(self):
        self.view.makeKeyAndOrderFront_(nil)
        self.view.makeMainWindow()

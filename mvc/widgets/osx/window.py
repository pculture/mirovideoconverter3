from AppKit import *
from objc import YES, NO, nil

from .base import Widget, FlippedView
from .helpers import NotificationForwarder

class MVCWindow(NSWindow):

    def initWithContentRect_parent_(self, rect, parent):
        self = self.initWithContentRect_styleMask_backing_defer_(
            rect,
            NSTitledWindowMask | NSClosableWindowMask |
            NSMiniaturizableWindowMask | NSResizableWindowMask,
            NSBackingStoreBuffered, NO)
        self.parent = parent
        return self

    def draggingEntered_(self, info):
        return self.parent.draggingEntered_(info) or NSDragOperationNone

    def draggingUpdated_(self, info):
        return self.parent.draggingUpdated_(info) or NSDragOperationNone

    def draggingExited_(self, info):
        self.parent.draggingExited_(info)

    def prepareForDragOperation_(self, info):
        return self.parent.prepareForDragOperation_(info) or NO

    def performDragOperation_(self, info):
        return self.parent.performDragOperation_(info) or NO


class Window(Widget):

    SIGNAL_MAP = {
        'destroy': 'NSWindowWillCloseNotification'
        }

    def __init__(self, title):
        self.content_widget = None
        rect = NSMakeRect(200.0, 200.0, 800.0, 400.0)
        self.view = MVCWindow.alloc().initWithContentRect_parent_(rect, self)
        self.view.setMinSize_(NSSize(800, 400))
        self.view.setTitle_(title)
        self.content_view = FlippedView.alloc().initWithFrame_(rect)
        self.content_view.setAutoresizesSubviews_(NO)
        self.content_notifications = NotificationForwarder.create(
            self.content_view)
        self.content_notifications.connect(self.on_frame_change,
                                           'NSViewFrameDidChangeNotification')
        self.view.setContentView_(self.content_view)
        super(Window, self).__init__()

    def add(self, widget):
        if self.content_widget:
            self.unhook_content_widget_signals()
            self.content_widget.remove_viewport()
        self.content_widget = widget
        self.hookup_content_widget_signals()
        self.place_child()

    def place_child(self):
        if self.content_widget is None:
            return
        rect = self.view.contentRectForFrameRect_(self.view.frame())
        self.content_widget.place(NSRect(NSPoint(0, 0), rect.size),
                                  self.content_view)

    def show(self):
        self.view.makeKeyAndOrderFront_(nil)
        self.view.makeMainWindow()

    def on_frame_change(self, widget):
        self.place_child()

    def hookup_content_widget_signals(self):
        self.size_req_handler = self.content_widget.connect(
                'size-request-changed',
                self.on_content_widget_size_request_change)

    def unhook_content_widget_signals(self):
        self.content_widget.disconnect(self.size_req_handler)
        self.size_req_handler = None

    def on_content_widget_size_request_change(self, widget, old_size):
        width, height = self.content_widget.get_size_request()
        # It is possible the window is torn down between the size invalidate
        # request and the actual size invalidation invocation.  So check
        # to see if nswindow is there if not then do not do anything.
        if self.view and (width, height) != old_size:
            self.change_content_size(width, height)

    def change_content_size(self, width, height):
        content_rect = self.window.contentRectForFrameRect_(
                self.window.frame())
        # Cocoa's coordinate system is funky, adjust y so that the top stays
        # in place
        content_rect.origin.y += (content_rect.size.height - height)
        # change our frame to fit the new content.  It would be nice to
        # animate the change, but timers don't work when we are displaying a
        # modal dialog
        content_rect.size = NSSize(width, height)
        new_frame = self.view.frameRectForContentRect_(content_rect)
        self.view.setFrame_display_(new_frame, NO)
        # Need to call place() again, since our window has changed size
        contentView = self.view.contentView()
        self.content_widget.place(contentView.frame(), contentView)

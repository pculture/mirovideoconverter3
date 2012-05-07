from collections import defaultdict
import logging

from AppKit import NSView
from objc import YES

from .helpers import NotificationForwarder
from .viewport import Viewport, BorrowedViewport

class Widget(object):

    SIGNAL_MAP = {}
    CREATES_VIEW = True
    view = None
    viewport = None

    def __init__(self):
        if self.CREATES_VIEW and self.view:
            self.notifications = NotificationForwarder.create(self.view)
            for signal, notification in self.SIGNAL_MAP.iteritems():
                self.notifications.connect(lambda n: self.emit(signal),
                                           notification)
        self.emitting = set()
        self.listeners = defaultdict(set)
        self.cached_size_request = None

    def connect(self, signal, callback):
        self.listeners[signal].add(callback)

    def emit(self, signal):
        if signal in self.emitting:
            return
        self.emitting.add(signal)
        if signal in self.listeners:
            for listener in self.listeners[signal]:
                try:
                    listener(self)
                except:
                    logging.error('during signal %r on %r', signal, self,
                                  exc_info=True)
        self.emitting.remove(signal)

    def invalidate_size_request(self):
        self.cached_size_request = None

    def get_size_request(self):
        if self.cached_size_request is None:
            self.cached_size_request = self.calc_size_request()
        return self.cached_size_request

    def calc_size_request(self):
        raise NotImplementedError()

    def place(self, rect, containing_view):
        if self.viewport is None:
            if self.CREATES_VIEW:
                self.viewport = Viewport(self.view, rect)
                containing_view.addSubview_(self.view)
            else:
                self.viewport = BorrowedViewport(containing_view, rect)
            self.viewport_created()
        else:
            if not self.viewport.at_position(rect):
                self.viewport.reposition(rect)
                self.viewport_repositioned()

    def viewport_created(self):
        pass

    def viewport_repositioned(self):
        pass


class FlippedView(NSView):
    """Flipped NSView.  We use these internally to lessen the differences
    between Cocoa and GTK.
    """

    def isFlipped(self):
        return YES

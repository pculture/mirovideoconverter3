from collections import defaultdict
import logging

from AppKit import *
from objc import YES, NO

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
        self.drag_dest = None

    def create_signal(self, signal):
        pass

    def connect(self, signal, callback):
        self.listeners[signal].add(callback)
        return (signal, callback)

    def disconnect(self, (signal, callback)):
        self.listeners[signal].remove(callback)

    def emit(self, signal, *args):
        if signal in self.emitting:
            return
        self.emitting.add(signal)
        if signal in self.listeners:
            for listener in self.listeners[signal]:
                try:
                    listener(self, *args)
                except:
                    logging.error('during signal %r on %r', signal, self,
                                  exc_info=True)
        self.emitting.remove(signal)

    def invalidate_size_request(self):
        old_size_request = self.cached_size_request
        self.cached_size_request = None
        self.emit('size-request-changed', old_size_request)

    def get_size_request(self):
        if self.cached_size_request is None:
            self.cached_size_request = self.calc_size_request()
        return self.cached_size_request

    def calc_size_request(self):
        raise NotImplementedError(
            "%s.calc_size_request()" % self.__class__.__name__)

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

    def remove_viewport(self):
        if self.viewport is not None:
            self.viewport.remove()
            self.viewport = None

    def viewport_created(self):
        pass

    def viewport_repositioned(self):
        pass

    def accept_file_drag(self, val):
        if not val:
            self.drag_dest = None
        else:
            self.drag_dest = NSDragOperationCopy
            self.view.registerForDraggedTypes_([NSURLPboardType])

    def prepareForDragOperation_(self, info):
        return NO if self.drag_dest is None else YES

    def performDragOperation_(self, info):
        pb = info.draggingPasteboard()
        point = info.draggingLocation()
        available_types = set(pb.types()) & set([NSURLPboardType])
        if available_types:
            type_ = available_types.pop()
            values = list(pb.propertyListForType_(type_))
            self.emit('file-drag-received', values)
        self.draggingExited_(info)

    def draggingEntered_(self, info):
        return self.draggingUpdated_(info)

    def draggingUpdated_(self, info):
        point = info.draggingLocation()
        self.emit('file-drag-motion')
        return self.drag_dest

    def draggingExited_(self, info):
        self.emit('file-drag-leave')


class Container(Widget):
    """Widget that holds other widgets.  """

    def __init__(self):
        Widget.__init__(self)
        self.callback_handles = {}

    def on_child_size_request_changed(self, child, old_size):
        self.invalidate_size_request()

    def connect_child_signals(self, child):
        handle = child.connect('size-request-changed',
                               self.on_child_size_request_changed)
        self.callback_handles[child] = handle

    def disconnect_child_signals(self, child):
        child.disconnect(self.callback_handles.pop(child))

    def remove_viewport(self):
        for child in self.children:
            child.remove_viewport()
        Widget.remove_viewport(self)

    def child_added(self, child):
        """Must be called by subclasses when a child is added to the
        Container."""
        self.connect_child_signals(child)
        self.children_changed()

    def child_removed(self, child):
        """Must be called by subclasses when a child is removed from the
        Container."""
        self.disconnect_child_signals(child)
        child.remove_viewport()
        self.children_changed()

    def child_changed(self, old_child, new_child):
        """Must be called by subclasses when a child is replaced by a new
        child in the Container.  To simplify things a bit for subclasses,
        old_child can be None in which case this is the same as
        child_added(new_child).
        """
        if old_child is not None:
            self.disconnect_child_signals(old_child)
            old_child.remove_viewport()
        self.connect_child_signals(new_child)
        self.children_changed()

    def children_changed(self):
        """Invoked when the set of children for this widget changes."""
        self.invalidate_size_request()

    def invalidate_size_request(self):
        Widget.invalidate_size_request(self)
        if self.viewport:
            self.place_children()

    def viewport_created(self):
        self.place_children()

    def viewport_repositioned(self):
        self.place_children()

    def viewport_scrolled(self):
        for child in self.children:
            child.viewport_scrolled()

    def place_children(self):
        """Layout our child widgets.  Must be implemented by subclasses."""
        raise NotImplementedError(
            "%s.place_children()" % self.__class__.__name__)


class Bin(Container):
    """Container that only has one child widget."""

    def __init__(self, child=None):
        Container.__init__(self)
        self.child = None
        if child is not None:
            self.add(child)

    def get_children(self):
        if self.child:
            return [self.child]
        else:
            return []
    children = property(get_children)

    def get_child(self):
        return self.child

    def add(self, child):
        if self.child is not None:
            raise ValueError("Already have a child: %s" % self.child)
        self.child = child
        self.child_added(self.child)

    def remove(self, child=None):
        if self.child is not None:
            old_child = self.child
            self.child = None
            self.child_removed(old_child)

    def set_child(self, new_child):
        old_child = self.child
        self.child = new_child
        self.child_changed(old_child, new_child)

    def enable(self):
        Container.enable(self)
        self.child.enable()

    def disable(self):
        Container.disable(self)
        self.child.disable()


class FlippedView(NSView):
    """Flipped NSView.  We use these internally to lessen the differences
    between Cocoa and GTK.
    """

    def isFlipped(self):
        return YES


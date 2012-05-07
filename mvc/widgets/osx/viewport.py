from objc import YES, NO, nil
from Foundation import *

class Viewport(object):
    """Used when a widget creates it's own NSView."""
    def __init__(self, view, initial_frame):
        self.view = view
        self.view.setFrame_(initial_frame)
        self.placement = initial_frame

    def at_position(self, rect):
        """Check if a viewport is currently positioned at rect."""
        return self.placement == rect

    def reposition(self, rect):
        """Move the viewport to a different position."""
        self.view.setFrame_(rect)
        self.placement = rect

    def remove(self):
        self.view.removeFromSuperview()

    def area(self):
        """Area of our view that is occupied by the viewport."""
        return NSRect(self.view.bounds().origin, self.placement.size)

    def get_width(self):
        return self.view.frame().size.width

    def get_height(self):
        return self.view.frame().size.height

    def queue_redraw(self):
        opaque_view = self.view.opaqueAncestor()
        if opaque_view is not None:
            rect = opaque_view.convertRect_fromView_(self.area(), self.view)
            opaque_view.setNeedsDisplayInRect_(rect)

    def redraw_now(self):
        self.view.displayRect_(self.area())

class BorrowedViewport(Viewport):
    """Used when a widget uses the NSView of one of it's ancestors.  We store
    the view that we borrow as well as an NSRect specifying where on that view
    we are placed.
    """
    def __init__(self, view, placement):
        self.view = view
        self.placement = placement

    def at_position(self, rect):
        return self.placement == rect

    def reposition(self, rect):
        self.placement = rect

    def remove(self):
        pass

    def area(self):
        return self.placement

    def get_width(self):
        return self.placement.size.width

    def get_height(self):
        return self.placement.size.height

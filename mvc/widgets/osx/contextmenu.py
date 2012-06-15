from AppKit import *
from objc import nil

from .base import Widget

class ContextMenuHandler(NSObject):
    def initWithCallback_widget_i_(self, callback, widget, i):
        self = super(ContextMenuHandler, self).init()
        self.callback = callback
        self.widget = widget
        self.i = i
        return self

    def handleMenuItem_(self, sender):
        self.callback(self.widget, self.i)


class MiroContextMenu(NSMenu):
    # Works exactly like NSMenu, except it keeps a reference to the menu
    # handler objects.
    def init(self):
        self = super(MiroContextMenu, self).init()
        self.handlers = set()
        return self

    def addItem_(self, item):
        if isinstance(item.target(), ContextMenuHandler):
            self.handlers.add(item.target())
        return NSMenu.addItem_(self, item)


class ContextMenu(object):

    def __init__(self, options):
        super(ContextMenu, self).__init__()
        self.menu = MiroContextMenu.alloc().init()
        for i, item_info in enumerate(options):
            if item_info is None:
                nsitem = NSMenuItem.separatorItem()
            else:
                label, callback = item_info
                nsitem = NSMenuItem.alloc().init()
                font_size = NSFont.systemFontSize()
                font = NSFont.fontWithName_size_("Lucida Sans Italic", font_size)
                if font is None:
                    font = NSFont.systemFontOfSize_(font_size)
                    attributes = {NSFontAttributeName: font}
                    attributed_label = NSAttributedString.alloc().initWithString_attributes_(label, attributes)
                    nsitem.setAttributedTitle_(attributed_label)
                else:
                    nsitem.setTitle_(label)
                handler = ContextMenuHandler.alloc().initWithCallback_widget_i_(callback, self, i)
                nsitem.setTarget_(handler)
                nsitem.setAction_('handleMenuItem:')
            self.menu.addItem_(nsitem)

    def popup(self):
        # support for non-window based popups thanks to
        # http://stackoverflow.com/questions/9033534/how-can-i-pop-up-nsmenu-at-mouse-cursor-position
        location = NSEvent.mouseLocation()
        frame = NSMakeRect(location.x, location.y, 200, 200)
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSBorderlessWindowMask,
            NSBackingStoreBuffered,
            NO)
        window.setAlphaValue_(0)
        window.makeKeyAndOrderFront_(NSApp)
        location_in_window = window.convertScreenToBase_(location)
        event = NSEvent.mouseEventWithType_location_modifierFlags_timestamp_windowNumber_context_eventNumber_clickCount_pressure_(
            NSLeftMouseDown,
            location_in_window,
            0,
            0,
            window.windowNumber(),
            nil,
            0,
            0,
            0)
        NSMenu.popUpContextMenu_withEvent_forView_(self.menu, event, window.contentView())

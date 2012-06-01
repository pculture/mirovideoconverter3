import os
import math

from objc import *
from AppKit import *
from Foundation import *

from .base import Widget
from .drawing import make_color, DrawingMixin, DrawingContext, DrawingStyle
from .layoutmanager import LayoutManager


class MVCPopUpButton(NSPopUpButton):

    def initWithParent_(self, parent):
        self = super(MVCPopUpButton, self).init()
        self.parent = parent
        self.setTarget_(self)
        self.setAction_("handleChange:")
        return self

    def handleChange_(self, sender):
        self.parent.emit('changed')


class OptionMenu(Widget):

    def __init__(self, options):
        self.view = MVCPopUpButton.alloc().initWithParent_(self)
        titles, options = zip(*options)
        self.options = options
        self.view.addItemsWithTitles_(titles)
        super(OptionMenu, self).__init__()

    def calc_size_request(self):
        size = self.view.cell().cellSize()
        return size.width, size.height

    def set_selected(self, index):
        self.view.selectItemAtIndex_(index)

    def get_selected(self):
        index = self.view.indexOfSelectedItem()
        return self.options[index]


class MVCButton(NSButton):
    def initWithParent_(self, parent):
        self.parent = parent
        return super(MVCButton, self).init()

    def sendAction_to_(self, action, to):
        self.parent.on_clicked()


class Button(Widget):
    def __init__(self, title):
        self.view = MVCButton.alloc().initWithParent_(self)
        self.view.setButtonType_(NSMomentaryPushInButton)
        self.view.setBezelStyle_(NSRoundedBezelStyle)
        self.view.setTitle_(title)
        super(Button, self).__init__()

    def calc_size_request(self):
        size = self.view.cell().cellSize()
        return max(size.width + 10, 112), size.height

    def on_clicked(self):
        self.emit('clicked')

    def disable(self):
        self.view.setEnabled_(NO)

    def enable(self):
        self.view.setEnabled_(YES)

    def set_label(self, text):
        self.view.setTitle_(text)


class DrawableButtonCell(NSButtonCell):
    def startTrackingAt_inView_(self, point, view):
        view.setState_(NSOnState)
        return YES

    def continueTracking_at_inView_(self, lastPoint, at, view):
        view.setState_(NSOnState)
        return YES

    def stopTracking_at_inView_mouseIsUp_(self, lastPoint, at, view, mouseIsUp):
        if not mouseIsUp:
            view.mouse_inside = False
            view.setState_(NSOffState)


class DrawableButton(NSButton):
    def initWithParent_(self, parent):
        self = super(DrawableButton, self).init()
        self.parent = parent
        self.layout_manager = LayoutManager()
        self.tracking_area = None
        self.mouse_inside = False
        self.custom_cursor = None
        return self

    def resetCursorRects(self):
        if self.custom_cursor is not None:
            self.addCursorRect_cursor_(self.visibleRect(), self.custom_cursor)
            self.custom_cursor.setOnMouseEntered_(YES)

    def updateTrackingAreas(self):
        # remove existing tracking area if needed
        if self.tracking_area:
            self.removeTrackingArea_(self.tracking_area)

        # create a new tracking area for the entire view.  This allows us to
        # get mouseMoved events whenever the mouse is inside our view.
        self.tracking_area = NSTrackingArea.alloc()
        self.tracking_area.initWithRect_options_owner_userInfo_(
                self.visibleRect(),
                NSTrackingMouseEnteredAndExited | NSTrackingMouseMoved |
                NSTrackingActiveInKeyWindow,
                self,
                nil)
        self.addTrackingArea_(self.tracking_area)

    def mouseEntered_(self, event):
        window = self.window()
        if window is not nil and window.isMainWindow():
            self.mouse_inside = True
            self.setNeedsDisplay_(YES)

    def mouseExited_(self, event):
        window = self.window()
        if window is not nil and window.isMainWindow():
            self.mouse_inside = False
            self.setNeedsDisplay_(YES)

    def isOpaque(self):
        return self.parent.is_opaque()

    def drawRect_(self, rect):
        context = DrawingContext(self, self.bounds(), rect)
        context.style = DrawingStyle()
        self.parent.state = 'normal'
        # disabled = self.parent.get_disabled()
        # if not disabled:
        #     if self.state() == NSOnState:
        #         self.parent.state = 'pressed'
        #     elif self.mouse_inside:
        #         self.parent.state = 'hover'
        #     else:
        #         self.parent.state = 'normal'

        self.parent.draw(context, self.layout_manager)
        self.layout_manager.reset()

    def sendAction_to_(self, action, to):
        # We override the Cocoa machinery here and just send it to our wrapper
        # widget.
        disabled = self.parent.get_disabled()
        if not disabled:
            self.parent.emit('clicked')
        # Tell Cocoa we handled it anyway, just not emit the actual clicked
        # event.
        return YES
DrawableButton.setCellClass_(DrawableButtonCell)


class CustomButton(DrawingMixin, Widget):
    """See https://develop.participatoryculture.org/index.php/WidgetAPI for a description of the API for this class."""
    def __init__(self):
        super(CustomButton, self).__init__()
        self.create_signal('clicked')
        self.view = DrawableButton.alloc().initWithParent_(self)
        self.view.custom_cursor = NSCursor.pointingHandCursor()
        self.view.setRefusesFirstResponder_(NO)
        self.view.setEnabled_(True)

    def enable(self):
        self.view.setNeedsDisplay_(YES)

    def disable(self):
        self.view.setNeedsDisplay_(YES)


class FileChooserButton(Button):

    def __init__(self, title):
        super(FileChooserButton, self).__init__(title)
        self.filename = None

    def on_clicked(self):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(YES)
        panel.setCanChooseDirectories_(NO)
        response = panel.runModalForDirectory_file_(os.getcwd(), "")
        if response == NSFileHandlingPanelOKButton:
            self.filename = panel.filename()
        else:
            self.filename = ""

    def get_filename(self):
        return self.filename


class Label(Widget):
    def __init__(self, text=None, markup=False, color=None):
        self.view = NSTextField.alloc().init()
        self.view.setEditable_(NO)
        self.view.setBezeled_(NO)
        self.view.setBordered_(NO)
        self.view.setDrawsBackground_(NO)
        super(Label, self).__init__()
        self.sizer_cell = self.view.cell().copy()
        self.set_text(text)
        if color is not None:
            self.set_color(color)

    def set_text(self, text):
        self.string_value, _ = NSAttributedString.alloc().initWithHTML_documentAttributes_(buffer(text), nil)
        # fallback
        if self.string_value is None:
            self.string_value = text
        self.view.setAttributedStringValue_(self.string_value)
        self.sizer_cell.setAttributedStringValue_(self.string_value)
        self.invalidate_size_request()

    def calc_size_request(self):
        size = self.sizer_cell.cellSize()
        return math.ceil(size.width), math.ceil(size.height)

    def set_color(self, color):
        self.view.setTextColor_(make_color(color))


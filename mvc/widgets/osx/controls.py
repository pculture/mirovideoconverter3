import os
import math

from AppKit import *

from .base import Widget

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
    def __init__(self, text=None, markup=False):
        self.view = NSTextField.alloc().init()
        self.view.setEditable_(NO)
        self.view.setBezeled_(NO)
        self.view.setBordered_(NO)
        self.view.setDrawsBackground_(NO)
        super(Label, self).__init__()
        self.sizer_cell = self.view.cell().copy()
        self.set_text(text)


    def set_text(self, text):
        self.view.setStringValue_(text)
        self.sizer_cell.setStringValue_(text)
        self.invalidate_size_request()

    def calc_size_request(self):
        size = self.sizer_cell.cellSize()
        return math.ceil(size.width), math.ceil(size.height)


import gtk

from .base import Widget

class ContextMenu(Widget):

    def __init__(self, options):
        super(ContextMenu, self).__init__()
        self.set_widget(gtk.Menu())
        for item_info in options:
            if item_info is None:
                # separator
                item = gtk.SeparatorMenuItem()
            else:
                label, callback = item_info
                item = gtk.MenuItem(label)
                if callback is not None:
                    item.connect('activate', self.on_activate, callback)
                else:
                    item.set_sensitive(False)
            self._widget.append(item)
            item.show()

    def popup(self):
        self._widget.popup(None, None, None, 0, 0)

    def on_activate(self, widget, callback):
        callback(self)

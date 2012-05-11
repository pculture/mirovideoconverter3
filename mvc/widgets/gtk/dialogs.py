import gtk

class FileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title=None):
        super(FileChooserDialog, self).__init__(
            title,
            buttons=(
                gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        self.set_select_multiple(True)

    def run(self):
        response = super(FileChooserDialog, self).run()
        return response == gtk.RESPONSE_ACCEPT

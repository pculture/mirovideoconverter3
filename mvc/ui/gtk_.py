import gtk
import gobject

import mvc
from miro import app
from miro.plat.frontends.widgets import widgetset

class Application(mvc.Application):

    def startup(self):
        if self.started:
            return

        mvc.Application.startup(self)
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Miro Video Converter')

        self.menubar = None

        rect = widgetset.Rect(100, 300, 800, 600)
        self.mainwindow = widgetset.MainWindow('Miro Video Converter', rect)
        self.hbox = widgetset.HBox()
        def on_clicked(widget):
            print 'clicked %s' % widget.label.get_text()
        for i in xrange(0, 6):
            b = widgetset.Button('Test Button %d' % i)
            b.connect('clicked', on_clicked)
            self.hbox.pack_start(b)
        self.mainwindow.set_content_widget(self.hbox)
        self.mainwindow.show()
        
        self.chooser = gtk.FileChooserButton('Add a file to convert')
        self.chooser.show()

        store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for converter in self.converter_manager.list_converters():
            store.append((converter.name, converter.identifier))
        self.conversions = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        self.conversions.pack_start(cell, True)
        self.conversions.add_attribute(cell, 'text', 0)
        self.conversions.set_active_iter(store.get_iter_first())
        self.conversions.show()

        convert = gtk.Button("Convert!")
        convert.connect('clicked', self.convert)
        convert.show()

        bottom = gtk.HBox()
        bottom.pack_start(self.chooser)
        bottom.pack_start(self.conversions)
        bottom.pack_start(convert)
        bottom.show()

        self.model = gtk.ListStore(gobject.TYPE_STRING, # name
                                   gobject.TYPE_STRING, # output
                                   gobject.TYPE_STRING, # converter
                                   gobject.TYPE_STRING, # status
                                   gobject.TYPE_INT, # duration
                                   gobject.TYPE_INT, # progress
                                   gobject.TYPE_INT) # eta
        self.table = gtk.TreeView(self.model)
        self.table.set_size_request(-1, 200)
        for i, name in enumerate(('Name', 'Output', 'Converter', 'Status',
                                  'Duration', 'Progress', 'ETA')):
            self.table.insert_column_with_attributes(
                i, name, gtk.CellRendererText(), text=i)
        self.table.show()

        vbox = gtk.VBox()
        vbox.pack_start(self.table)
        vbox.pack_end(bottom)
        vbox.show()

        self.window.add(vbox)
        self.window.connect('destroy', self.destroy)
        self.window.show()

        gobject.idle_add(self.check_notifications)

    def destroy(self, widget):
        gtk.main_quit()

    def convert(self, widget):
        iter_ = self.conversions.get_active_iter()
        if not iter_:
            return
        identifier = self.conversions.get_model()[iter_][1]
        filename = self.chooser.get_filename()
        if not filename:
            return
        c = self.start_conversion(filename, identifier)
        c.listen(self.update_conversion)
        self.update_conversion(c)

    def update_conversion(self, conversion):
        values = (conversion.video.filename,
                  conversion.output,
                  conversion.converter.name,
                  conversion.status,
                  conversion.duration or 0,
                  conversion.progress or 0,
                  conversion.eta or 0)
        if not hasattr(conversion, '_iter'):
            conversion._iter = self.table.get_model().append(values)
        else:
            [self.table.get_model().set_value(conversion._iter,
                                              i, v)
             for i, v in enumerate(values)]

    def check_notifications(self):
        self.conversion_manager.check_notifications()
        return True

    def run(self):
        gtk.main()


if __name__ == "__main__":
    a = Application()
    app.widgetapp = a
    a.startup()
    a.run()

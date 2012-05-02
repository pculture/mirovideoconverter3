import mvc

from mvc.widgets import *

class Application(mvc.Application):

    def startup(self):
        if self.started:
            return

        mvc.Application.startup(self)

        self.window = Window("Miro Video Converter")
        self.window.connect('destroy', self.destroy)

        # # table on top
        self.table = ConversionTable()

        # # bottom buttons
        self.chooser = FileChooserButton('Add a File to Convert')

        options = [(c.name, c.identifier) for c in
                   self.converter_manager.list_converters()]
        self.conversions = OptionMenu(options)

        convert = Button("Convert!")
        convert.connect('clicked', self.convert)

        bottom = HBox()
        bottom.pack_start(self.chooser)
        bottom.pack_start(self.conversions)
        bottom.pack_start(convert)

        # # finish up
        vbox = VBox()
        vbox.pack_start(self.table)
        vbox.pack_end(bottom)
        self.window.add(vbox)

        idle_add(self.conversion_manager.check_notifications)

        self.window.show()

    def destroy(self, widget):
        mainloop_stop()

    def run(self):
        mainloop_start()

    def convert(self, widget):
        identifier = self.conversions.get_selected()
        if identifier is None:
            return
        filename = self.chooser.get_filename()
        if not filename:
            return
        c = self.start_conversion(filename, identifier)
        c.listen(self.update_conversion)
        self.update_conversion(c)

    def update_conversion(self, conversion):
        self.table.update_conversion(conversion)

if __name__ == "__main__":
    app = Application()
    app.startup()
    app.run()

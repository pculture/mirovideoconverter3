try:
    import mvc
except ImportError:
    import os.path, sys
    mvc_path = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.append(mvc_path)
    import mvc

from mvc.widgets import *

TABLE_COLUMNS = (
    ("Name", unicode),
    ("Output", unicode),
    ("Converter", unicode),
    ("Status", unicode),
    ("Duration", int),
    ("Progress", int),
    ("ETA", int))

class ConversionModel(TableModel):
    def __init__(self):
        super(ConversionModel, self).__init__(zip(*TABLE_COLUMNS)[1])
        self.conversion_to_iter = {}

    def update_conversion(self, conversion):
        values = (conversion.video.filename,
                  conversion.output,
                  conversion.converter.name,
                  conversion.status,
                  conversion.duration or 0,
                  conversion.progress or 0,
                  conversion.eta or 0)
        iter_ = self.conversion_to_iter.get(conversion)
        if iter_ is None:
            self.conversion_to_iter[conversion] = self.append(values)
        else:
            self.update_iter(iter_, values)


class Application(mvc.Application):

    def startup(self):
        if self.started:
            return

        mvc.Application.startup(self)

        self.window = Window("Miro Video Converter")
        self.window.connect('destroy', self.destroy)

        # # table on top
        self.model = ConversionModel()
        self.table = TableView(self.model)

        for name in zip(*TABLE_COLUMNS)[0]:
            self.table.add_column(name)

        # bottom buttons
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
        vbox.pack_start(self.table, expand=True)
        vbox.pack_end(bottom)
        self.window.add(vbox)

        idle_add(self.conversion_manager.check_notifications)

        self.window.show()

    def destroy(self, widget):
        for conversion in self.conversion_manager.in_progress.copy():
            conversion.stop()
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
        self.model.update_conversion(conversion)

if __name__ == "__main__":
    initialize()
    app = Application()
    app.startup()
    app.run()

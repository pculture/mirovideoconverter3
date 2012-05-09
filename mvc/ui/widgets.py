try:
    import mvc
except ImportError:
    import os.path, sys
    mvc_path = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.append(mvc_path)
    import mvc

import urllib

from mvc.widgets import *

from mvc.video import VideoFile

TABLE_COLUMNS = (
    ("Name", unicode),
    ("Output", unicode),
    ("Converter", unicode),
    ("Status", unicode),
    ("Duration", int),
    ("Progress", int),
    ("ETA", int))

class FileDropTarget(Alignment):
    def __init__(self):
        super(FileDropTarget, self).__init__(
            xscale=0.5, yscale=0.5,
            top_pad=50, right_pad=40,
            bottom_pad=50, left_pad=40)
        self.connect('drag-motion', self.drag_motion)
        self.connect('drag-data-received', self.drag_data_received)
        self.connect('drag-leave', self.drag_finished)
        self.drag_dest_set(DEST_DEFAULT_ALL, [
                ('text/uri-list', 0, 0)], ACTION_COPY)

        self.create_signal('file-activated')
        hbox = self.normal = HBox()
        hbox.pack_start(Label("Drag more videos here or "))

        file_chooser = Label("<a href=''>Choose File...</a>", markup=True)
        file_chooser.connect('clicked', self.choose_file)
        hbox.pack_start(file_chooser)
        self.add(hbox)

        self.drag = HBox()
        self.drag.pack_start(Label("Release button to drop off"))

        self.in_drag = False

    def set_in_drag(self, in_drag):
        if in_drag != self.in_drag:
            self.in_drag = in_drag
            self.remove(self.get_child())
            if in_drag:
                self.add(self.drag)
            else:
                self.add(self.normal)

    def choose_file(self, widget):
        dialog = FileChooserDialog('Choose File...')
        if dialog.run():
            for filename in dialog.get_filenames():
                self.emit('file-activated', filename)
        dialog.destroy()

    def drag_finished(self, widget, context, time):
        self.set_in_drag(False)

    def drag_motion(self, widget, context, x, y, time):
        self.set_in_drag(True)

    def drag_data_received(self, widget, context, x, y,
                           selection_data, info, time):
        for uri in selection_data.get_uris():
            if uri.startswith('file://'):
                pathname = urllib.url2pathname(uri[7:])
                self.emit('file-activated', pathname)



class ConversionModel(TableModel):
    def __init__(self):
        super(ConversionModel, self).__init__(zip(*TABLE_COLUMNS)[1])
        self.conversion_to_iter = {}

    def conversions(self):
        return iter(self.conversion_to_iter)

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
        converter_types = ('apple', 'android', 'other', 'format')
        converters = {}
        for c in self.converter_manager.list_converters():
            media_type = c.media_type
            if media_type not in converter_types:
                media_type = 'others'
            converters.setdefault(media_type, []).append(c)

        self.menus = []
        bottom = HBox()

        for type_ in converter_types:
            options = [(c.name, c.identifier) for c in
                       converters[type_]]
            options.sort()
            options.insert(0, (type_.title(), None))
            menu = OptionMenu(options)
            menu.connect('changed', self.change_conversion)
            self.menus.append(menu)
            bottom.pack_start(menu)


        self.convert_button = Button("Start Conversions!")
        self.convert_button.disable()
        self.convert_button.connect('clicked', self.convert)
        bottom.pack_start(self.convert_button)

        drop_target = FileDropTarget()
        drop_target.connect('file-activated', self.file_activated)

        # # finish up
        vbox = VBox()
        vbox.pack_start(self.table, expand=True)
        vbox.pack_start(drop_target)
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

    def file_activated(self, widget, filename):
        if self.current_conversion is None:
            return
        vf = VideoFile(filename)
        converter = self.converter_manager.get_by_id(identifier)
        c = self.conversion_manager.get_conversion(vf, converter)
        c.listen(self.update_conversion)
        self.update_conversion(c)

    def change_conversion(self, widget):
        if hasattr(self, '_doing_conversion_change'):
            return
        self._doing_conversion_change = True

        self.current_conversion = widget.get_selected()
        if self.current_conversion is None:
            self.convert_button.disable()
        else:
            self.convert_button.enable()
        for menu in self.menus:
            if menu is not widget:
                menu.set_selected(0)

        del self._doing_conversion_change

    def convert(self, widget):
        if not self.conversion_manager.running:
            started = False
            for conversion in self.model.conversions():
                if conversion.status == 'initialized':
                    started = True
                    self.conversion_manager.run_conversion(conversion)
            if started:
                widget.set_label('Cancel Conversions')
        else:
            for conversion in self.model.conversions():
                conversion.stop()

    def update_conversion(self, conversion):
        self.model.update_conversion(conversion)
        if not self.conversion_manager.running:
            self.convert_button.set_label('Start Conversions!')


if __name__ == "__main__":
    initialize()
    app = Application()
    app.startup()
    app.run()

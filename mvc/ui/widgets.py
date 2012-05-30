import os.path

try:
    import mvc
except ImportError:
    import os.path, sys
    mvc_path = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.append(mvc_path)
    import mvc

import urllib
import urlparse

from mvc.widgets import *
from mvc.widgets import cellpack

from mvc.converter import ConverterInfo
from mvc.video import VideoFile
from mvc.resources import image_path

LARGE_FONT = 13.0 / 13.0
SMALL_FONT = 10.0 / 13.0


def css_to_color(css_string):
    parts = (css_string[1:3], css_string[3:5], css_string[5:7])
    return tuple((int(value, 16) / 255.0) for value in parts)


GRADIENT_TOP = css_to_color('#585f63')
GRADIENT_BOTTOM = css_to_color('#383d40')

DRAG_AREA = css_to_color('#2b2e31')

TEXT_DISABLED = css_to_color('#333333')
TEXT_ACTIVE = css_to_color('#ffffff')
TEXT_INFO = css_to_color('#808080')
TEXT_COLOR = css_to_color('#ffffff')

class FileDropTarget(SolidBackground):

    dropoff_on = ImageDisplay(Image.from_file(
            image_path("dropoff-icon-on.png")))
    dropoff_off = ImageDisplay(Image.from_file(
            image_path("dropoff-icon-off.png")))
    dropoff_small_on = ImageDisplay(Image.from_file(
            image_path("dropoff-icon-small-on.png")))
    dropoff_small_off = ImageDisplay(Image.from_file(
            image_path("dropoff-icon-small-off.png")))

    def __init__(self):
        super(FileDropTarget, self).__init__()
        self.set_background_color(DRAG_AREA)
        self.alignment = Alignment(
            xscale=0.0, yscale=0.5,
            xalign=0.5, yalign=0.5,
            top_pad=10, right_pad=40,
            bottom_pad=10, left_pad=40)
        self.add(self.alignment)

        self.create_signal('file-activated')

        self.widgets = {
            False: self.build_large_widgets(),
            True: self.build_small_widgets()
            }

        self.normal, self.drag = self.widgets[False]
        self.alignment.add(self.normal)

        self.in_drag = False
        self.small = False

    def build_large_widgets(self):
        normal = VBox(spacing=20)
        normal.pack_start(self.dropoff_on)
        normal.pack_start(Label(
            "Drag videos here or <a href=''>Choose File...</a>",
            markup=True,
            color=TEXT_COLOR))

        drag = VBox(spacing=20)
        drag.pack_start(self.dropoff_off)
        drag.pack_start(Label("Release button to drop off",
                              color=TEXT_COLOR))
        return normal, drag

    def build_small_widgets(self):
        normal = HBox(spacing=10)
        normal.pack_start(self.dropoff_small_on)
        normal.pack_start(Label(
            "Drag more videos here or <a href=''>Choose File...</a>",
            markup=True,
            color=TEXT_COLOR))

        drag = HBox(spacing=10)
        drag.pack_start(self.dropoff_small_off)
        drag.pack_start(Label("Release button to drop off",
                              color=TEXT_COLOR))
        return normal, drag

    def set_small(self, small):
        if small != self.small:
            self.small = small
            self.normal, self.drag = self.widgets[small]
            self.set_in_drag(self.in_drag, force=True)

    def set_in_drag(self, in_drag, force=False):
        if force or in_drag != self.in_drag:
            self.in_drag = in_drag
            if in_drag:
                self.alignment.set_child(self.drag)
            else:
                self.alignment.set_child(self.normal)

    def choose_file(self, widget):
        dialog = FileChooserDialog('Choose File...')
        if dialog.run():
            for filename in dialog.get_filenames():
                self.emit('file-activated', filename)
        dialog.destroy()


EMPTY_CONVERTER = ConverterInfo("")


class ConversionModel(TableModel):
    def __init__(self):
        super(ConversionModel, self).__init__((
            unicode, # filename
            unicode, # output
            unicode, # converter
            unicode, # status
            float, # duration
            float, # progress
            float, # eta,
            Image, # image
            ))
        self.conversion_to_iter = {}
        self.thumbnail_to_image = {}

    def conversions(self):
        return iter(self.conversion_to_iter)

    def get_image(self, path):
        if path not in self.thumbnail_to_image:
            self.thumbnail_to_image[path] = Image.from_file(path)
        return self.thumbnail_to_image[path]

    def update_conversion(self, conversion):
        values = (conversion.video.filename,
                  conversion.output,
                  conversion.converter.name,
                  conversion.status,
                  conversion.duration or 0,
                  conversion.progress or 0,
                  conversion.eta or 0,
                  self.get_image(conversion.video.get_thumbnail(90, 70)),
                  )
        iter_ = self.conversion_to_iter.get(conversion)
        if iter_ is None:
            self.conversion_to_iter[conversion] = self.append(values)
        else:
            self.update_iter(iter_, values)

class ConversionCellRenderer(CustomCellRenderer):

    clear = ImageSurface(Image.from_file(
            image_path("clear-icon.png")))
    converted_to = ImageSurface(Image.from_file(
            image_path("converted_to-icon.png")))
    queued = ImageSurface(Image.from_file(
            image_path("queued-icon.png")))
    showfile = ImageSurface(Image.from_file(
            image_path("showfile-icon.png")))
    progressbar_base = ImageSurface(Image.from_file(
            image_path("progressbar-base.png")))
    delete_on = ImageSurface(Image.from_file(
            image_path("item-delete-button-on.png")))
    delete_off = ImageSurface(Image.from_file(
            image_path("item-delete-button-off.png")))
    error = ImageSurface(Image.from_file(
            image_path("item-error.png")))
    completed = ImageSurface(Image.from_file(
            image_path("item-completed.png")))

    def get_size(self, style, layout_manager):
        return 350, 90

    def render(self, context, layout_manager, selected, hotspot, hover):
        left_right = cellpack.HBox()
        top_bottom = cellpack.VBox()
        left_right.pack(self.layout_left(layout_manager))
        left_right.pack(top_bottom, expand=True)
        layout_manager.set_text_color(TEXT_COLOR)
        layout_manager.set_font(LARGE_FONT, bold=True)
        title = layout_manager.textbox(os.path.basename(self.input))
        title.set_wrap_style('truncated-char')
        alignment = cellpack.Padding(cellpack.TruncatedTextLine(title),
                                     top=25)
        top_bottom.pack(alignment)
        layout_manager.set_font(SMALL_FONT)

        bottom = self.layout_bottom(layout_manager)
        if bottom is not None:
            top_bottom.pack(bottom)
        left_right.pack(self.layout_right(layout_manager))

        alignment = cellpack.Alignment(left_right, yscale=0, yalign=0.5)

        background = cellpack.Background(alignment)
        background.set_callback(self.draw_background)
        background.render_layout(context)

    @staticmethod
    def draw_background(context, x, y, width, height):
        gradient = Gradient(x, y + 1, x, height - 1)
        gradient.set_start_color(GRADIENT_TOP)
        gradient.set_end_color(GRADIENT_BOTTOM)
        context.rectangle(x, y + 1, width, height -1 )
        context.gradient_fill(gradient)
        context.set_line_width(1)
        context.set_color((0, 0, 0))
        context.move_to(0, 0.5)
        context.line_to(context.width, 0.5)
        context.stroke()

    def layout_left(self, layout_manager):
        surface = ImageSurface(self.thumbnail)
        return cellpack.Padding(surface, 10, 10, 10, 10)

    def layout_right(self, layout_manager):
        alignment_kwargs = dict(
            xalign=0.5,
            xscale=0,
            yalign=0.5,
            yscale=0,
            min_width=80)
        if self.status == 'finished':
            return cellpack.Alignment(self.completed, **alignment_kwargs)
        elif self.status == 'error':
            return cellpack.Alignment(self.error, **alignment_kwargs)
        else:
            return cellpack.Alignment(self.delete_off, **alignment_kwargs)

    def layout_bottom(self, layout_manager):
        layout_manager.set_text_color(TEXT_COLOR)
        if self.status in ('converting', 'staging'):
            box = cellpack.HBox(spacing=5)
            box.pack(cellpack.Alignment(self.progressbar_base,
                                        xscale=0, yscale=0))
            textbox = layout_manager.textbox("%d%%" % (
                        100 * self.progress / self.duration))
            box.pack(textbox)
            return box
        elif self.status == 'initialized': # queued
            box = cellpack.HBox(spacing=5)
            box.pack(cellpack.Alignment(self.queued))
            box.pack(layout_manager.textbox("Queued"))
            return box
        elif self.status == 'finished':
            vbox = cellpack.VBox(spacing=10)
            top = cellpack.HBox(spacing=5)
            top.pack(cellpack.Alignment(self.showfile, xscale=0, yscale=0))
            top.pack(layout_manager.textbox("Show File"))
            top.pack(cellpack.Alignment(self.clear, xscale=0, yscale=0))
            top.pack(layout_manager.textbox("Clear"))
            vbox.pack(top)
            bottom = cellpack.HBox(spacing=5)
            bottom.pack(cellpack.Alignment(self.converted_to,
                                           xscale=0, yscale=0))
            layout_manager.set_text_color(TEXT_INFO)
            bottom.pack(layout_manager.textbox("Converted to 1034Mb"))
            vbox.pack(bottom)
            return vbox


class Application(mvc.Application):

    def startup(self):
        if self.started:
            return

        self.current_converter = EMPTY_CONVERTER

        mvc.Application.startup(self)

        self.window = Window("Miro Video Converter")
        self.window.connect('destroy', self.destroy)

        # # table on top
        self.model = ConversionModel()
        self.table = TableView(self.model)

        c = TableColumn("Data", ConversionCellRenderer(),
                        **dict((n, v) for (v, n) in enumerate((
                        'input', 'output', 'converter', 'status',
                        'duration', 'progress', 'eta', 'thumbnail'))))
        c.set_min_width(300)
        self.table.add_column(c)
        self.table.set_size_request(0, -1)

        if True:
            self.model.append([
                    'Super_Bowl_XLVI_New_York_Giants_very_long_output_title.avi',
                    '/home/z3p/',
                    'conv',
                    'finished',
                    100,
                    100,
                    0,
                    Image.from_file(image_path('audio.png'))])

            self.model.append([
                    'Big_buck_bunny_original.avi',
                    '/home/z3p/',
                    'conv',
                    'error',
                    0,
                    0,
                    0,
                    Image.from_file(image_path('audio.png'))])

            self.model.append([
                    'LouisCK_1024x800.avi',
                    '/home/z3p/',
                    'conv',
                    'converting',
                    100.0,
                    64.0,
                    0,
                    Image.from_file(image_path('audio.png'))])

            self.model.append([
                    'JimmyFallon_21_01_2012.flv',
                    '/home/z3p/',
                    'conv',
                    'initialized',
                    0,
                    0,
                    0,
                    Image.from_file(image_path('audio.png'))])

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


        self.drop_target = FileDropTarget()
        self.drop_target.connect('file-activated', self.file_activated)
        self.drop_target.set_size_request(-1, 70)

        # # finish up
        vbox = VBox()
        self.scroller = Scroller(vertical=True)
        #scroller.add(self.table)
        self.scroller.set_size_request(0, -1)
        vbox.pack_start(self.scroller)
        vbox.pack_start(self.drop_target, expand=True)
        vbox.pack_start(bottom)

        self.convert_button = Button("Start Conversions!")
        self.convert_button.disable()
        self.convert_button.connect('clicked', self.convert)
        alignment = Alignment(xalign=0.5, yalign=0.5,
                              top_pad=50, bottom_pad=50,
                              left_pad=20, right_pad=50)
        alignment.add(self.convert_button)
        vbox.pack_start(alignment)

        self.window.add(vbox)

        idle_add(self.conversion_manager.check_notifications)

        self.window.set_size_request(460, 600)

        self.window.connect('file-drag-motion', self.drag_motion)
        self.window.connect('file-drag-received', self.drag_data_received)
        self.window.connect('file-drag-leave', self.drag_finished)
        self.window.accept_file_drag(True)

        self.window.show()
        self.update_table_size()

    def drag_finished(self, widget):
        self.drop_target.set_in_drag(False)

    def drag_motion(self, widget):
        self.drop_target.set_in_drag(True)

    def drag_data_received(self, widget, values):
        for uri in values:
            parsed = urlparse.urlparse(uri)
            if parsed.scheme == 'file':
                pathname = urllib.url2pathname(parsed.path)
                self.file_activated(widget, pathname)

    def destroy(self, widget):
        for conversion in self.conversion_manager.in_progress.copy():
            conversion.stop()
        mainloop_stop()

    def run(self):
        mainloop_start()

    def update_convert_button(self):
        can_cancel = False
        can_start = False
        for c in self.model.conversions():
            if c.status == 'converting':
                can_cancel = True
                break
            elif c.status == 'initialized':
                can_start = True
        if (self.current_converter is EMPTY_CONVERTER or not
            (can_cancel or can_start)):
            self.convert_button.disable()
        else:
            self.convert_button.enable()
        if can_cancel:
            self.convert_button.set_label('Cancel Conversions')
        else:
            self.convert_button.set_label('Start Conversions!')

    def file_activated(self, widget, filename):
        vf = VideoFile(filename)
        c = self.conversion_manager.get_conversion(vf,
                                                   self.current_converter)
        c.listen(self.update_conversion)
        self.update_conversion(c)

    def change_conversion(self, widget):
        if hasattr(self, '_doing_conversion_change'):
            return
        self._doing_conversion_change = True

        identifier = widget.get_selected()
        if identifier is not None:
            self.current_converter = self.converter_manager.get_by_id(
                identifier)
        else:
            self.current_converter = EMPTY_CONVERTER

        for c in self.model.conversions():
            if c.status == 'initialized':
                c.set_converter(self.current_converter)
                self.model.update_conversion(c)

        self.update_convert_button()

        for menu in self.menus:
            if menu is not widget:
                menu.set_selected(0)

        del self._doing_conversion_change

    def convert(self, widget):
        if not self.conversion_manager.running:
            for conversion in self.model.conversions():
                if conversion.status == 'initialized':
                    self.conversion_manager.run_conversion(conversion)
            self.update_convert_button()
        else:
            for conversion in self.model.conversions():
                conversion.stop()

    def update_conversion(self, conversion):
        self.model.update_conversion(conversion)
        self.update_convert_button()

    def update_table_size(self):
        conversions = len(self.model)
        if not conversions:
            self.scroller.set_child(None)
            self.drop_target.set_small(False)
        else:
            height = 94 * conversions
            self.scroller.set_child(self.table)
            self.table.set_size_request(-1, min(height, 320))
            self.drop_target.set_small(True)

if __name__ == "__main__":
    initialize()
    app = Application()
    app.startup()
    app.run()



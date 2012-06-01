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

from mvc.widgets import initialize, idle_add, mainloop_start, mainloop_stop
from mvc.widgets import widgetset
from mvc.widgets import cellpack
from mvc.widgets import widgetutil

from mvc.converter import ConverterInfo
from mvc.video import VideoFile
from mvc.resources import image_path

LARGE_FONT = 13.0 / 13.0
SMALL_FONT = 10.0 / 13.0


GRADIENT_TOP = widgetutil.css_to_color('#585f63')
GRADIENT_BOTTOM = widgetutil.css_to_color('#383d40')

DRAG_AREA = widgetutil.css_to_color('#2b2e31')

TEXT_DISABLED = widgetutil.css_to_color('#333333')
TEXT_ACTIVE = widgetutil.css_to_color('#ffffff')
TEXT_INFO = widgetutil.css_to_color('#808080')
TEXT_COLOR = widgetutil.css_to_color('#ffffff')

class FileDropTarget(widgetset.SolidBackground):

    dropoff_on = widgetset.ImageDisplay(widgetset.Image(
            image_path("dropoff-icon-on.png")))
    dropoff_off = widgetset.ImageDisplay(widgetset.Image(
            image_path("dropoff-icon-off.png")))
    dropoff_small_on = widgetset.ImageDisplay(widgetset.Image(
            image_path("dropoff-icon-small-on.png")))
    dropoff_small_off = widgetset.ImageDisplay(widgetset.Image(
            image_path("dropoff-icon-small-off.png")))

    def __init__(self):
        super(FileDropTarget, self).__init__()
        self.set_background_color(DRAG_AREA)
        self.alignment = widgetset.Alignment(
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
        normal = widgetset.VBox(spacing=20)
        normal.pack_start(widgetutil.align_center(self.dropoff_on))
        normal.pack_start(widgetutil.align_center(widgetset.Label(
                    "Drag videos here or <a href=''>Choose File...</a>",
                    markup=True,
                    color=TEXT_COLOR)))

        drag = widgetset.VBox(spacing=20)
        drag.pack_start(widgetutil.align_center(self.dropoff_off))
        drag.pack_start(widgetutil.align_center(
                widgetset.Label("Release button to drop off",
                      color=TEXT_COLOR)))
        return normal, drag

    def build_small_widgets(self):
        normal = widgetset.HBox(spacing=10)
        normal.pack_start(widgetutil.align_middle(self.dropoff_small_on))
        normal.pack_start(widgetutil.align_middle(widgetset.Label(
                    "Drag more videos here or <a href=''>Choose File...</a>",
                    markup=True,
                    color=TEXT_COLOR)))

        drag = widgetset.HBox(spacing=10)
        drag.pack_start(widgetutil.align_middle(self.dropoff_small_off))
        drag.pack_start(widgetutil.align_middle(
                widgetset.Label("Release button to drop off",
                      color=TEXT_COLOR)))
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
            self.queue_redraw()

    def choose_file(self, widget):
        dialog = widgetset.FileChooserDialog('Choose File...')
        if dialog.run():
            for filename in dialog.get_filenames():
                self.emit('file-activated', filename)
        dialog.destroy()


class BottomBackground(widgetset.SolidBackground):

    def __init__(self):
        super(BottomBackground, self).__init__(color=GRADIENT_BOTTOM)

    # def draw(self, context, layout_manager):
    #     gradient = Gradient(0, 0, 0, context.height)
    #     gradient.set_start_color(GRADIENT_TOP)
    #     gradient.set_end_color(GRADIENT_BOTTOM)
    #     context.rectangle(0, 0, context.width, context.height)
    #     context.gradient_fill(gradient)


EMPTY_CONVERTER = ConverterInfo("")


class ConversionModel(widgetset.TableModel):
    def __init__(self):
        super(ConversionModel, self).__init__(
            'text', # filename
            'text', # output
            'text', # converter
            'text', # status
            'numeric', # duration
            'numeric', # progress
            'numeric', # eta,
            'object', # image
            )
        self.conversion_to_iter = {}
        self.thumbnail_to_image = {}

    def conversions(self):
        return iter(self.conversion_to_iter)

    def get_image(self, path):
        if path not in self.thumbnail_to_image:
            self.thumbnail_to_image[path] = widgetset.Image(path)
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
            self.conversion_to_iter[conversion] = self.append(*values)
        else:
            self.update(iter_, *values)


class IconHotspot(cellpack.Hotspot):

    def __init__(self, name, icon, textbox):
        box = cellpack.HBox(spacing=5)
        box.pack(cellpack.Alignment(icon, xscale=0, yscale=0))
        box.pack(textbox)
        super(IconHotspot, self).__init__(name, box)


class ConversionCellRenderer(widgetset.CustomCellRenderer):

    clear = widgetset.ImageSurface(widgetset.Image(
            image_path("clear-icon.png")))
    converted_to = widgetset.ImageSurface(widgetset.Image(
            image_path("converted_to-icon.png")))
    queued = widgetset.ImageSurface(widgetset.Image(
            image_path("queued-icon.png")))
    showfile = widgetset.ImageSurface(widgetset.Image(
            image_path("showfile-icon.png")))
    progressbar_base = widgetset.ImageSurface(widgetset.Image(
            image_path("progressbar-base.png")))
    delete_on = widgetset.ImageSurface(widgetset.Image(
            image_path("item-delete-button-on.png")))
    delete_off = widgetset.ImageSurface(widgetset.Image(
            image_path("item-delete-button-off.png")))
    error = widgetset.ImageSurface(widgetset.Image(
            image_path("item-error.png")))
    completed = widgetset.ImageSurface(widgetset.Image(
            image_path("item-completed.png")))

    def __init__(self):
        super(ConversionCellRenderer, self).__init__()
        self.alignment = None

    def get_size(self, style, layout_manager):
        return 450, 90

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
        self.alignment = alignment

        background = cellpack.Background(alignment)
        background.set_callback(self.draw_background)
        background.render_layout(context)

    @staticmethod
    def draw_background(context, x, y, width, height):
        gradient = widgetset.Gradient(x, y + 1, x, height - 1)
        gradient.set_start_color(GRADIENT_TOP)
        gradient.set_end_color(GRADIENT_BOTTOM)
        context.rectangle(x, y + 1, width, height -1 )
        context.gradient_fill(gradient)
        context.set_line_width(1)
        context.set_color((0, 0, 0))
        context.move_to(0, 0.5)
        context.line_to(context.width, 0.5)
        context.stroke()

    def draw_progressbar(self, context, x, y, _, height, width):
        # We're only drawing a certain amount of width, not however much we're
        # allocated.  So, we ignore the passed-in width and just use what we
        # set in layout_bottom.
        widgetutil.circular_rect(context, x, y, width-1, height-1)
        context.set_color((1, 1, 1))
        context.fill()

    def layout_left(self, layout_manager):
        surface = widgetset.ImageSurface(self.thumbnail)
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
            stack = cellpack.Stack()
            stack.pack(cellpack.Alignment(self.progressbar_base,
                                          xscale=0, yscale=0))
            percent = self.progress / self.duration
            width = int(percent * self.progressbar_base.width)
            stack.pack(cellpack.DrawingArea(
                    width, self.progressbar_base.height,
                    self.draw_progressbar, width))
            box.pack(cellpack.Alignment(stack,
                                        xscale=0, yscale=0))
            textbox = layout_manager.textbox("%d%%" % (
                        100 * percent))
            box.pack(textbox)
            return box
        elif self.status == 'initialized': # queued
            box = cellpack.HBox(spacing=5)
            box.pack(cellpack.Alignment(self.queued))
            box.pack(layout_manager.textbox("Queued"))
            return box
        elif self.status in ('finished', 'error'):
            vbox = cellpack.VBox(spacing=10)
            top = cellpack.HBox(spacing=5)
            if self.status == 'finished':
                top.pack(IconHotspot('show-file', self.showfile,
                                     layout_manager.textbox('Show File')))
            top.pack(IconHotspot('clear', self.showfile,
                                 layout_manager.textbox('Clear')))
            vbox.pack(top)
            if self.status == 'finished':
                bottom = cellpack.HBox(spacing=5)
                bottom.pack(cellpack.Alignment(self.converted_to,
                                               xscale=0, yscale=0))
                layout_manager.set_text_color(TEXT_INFO)
                bottom.pack(layout_manager.textbox("Converted to 1034Mb"))
                vbox.pack(bottom)
            return vbox

    def hotspot_test(self, style, layout_manager, x, y, width, height):
        if self.alignment is None:
            return
        hotspot_info = self.alignment.find_hotspot(x, y, width, height)
        if hotspot_info:
            print 'HOTSPOT INFO', hotspot_info
            return hotspot_info[0]

class ConvertButton(widgetset.CustomButton):
    off = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-off.png")))
    on = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-on.png")))
    stop = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-stop.png")))

    def __init__(self):
        super(ConvertButton, self).__init__()
        self.set_off()

    def set_on(self):
        self.label = 'Start Conversions!'
        self.image = self.on
        self.queue_redraw()

    def set_off(self):
        self.label = 'Start Conversions!'
        self.image = self.off
        self.queue_redraw()

    def set_stop(self):
        self.label = 'Stop Conversions'
        self.image = self.stop
        self.queue_redraw()

    def size_request(self, layout_manager):
        return self.off.width, self.off.height

    def draw(self, context, layout_manager):
        x = (context.width - self.image.width) // 2
        y = (context.height - self.image.height) // 2
        self.image.draw(context, x, y, self.image.width, self.image.height)
        if self.image == self.off:
            layout_manager.set_text_color(TEXT_DISABLED)
        else:
            layout_manager.set_text_color(TEXT_ACTIVE)
        textbox = layout_manager.textbox(self.label)
        alignment = cellpack.Alignment(textbox, xalign=0.5, xscale=0.0,
                                       yalign=0.5, yscale=0)
        alignment.render_layout(context)


class Application(mvc.Application):

    def startup(self):
        if self.started:
            return

        self.current_converter = EMPTY_CONVERTER

        mvc.Application.startup(self)

        self.window = widgetset.Window("Miro Video Converter")
        self.window.connect('will-close', self.destroy)

        # # table on top
        self.model = ConversionModel()
        self.table = widgetset.TableView(self.model)
        self.table.set_row_spacing(0)
        self.table.set_fixed_height(True)
        self.table.set_grid_lines(False, False)
        self.table.set_show_headers(False)

        c = widgetset.TableColumn("Data", ConversionCellRenderer(),
                        **dict((n, v) for (v, n) in enumerate((
                        'input', 'output', 'converter', 'status',
                        'duration', 'progress', 'eta', 'thumbnail'))))
        c.set_min_width(450)
        self.table.add_column(c)

        # bottom buttons
        converter_types = ('apple', 'android', 'other', 'format')
        converters = {}
        for c in self.converter_manager.list_converters():
            media_type = c.media_type
            if media_type not in converter_types:
                media_type = 'others'
            converters.setdefault(media_type, []).append(c)

        self.menus = []
        buttons = widgetset.HBox()

        for type_ in converter_types:
            options = [(c.name, c.identifier) for c in
                       converters[type_]]
            options.sort()
            options.insert(0, (type_.title(), None))
            menu = widgetset.OptionMenu(options)
            menu.set_size_request(460 / len(converter_types), -1)
            menu.connect('changed', self.change_conversion)
            self.menus.append(menu)
            buttons.pack_start(menu)


        self.drop_target = FileDropTarget()
        self.drop_target.connect('file-activated', self.file_activated)
        self.drop_target.set_size_request(-1, 70)

        # # finish up
        vbox = widgetset.VBox()
        self.scroller = widgetset.Scroller(False, True)
        self.scroller.set_size_request(0, 0)
        self.scroller.add(self.table)
        vbox.pack_start(self.scroller)
        vbox.pack_start(self.drop_target, expand=True)

        bottom = BottomBackground()
        bottom_box = widgetset.VBox()
        bottom_box.pack_start(buttons)


        self.convert_button = ConvertButton()
        self.convert_button.connect('clicked', self.convert)

        bottom_box.pack_start(widgetutil.align(self.convert_button,
                                         xalign=0.5, yalign=0.5,
                                         top_pad=50, bottom_pad=50))
        bottom.set_child(bottom_box)
        vbox.pack_start(bottom)
        self.window.set_content_widget(vbox)

        idle_add(self.conversion_manager.check_notifications)

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
            self.convert_button.set_off()
        else:
            self.convert_button.set_on()
        if can_cancel:
            self.convert_button.set_stop()

    def file_activated(self, widget, filename):
        vf = VideoFile(filename)
        c = self.conversion_manager.get_conversion(vf,
                                                   self.current_converter)
        c.listen(self.update_conversion)
        self.update_conversion(c)
        self.update_table_size()

    def change_conversion(self, widget, index):
        if hasattr(self, '_doing_conversion_change'):
            return
        self._doing_conversion_change = True

        identifier = widget.options[index][1]
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
        self.table.model_changed()
        self.update_convert_button()

    def update_table_size(self):
        conversions = len(self.model)
        total_height = 385
        if not conversions:
            self.drop_target.set_small(False)
            self.drop_target.set_size_request(-1, total_height)
        else:
            height = min(94 * conversions, 320)
            self.scroller.set_size_request(-1, height)
            self.drop_target.set_small(True)
            self.drop_target.set_size_request(-1, total_height - height)

if __name__ == "__main__":
    initialize()
    app = Application()
    app.startup()
    app.run()





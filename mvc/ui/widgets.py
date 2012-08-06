import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os.path

try:
    import mvc
except ImportError:
    import os.path, sys
    mvc_path = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.append(mvc_path)
    import mvc

import copy
import tempfile
import urllib
import urlparse

from mvc.widgets import (initialize, idle_add, mainloop_start, mainloop_stop,
                         reveal_file)
from mvc.widgets import widgetset
from mvc.widgets import cellpack
from mvc.widgets import widgetconst
from mvc.widgets import widgetutil

from mvc.converter import ConverterInfo
from mvc.video import VideoFile
from mvc.resources import image_path
from mvc.utils import size_string, round_even

BUTTON_FONT = 15.0 / 13.0
LARGE_FONT = 13.0 / 13.0
SMALL_FONT = 10.0 / 13.0

DEFAULT_FONT="Helvetica"

GRADIENT_TOP = widgetutil.css_to_color('#585f63')
GRADIENT_BOTTOM = widgetutil.css_to_color('#383d40')

DRAG_AREA = widgetutil.css_to_color('#2b2e31')

TEXT_DISABLED = widgetutil.css_to_color('#333333')
TEXT_ACTIVE = widgetutil.css_to_color('#ffffff')
TEXT_CLICKED = widgetutil.css_to_color('#cccccc')
TEXT_INFO = widgetutil.css_to_color('#808080')
TEXT_COLOR = widgetutil.css_to_color('#ffffff')
TEXT_SHADOW = widgetutil.css_to_color('#000000')

TABLE_WIDTH, TABLE_HEIGHT = 450, 87

# app singleton
app = None

class CustomLabel(widgetset.Background):
    def __init__(self, text=''):
        widgetset.Background.__init__(self)
        self.text = text
        self.font = None
        self.color = TEXT_COLOR

    def set_text(self, text):
        self.text = text
        self.queue_redraw()

    def set_color(self, color):
        self.color = color
        self.queue_redraw()

    def set_font(self, font):
        self.font = font
        self.queue_redraw()

    def textbox(self, layout_manager):
        layout_manager.set_text_color(self.color)
        layout_manager.set_font(LARGE_FONT, family=self.font)
        return layout_manager.textbox(self.text)

    def draw(self, context, layout_manager):
        layout_manager.set_text_color(self.color)
        layout_manager.set_font(LARGE_FONT, family=self.font)
        textbox = self.textbox(layout_manager)
        size = textbox.get_size()
        textbox.draw(context, 0, (context.height - size[1]) // 2,
                     context.width, context.height)

    def size_request(self, layout_manager):
        return self.textbox(layout_manager).get_size()

class ChooseFileButton(widgetset.CustomButton):

    def __init__(self):
        super(ChooseFileButton, self).__init__()
        self.set_cursor(widgetconst.CURSOR_POINTING_HAND)

    def textbox(self, layout_manager):
        return layout_manager.textbox('Choose Files...', underline=True)

    def size_request(self, layout_manager):
        textbox = self.textbox(layout_manager)
        return textbox.get_size()

    def draw(self, context, layout_manager):
        layout_manager.set_text_color(TEXT_COLOR)
        layout_manager.set_font(LARGE_FONT, family=DEFAULT_FONT)
        textbox = self.textbox(layout_manager)
        size = textbox.get_size()
        textbox.draw(context, 0, (context.height - size[1]) // 2,
                     context.width, context.height)

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
        height = 40 # arbitrary, but the same for both
        normal = widgetset.VBox(spacing=20)
        normal.pack_start(widgetutil.align_center(self.dropoff_off,
                                                  top_pad=60))
        label = CustomLabel("Drag videos here or")
        label.set_color(TEXT_COLOR)
        label.set_font(DEFAULT_FONT)
        hbox = widgetset.HBox(spacing=4)
        hbox.pack_start(widgetutil.align_middle(label))

        cfb = ChooseFileButton()
        cfb.connect('clicked', self.choose_file)
        hbox.pack_start(widgetutil.align_middle(cfb))
        hbox.set_size_request(-1, height)
        normal.pack_start(hbox)

        drag = widgetset.VBox(spacing=20)
        drag.pack_start(widgetutil.align_center(self.dropoff_on,
                                                top_pad=60))
        hbox = widgetset.HBox(spacing=4)
        hbox.pack_start(widgetutil.align_center(
                widgetset.Label("Release button to drop off",
                      color=TEXT_COLOR)))
        hbox.set_size_request(-1, height)
        drag.pack_start(hbox)
        return normal, drag

    def build_small_widgets(self):
        height = 40 # arbitrary, but the same for both
        normal = widgetset.HBox(spacing=4)
        normal.pack_start(widgetutil.align_middle(self.dropoff_small_off,
                                                  right_pad=7))
        drag_label = CustomLabel('Drag more videos here or')
        drag_label.set_font(DEFAULT_FONT)
        drag_label.set_color(TEXT_COLOR)
        normal.pack_start(widgetutil.align_middle(drag_label))
        cfb = ChooseFileButton()
        cfb.connect('clicked', self.choose_file)
        normal.pack_start(cfb)
        normal.set_size_request(-1, height)

        drop_label = CustomLabel('Release button to drop off')
        drop_label.set_font(DEFAULT_FONT)
        drop_label.set_color(TEXT_COLOR)
        drag = widgetset.HBox(spacing=10)
        drag.pack_start(widgetutil.align_middle(self.dropoff_small_on))
        drag.pack_start(widgetutil.align_middle(drop_label))
        drag.set_size_request(-1, height)

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
        dialog = widgetset.FileOpenDialog('Choose Files...')
        dialog.set_select_multiple(True)
        if dialog.run() == 0: # success
            for filename in dialog.get_filenames():
                self.emit('file-activated', filename)
        dialog.destroy()

BUTTON_BACKGROUND = widgetutil.ThreeImageSurface('settings-base')

class SettingsButton(widgetset.CustomButton):

    arrow_on = widgetset.ImageSurface(widgetset.Image(
            image_path('arrow-down-on.png')))
    arrow_off = widgetset.ImageSurface(widgetset.Image(
            image_path('arrow-down-off.png')))

    def __init__(self, name):
        super(SettingsButton, self).__init__()
        if name != 'settings':
            self.name = name.title()
        else:
            self.name = None
        self.selected = False
        if name != 'format':
            self.surface_on = widgetset.ImageSurface(widgetset.Image(
                    image_path('%s-icon-on.png' % name)))
            self.surface_off = widgetset.ImageSurface(widgetset.Image(
                    image_path('%s-icon-off.png' % name)))
        else:
            self.surface_on = self.surface_off = None

    def textbox(self, layout_manager):
        layout_manager.set_font(LARGE_FONT, family=DEFAULT_FONT)
        return layout_manager.textbox(self.name)

    def size_request(self, layout_manager):
        hbox = self.build_hbox(layout_manager)
        size = hbox.get_size()
        return size[0] + 2, size[1] + 2 # padding

    def build_hbox(self, layout_manager):
        hbox = cellpack.HBox(spacing=5)
        if self.selected:
            image = self.surface_on
            arrow = self.arrow_on
            layout_manager.set_text_color(TEXT_ACTIVE)
        else:
            image = self.surface_off
            arrow = self.arrow_off
            layout_manager.set_text_color(TEXT_DISABLED)
        if image:
            hbox.pack(cellpack.Alignment(image, xscale=0, yscale=0,
                                         yalign=0.5))
        if self.name:
            textbox = self.textbox(layout_manager)
            hbox.pack(cellpack.Alignment(textbox, yscale=0, yalign=0.5),
                      expand=True)
        a = cellpack.Alignment(arrow, xscale=0, yscale=0, yalign=0.5)
        hbox.pack(cellpack.Padding(a, left=5, right=12))
        alignment = cellpack.Padding(hbox, left=5)
        return alignment

    def draw(self, context, layout_manager):
        BUTTON_BACKGROUND.draw(context, 1, 1, context.width - 2)
        alignment = self.build_hbox(layout_manager)
        padding = cellpack.Padding(alignment, top=1, right=3, bottom=1, left=3)
        padding.render_layout(context)

    def set_selected(self, selected):
        self.selected = selected
        self.queue_redraw()


class OptionMenuBackground(widgetset.Background):

    surface = widgetutil.ThreeImageSurface('settings-depth')

    def size_request(self, layout_manager):
        return 1, self.surface.height

    def draw(self, context, layout_manager):
        child_width = self.child.get_size_request()[0]
        self.surface.draw(context, 0, 0, child_width)


class BottomBackground(widgetset.Background):

    def draw(self, context, layout_manager):
        gradient = widgetset.Gradient(0, 0, 0, context.height)
        gradient.set_start_color(GRADIENT_TOP)
        gradient.set_end_color(GRADIENT_BOTTOM)
        context.rectangle(0, 0, context.width, context.height)
        context.gradient_fill(gradient)


class LabeledNumberEntry(widgetset.HBox):

    def __init__(self, label):
        super(LabeledNumberEntry, self).__init__(spacing=5)
        self.label = widgetset.Label(label, color=TEXT_COLOR)
        self.label.set_size(widgetconst.SIZE_SMALL)
        self.entry = widgetset.NumberEntry()
        self.entry.set_size_request(50, 20)
        self.pack_start(self.label)
        self.pack_start(self.entry)
        self.entry.connect('focus-out', lambda x: self.emit('focus-out'))

    def get_text(self):
        return self.entry.get_text()

    def set_text(self, text):
        self.entry.set_text(text)


class CustomOptions(widgetset.Background):

    background = widgetset.ImageSurface(widgetset.Image(
            image_path('settings-dropdown-bottom-bg.png')))

    def __init__(self):
        super(CustomOptions, self).__init__()
        self.create_signal('setting-changed')
        self.reset()

    def reset(self):
        self.top = self.create_top()
        self.top.set_size_request(390, 50)
        self.left = self.create_left()
        self.left.set_size_request(212, 70)
        self.right = self.create_right()
        self.right.set_size_request(178, 70)
        vbox = widgetset.VBox()
        vbox.pack_start(self.top)
        hbox = widgetset.HBox()
        hbox.pack_start(self.left)
        hbox.pack_start(self.right)
        vbox.pack_start(hbox)

        self.box = widgetutil.align_left(vbox)

        self.options = {
            'destination': None,
            'custom-size': False,
            'width': None,
            'height': None,
            'custom-aspect': False,
            'aspect-ratio': None
            }
        if self.child:
            self.set_child(self.box)

    def create_top(self):
        hbox = widgetset.HBox(spacing=5)
        hbox.pack_start(widgetset.Label('Save to', color=TEXT_COLOR))
        button = widgetset.Button('Current Video Location')
        button.connect('clicked', self.on_destination_clicked)
        hbox.pack_start(button)
        return widgetutil.align_center(hbox, top_pad=10, bottom_pad=10)

    def create_left(self):
        custom_size = widgetset.Checkbox('Custom Size', color=TEXT_COLOR)
        custom_size.set_size(widgetconst.SIZE_SMALL)
        custom_size.connect('toggled', self.on_custom_size_changed)

        bottom = widgetset.HBox(spacing=5)
        self.width_widget = LabeledNumberEntry('Width')
        self.width_widget.connect('focus-out', self.on_width_height_changed)
        self.width_widget.disable()
        self.height_widget = LabeledNumberEntry('Height')
        self.height_widget.connect('focus-out', self.on_width_height_changed)
        self.height_widget.disable()
        bottom.pack_start(self.width_widget)
        bottom.pack_start(self.height_widget)

        vbox = widgetset.VBox(spacing=5)
        vbox.pack_start(widgetutil.align_left(custom_size, left_pad=10))
        vbox.pack_start(widgetutil.align_center(bottom))
        return widgetutil.align_middle(vbox)

    def create_right(self):
        aspect = widgetset.Checkbox('Custom Aspect Ratio', color=TEXT_COLOR)
        aspect.set_size(widgetconst.SIZE_SMALL)
        aspect.connect('toggled', self.on_aspect_changed)
        self.button_group = widgetset.RadioButtonGroup()
        b1 = widgetset.RadioButton('4:3', self.button_group, color=TEXT_COLOR)
        b2 = widgetset.RadioButton('3:2', self.button_group, color=TEXT_COLOR)
        b3 = widgetset.RadioButton('16:9', self.button_group, color=TEXT_COLOR)
        self.aspect_map = dict()
        self.aspect_map[b1] = (4, 3)
        self.aspect_map[b2] = (3, 2)
        self.aspect_map[b3] = (16, 9)
        hbox = widgetset.HBox(spacing=5)
        for button in self.button_group.get_buttons():
            button.disable()
            button.set_size(widgetconst.SIZE_SMALL)
            hbox.pack_start(button)
            button.connect('clicked', self.on_aspect_size_changed)

        vbox = widgetset.VBox()
        vbox.pack_start(widgetutil.align_center(aspect))
        vbox.pack_start(widgetutil.align_center(hbox))
        return widgetutil.align_middle(vbox)

    def draw(self, context, layout_manager):
        self.background.draw(context, 0, 0, self.background.width,
                             self.background.height)

    def update_setting(self, setting, value):
        self.options[setting] = value
        if setting == 'width':
            self.width_widget.set_text(str(value))
        elif setting == 'height':
            self.height_widget.set_text(str(value))

    def _change_setting(self, setting, value):
        self.options[setting] = value
        self.emit('setting-changed', setting, value)
        if setting == 'aspect-ratio' and self.options['custom-aspect']:
            width = self.width_widget.get_text()
            height = self.height_widget.get_text()
            if not (width and height):
                return
            if float(width) / float(height) != value:
                new_height = round_even(float(width) / value)
                if new_height != height:
                    self.update_setting('width', int(width))
                    self.update_setting('height', new_height)
                    self.emit('setting-changed', 'height', new_height)

    def show(self):
        self.set_child(self.box)
        self.set_size_request(self.background.width,
                              self.background.height + 28)
        self.queue_redraw()

    def hide(self):
        self.remove()
        self.set_size_request(0, 0)
        self.queue_redraw()

    def toggle(self):
        if self.child:
            self.hide()
        else:
            self.show()

    # signal handlers
    def on_destination_clicked(self, widget):
        dialog = widgetset.DirectorySelectDialog('Destination Directory')
        r = dialog.run()
        if r == 0: # picked a directory
            self._change_setting('destination', dialog.get_directory())
            if widget:
                widget.set_text(os.path.basename(dialog.get_directory()))
        else: # cancel
            self._change_setting('destination', None)
            if widget:
                widget.set_text('Current Video Location')

    def on_custom_size_changed(self, widget):
        self._change_setting('custom-size', widget.get_checked())
        if widget.get_checked():
            self.width_widget.enable()
            self.height_widget.enable()
        else:
            self.width_widget.disable()
            self.height_widget.disable()

    def on_width_height_changed(self, widget):
        if widget.get_text():
            value = int(widget.get_text())
        else:
            value = None
        if widget.label.get_text() == 'Width':
            setting = 'width'
        else:
            setting = 'height'
        self._change_setting(setting, value)

    def on_aspect_changed(self, widget):
        self._change_setting('custom-aspect', widget.get_checked())
        if widget.get_checked():
            for button in self.button_group.get_buttons():
                button.enable()
        else:
            for button in self.button_group.get_buttons():
                button.disable()

    def on_aspect_size_changed(self, widget):
        if widget.get_selected():
            width_ratio, height_ratio = [float(v) for v in
                                         self.aspect_map[widget]]
            ratio = width_ratio / height_ratio
            self._change_setting('aspect-ratio', ratio)

EMPTY_CONVERTER = ConverterInfo("")


class ConversionModel(widgetset.TableModel):
    def __init__(self):
        super(ConversionModel, self).__init__(
            'text', # filename
            'numeric', # output_size
            'text', # converter
            'text', # status
            'numeric', # duration
            'numeric', # progress
            'numeric', # eta,
            'object', # image
            'object', # the actual conversion
            )
        self.conversion_to_iter = {}
        self.thumbnail_to_image = {None: widgetset.Image(
                image_path('audio.png'))}

    def conversions(self):
        return iter(self.conversion_to_iter)

    def all_conversions_done(self):
        has_conversions = any(self.conversions())
        all_done = ((set(c.status for c in self.conversions()) -
                     set(['finished', 'failed'])) == set())
        return all_done and has_conversions

    def get_image(self, path):
        if path not in self.thumbnail_to_image:
            try:
                image = widgetset.Image(path)
            except ValueError:
                image = self.thumbnail_to_image[None]
            self.thumbnail_to_image[path] = image
        return self.thumbnail_to_image[path]

    def update_conversion(self, conversion):
        try:
            output_size = os.stat(conversion.output).st_size
        except OSError:
            output_size = 0
        values = (conversion.video.filename,
                  output_size,
                  conversion.converter.name,
                  conversion.status,
                  conversion.duration or 0,
                  conversion.progress or 0,
                  conversion.eta or 0,
                  self.get_image(conversion.video.get_thumbnail(90, 70)),
                  conversion
                  )
        iter_ = self.conversion_to_iter.get(conversion)
        if iter_ is None:
            self.conversion_to_iter[conversion] = self.append(*values)
        else:
            self.update(iter_, *values)

    def remove(self, iter_):
        conversion = self[iter_][-1]
        del self.conversion_to_iter[conversion]
        thumbnail_path = conversion.video.get_thumbnail(90, 70)
        if thumbnail_path:
            del self.thumbnail_to_image[thumbnail_path]
        return super(ConversionModel, self).remove(iter_)


class IconWithText(cellpack.HBox):

    def __init__(self, icon, textbox):
        super(IconWithText, self).__init__(spacing=5)
        self.pack(cellpack.Alignment(icon, yalign=0.5, xscale=0, yscale=0))
        self.pack(textbox)


class ConversionCellRenderer(widgetset.CustomCellRenderer):

    IGNORE_PADDING = True

    clear = widgetset.ImageSurface(widgetset.Image(
            image_path("clear-icon.png")))
    converted_to = widgetset.ImageSurface(widgetset.Image(
            image_path("converted_to-icon.png")))
    queued = widgetset.ImageSurface(widgetset.Image(
            image_path("queued-icon.png")))
    showfile = widgetset.ImageSurface(widgetset.Image(
            image_path("showfile-icon.png")))
    show_ffmpeg = widgetset.ImageSurface(widgetset.Image(
            image_path("error-icon.png")))
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
        return TABLE_WIDTH, TABLE_HEIGHT

    def render(self, context, layout_manager, selected, hotspot, hover):
        left_right = cellpack.HBox()
        top_bottom = cellpack.VBox()
        left_right.pack(self.layout_left(layout_manager))
        left_right.pack(top_bottom, expand=True)
        layout_manager.set_text_color(TEXT_COLOR)
        layout_manager.set_font(LARGE_FONT, bold=True, family=DEFAULT_FONT)
        title = layout_manager.textbox(os.path.basename(self.input))
        title.set_wrap_style('truncated-char')
        alignment = cellpack.Padding(cellpack.TruncatedTextLine(title),
                                     top=25)
        top_bottom.pack(alignment)
        layout_manager.set_font(SMALL_FONT, family=DEFAULT_FONT)

        bottom = self.layout_bottom(layout_manager, hotspot)
        if bottom is not None:
            top_bottom.pack(bottom)
        left_right.pack(self.layout_right(layout_manager, hotspot))

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

    def layout_right(self, layout_manager, hotspot):
        alignment_kwargs = dict(
            xalign=0.5,
            xscale=0,
            yalign=0.5,
            yscale=0,
            min_width=80)
        if self.status == 'finished':
            return cellpack.Alignment(self.completed, **alignment_kwargs)
        elif self.status == 'failed':
            return cellpack.Alignment(self.error, **alignment_kwargs)
        else:
            if hotspot == 'cancel':
                image = self.delete_on
            else:
                image = self.delete_off
            return cellpack.Alignment(cellpack.Hotspot('cancel',
                                                       image),
                                      **alignment_kwargs)

    def layout_bottom(self, layout_manager, hotspot):
        layout_manager.set_text_color(TEXT_COLOR)
        if self.status in ('converting', 'staging'):
            box = cellpack.HBox(spacing=5)
            stack = cellpack.Stack()
            stack.pack(cellpack.Alignment(self.progressbar_base,
                                          yalign=0.5,
                                          xscale=0, yscale=0))
            percent = self.progress / self.duration
            width = max(int(percent * self.progressbar_base.width),
                        5)
            stack.pack(cellpack.DrawingArea(
                    width, self.progressbar_base.height,
                    self.draw_progressbar, width))
            box.pack(cellpack.Alignment(stack,
                                        yalign=0.5,
                                        xscale=0, yscale=0))
            textbox = layout_manager.textbox("%d%%" % (
                        100 * percent))
            box.pack(textbox)
            return box
        elif self.status == 'initialized': # queued
            return IconWithText(self.queued, layout_manager.textbox("Queued"))
        elif self.status in ('finished', 'failed'):
            vbox = cellpack.VBox(spacing=5)
            top = cellpack.HBox(spacing=5)
            if self.status == 'finished':
                if hotspot == 'show-file':
                    layout_manager.set_text_color(TEXT_CLICKED)
                top.pack(cellpack.Hotspot('show-file', IconWithText(
                            self.showfile,
                            layout_manager.textbox('Show File'))))
            elif self.status == 'failed':
                color = TEXT_CLICKED if hotspot == 'show-log' else TEXT_COLOR
                layout_manager.set_text_color(color)
                # XXX Missing grey error icon
                top.pack(cellpack.Hotspot('show-log', IconWithText(
                         self.show_ffmpeg,
                         layout_manager.textbox('Error - Show FFmpeg Output'))))
            color = TEXT_CLICKED if hotspot == 'clear' else TEXT_COLOR
            layout_manager.set_text_color(color)
            top.pack(cellpack.Hotspot('clear', IconWithText(
                     self.showfile,
                     layout_manager.textbox('Clear'))))
            vbox.pack(top)
            if self.status == 'finished':
                layout_manager.set_text_color(TEXT_INFO)
                vbox.pack(IconWithText(
                        self.converted_to,
                        layout_manager.textbox("Converted to %s" % (
                                size_string(self.output_size)))))
            return vbox

    def hotspot_test(self, style, layout_manager, x, y, width, height):
        if self.alignment is None:
            return
        hotspot_info = self.alignment.find_hotspot(x, y, width, height)
        if hotspot_info:
            return hotspot_info[0]

class ConvertButton(widgetset.CustomButton):
    off = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-off.png")))
    clear = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-off.png")))
    on = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-on.png")))
    stop = widgetset.ImageSurface(widgetset.Image(
            image_path("convert-button-stop.png")))

    def __init__(self):
        super(ConvertButton, self).__init__()
        self.hidden = False
        self.set_off()

    def set_on(self):
        self.label = 'Convert to %s' % app.current_converter.name
        self.image = self.on
        self.set_cursor(widgetconst.CURSOR_POINTING_HAND)
        self.queue_redraw()

    def set_clear(self):
        self.label = 'Clear and Start Over'
        self.image = self.clear
        self.set_cursor(widgetconst.CURSOR_POINTING_HAND)
        self.queue_redraw()

    def set_off(self):
        self.label = 'Convert Now'
        self.image = self.off
        self.set_cursor(widgetconst.CURSOR_NORMAL)
        self.queue_redraw()

    def set_stop(self):
        self.label = 'Stop All Conversions'
        self.image = self.stop
        self.set_cursor(widgetconst.CURSOR_POINTING_HAND)
        self.queue_redraw()

    def hide(self):
        self.hidden = True
        self.invalidate_size_request()
        self.queue_redraw()

    def show(self):
        self.hidden = False
        self.invalidate_size_request()
        self.queue_redraw()

    def size_request(self, layout_manager):
        if self.hidden:
            return 0, 0
        return self.off.width, self.off.height + 100 # padding

    def draw(self, context, layout_manager):
        if self.hidden:
            return
        x = (context.width - self.image.width) // 2
        y = (context.height - self.image.height - 100) // 2 + 50
        self.image.draw(context, x, y, self.image.width, self.image.height)
        if self.image == self.off:
            layout_manager.set_font(BUTTON_FONT, family=DEFAULT_FONT)
            layout_manager.set_text_shadow(widgetutil.Shadow(TEXT_SHADOW,
                                                             0.5, (-1, -1), 0))
            layout_manager.set_text_color(TEXT_DISABLED)
        else:
            layout_manager.set_font(BUTTON_FONT, bold=True,
                                    family=DEFAULT_FONT)
            layout_manager.set_text_shadow(widgetutil.Shadow(TEXT_SHADOW,
                                                             0.5, (1, 1), 0))
            layout_manager.set_text_color(TEXT_ACTIVE)
        textbox = layout_manager.textbox(self.label)
        alignment = cellpack.Alignment(textbox, xalign=0.5, xscale=0.0,
                                       yalign=0.5, yscale=0)
        alignment.render_layout(context)

# XXX do we want to export this for general purpose use?
class TextDialog(widgetset.Dialog):
    def __init__(self, title, description, window):
        widgetset.Dialog.__init__(self, title, description)
        self.set_transient_for(window)
        self.add_button('OK')
        self.textbox = widgetset.MultilineTextEntry()
        self.textbox.set_editable(False)
        scroller = widgetset.Scroller(False, True)
        scroller.set_has_borders(True)
        scroller.add(self.textbox)
        scroller.set_size_request(400, 500)
        self.set_extra_widget(scroller)

    def set_text(self, text):
        self.textbox.set_text(text)

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
        self.table.draws_selection = False
        self.table.set_row_spacing(0)
        self.table.enable_album_view_focus_hack()
        self.table.set_fixed_height(True)
        self.table.set_grid_lines(False, False)
        self.table.set_show_headers(False)

        c = widgetset.TableColumn("Data", ConversionCellRenderer(),
                        **dict((n, v) for (v, n) in enumerate((
                        'input', 'output_size', 'converter', 'status',
                        'duration', 'progress', 'eta', 'thumbnail',
                        'conversion'))))
        c.set_min_width(450)
        self.table.add_column(c)
        self.table.connect('hotspot-clicked', self.hotspot_clicked)

        # bottom buttons
        converter_types = ('apple', 'android', 'other', 'format')
        converters = {}
        for c in self.converter_manager.list_converters():
            media_type = c.media_type
            if media_type not in converter_types:
                media_type = 'others'
            converters.setdefault(media_type, []).append(c)

        self.menus = []

        self.button_bar = widgetset.HBox()
        buttons = widgetset.HBox()

        for type_ in converter_types:
            options = [(c.name, c.identifier) for c in
                       converters[type_]]
            options.sort()
            menu = SettingsButton(type_)
            menu.connect('clicked', self.show_options_menu, options)
            self.menus.append(menu)
            buttons.pack_start(menu)
        omb = OptionMenuBackground()
        omb.set_child(widgetutil.pad(buttons, top=2, bottom=2,
                                     left=2, right=2))
        self.button_bar.pack_start(omb)

        self.settings_button = SettingsButton('settings')
        omb = OptionMenuBackground()
        omb.set_child(widgetutil.pad(self.settings_button, top=2,
                                     bottom=2, left=2, right=2))
        self.button_bar.pack_end(omb)

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
        self.convert_label = CustomLabel('Convert to')
        self.convert_label.set_font(DEFAULT_FONT)
        self.convert_label.set_color(TEXT_COLOR)
        bottom_box.pack_start(widgetutil.align_left(self.convert_label,
                                                    top_pad=10,
                                                    bottom_pad=10))
        bottom_box.pack_start(self.button_bar)

        self.options = CustomOptions()
        self.options.connect('setting-changed', self.on_setting_changed)
        self.settings_button.connect('clicked', self.on_settings_toggle)
        bottom_box.pack_start(widgetutil.align_right(self.options,
                                                     right_pad=5))

        self.convert_button = ConvertButton()
        self.convert_button.connect('clicked', self.convert)

        bottom_box.pack_start(widgetutil.align(self.convert_button,
                                         xalign=0.5, yalign=0.5))
        bottom.set_child(widgetutil.pad(bottom_box, left=20, right=20))
        vbox.pack_start(bottom)
        self.window.set_content_widget(vbox)

        idle_add(self.conversion_manager.check_notifications, 1)

        self.window.connect('file-drag-motion', self.drag_motion)
        self.window.connect('file-drag-received', self.drag_data_received)
        self.window.connect('file-drag-leave', self.drag_finished)
        self.window.accept_file_drag(True)

        self.window.center()
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

    def show_options_menu(self, widget, options):
        menu = widgetset.ContextMenu([
                (option, lambda x, i: self.on_select_converter(widget,
                                                               options[i][1]))
                for option, id_ in options])
        menu.popup()

    def update_convert_button(self):
        can_cancel = False
        can_start = False
        has_conversions = any(self.model.conversions())
        all_done = self.model.all_conversions_done()
        for c in self.model.conversions():
            if c.status == 'converting':
                can_cancel = True
                break
            elif c.status == 'initialized':
                can_start = True
        self.convert_label.set_color(TEXT_DISABLED)
        # Set the colors - all are enabled if all conversions complete, or
        # if we have conversions conversions but the converter has not yet
        # been set.
        # the converter has not been set.
        if ((self.current_converter is EMPTY_CONVERTER and has_conversions) or
          all_done):
            for m in self.menus:
                m.set_selected(True)
            self.settings_button.set_selected(True)
        if self.current_converter is EMPTY_CONVERTER:
            self.convert_label.set_text('Convert to')
        elif can_cancel:
            target = self.current_converter.name
            self.convert_label.set_text('Converting to %s' % target)
        elif can_start:
            target = self.current_converter.name
            self.convert_label.set_text('Will convert to %s' % target)
            self.convert_label.set_color(TEXT_ACTIVE)
        if all_done:
            self.convert_button.set_clear()
        elif (self.current_converter is EMPTY_CONVERTER or not
            (can_cancel or can_start)):
            self.convert_button.set_off()
        else:
            self.convert_button.set_on()
        if can_cancel:
            self.convert_button.set_stop()
            self.button_bar.disable()
        else:
            if has_conversions:
                self.button_bar.enable()
            else:
                self.button_bar.disable()

    def file_activated(self, widget, filename):
        filename = os.path.realpath(filename)
        for c in self.model.conversions():
            if c.video.filename == filename:
                logger.info('ignoring duplicate: %r', filename)
                return
        if self.options.options['destination'] is None:
            try:
                tempfile.TemporaryFile(dir=os.path.dirname(filename))
            except EnvironmentError:
                # can't write to the destination directory; ask for a new one
                self.options.on_destination_clicked(None)
        vf = VideoFile(filename)
        c = self.conversion_manager.get_conversion(
            vf,
            self.current_converter,
            output_dir=self.options.options['destination'])
        c.listen(self.update_conversion)
        if self.conversion_manager.running:
            # start running automatically if a conversion is already in
            # progress
            self.conversion_manager.run_conversion(c)
        self.update_conversion(c)
        self.update_table_size()

    def on_select_converter(self, widget, identifier):
        self.current_converter = self.converter_manager.get_by_id(
            identifier)
        self.options.reset()

        self.converter_changed(widget)

    def converter_changed(self, widget):
        if hasattr(self, '_doing_conversion_change'):
            return
        self._doing_conversion_change = True

        # If all conversions are done, then change the status of them back
        # to 'initialized'.
        #
        # XXX TODO: what happens if the state is 'failed'?  Should we reset?
        all_done = self.model.all_conversions_done()
        if all_done:
            for c in self.model.conversions():
                c.status = 'initialized'

        if self.current_converter is not EMPTY_CONVERTER:
            self.convert_label.set_text(
                'Will convert to %s' % self.current_converter.name)
        else:
            self.convert_label.set_text('Convert to')

        if hasattr(self.current_converter, 'width'):
            self.options.update_setting('width',
                                        self.current_converter.width)
            self.options.update_setting('height',
                                        self.current_converter.height)

        for c in self.model.conversions():
            if c.status == 'initialized':
                c.set_converter(self.current_converter)
                self.model.update_conversion(c)

        # We likely either reset the status or we've changed the conversion
        # output so let's just reload the table model.
        self.table.model_changed()

        self.update_convert_button()

        widget.set_selected(True)
        for menu in self.menus:
            if menu is not widget:
                menu.set_selected(False)

        del self._doing_conversion_change

    def convert(self, widget):
        if not self.conversion_manager.running:
            for conversion in self.model.conversions():
                if conversion.status == 'initialized':
                    self.conversion_manager.run_conversion(conversion)
            self.button_bar.disable()
            # all done: no conversion job should be running at this point
            all_done = self.model.all_conversions_done()
            if all_done:
                # take stuff off one by one from the list until we have none!
                # might not be very efficient.
                iter_ = self.model.first_iter()
                while iter_ is not None:
                    conversion = self.model[iter_][-1]
                    if conversion.status in ('finished',
                                             'failed',
                                             'initialized'):
                        try:
                            self.conversion_manager.remove(conversion)
                        except ValueError:
                            pass
                    iter_ = self.model.remove(iter_)
                self.update_table_size()
        else:
            for conversion in self.model.conversions():
                conversion.stop()
        self.update_convert_button()

    def update_conversion(self, conversion):
        self.model.update_conversion(conversion)
        self.update_convert_button()
        self.update_table_size()

    def update_table_size(self):
        conversions = len(self.model)
        total_height = 380
        if not conversions:
            self.scroller.set_size_request(-1, 0)
            self.drop_target.set_small(False)
            self.drop_target.set_size_request(-1, total_height)
        else:
            height = min(TABLE_HEIGHT * conversions, 320)
            self.scroller.set_size_request(-1, height)
            self.drop_target.set_small(True)
            self.drop_target.set_size_request(-1, total_height - height)
        self.update_convert_button()
        self.table.model_changed()

    def hotspot_clicked(self, widget, name, iter_):
        conversion = self.model[iter_][-1]
        if name == 'show-file':
            reveal_file(os.path.dirname(conversion.output))
        elif name == 'clear':
            self.model.remove(iter_)
            self.update_table_size()
        elif name == 'show-log':
            lines = ''.join(conversion.lines)
            d = TextDialog('Log', '', self.window)
            d.set_text(lines)
            try:
                d.run()
            finally:
                d.destroy()
        elif name == 'cancel':
            if conversion.status == 'initialized':
                self.model.remove(iter_)
                try:
                    self.conversion_manager.remove(conversion)
                except ValueError:
                    pass
                self.update_table_size()
            else:
                conversion.stop()

    def on_settings_toggle(self, widget):
        if not self.options.child:
            # hidden, going to show
            self.convert_button.hide()
        self.options.toggle()
        if not self.options.child:
            # was shown, not hidden
            self.convert_button.show()

    def on_setting_changed(self, widget, setting, value):
        if setting == 'destination':
            for c in self.model.conversions():
                if c.status == 'initialized':
                    if value is None:
                        c.output_dir = os.path.dirname(c.video.filename)
                    else:
                        c.output_dir = value
                    # update final path
                    c.set_converter(self.current_converter)
            return
        if self.current_converter.identifier != 'custom':
            if hasattr(self.current_converter, 'simple'):
                self.current_converter = self.current_converter.simple(
                    self.current_converter.name)
            else:
                self.current_converter = copy.copy(self.current_converter)
            self.current_converter.name = 'Custom'
            self.current_converter.width = self.options.options['width']
            self.current_converter.height = self.options.options['height']
            self.converter_changed(self.menus[-1]) # formats menu
        if setting in ('width', 'height'):
            setattr(self.current_converter, setting, value)
        elif setting == 'custom-size':
            if not value:
                self.current_converter.old_size = (
                    self.current_converter.width,
                    self.current_converter.height)
                self.current_converter.width = None
                self.current_converter.height = None
            elif hasattr(self.current_converter, 'old_size'):
                old_size = self.current_converter.old_size
                (self.current_converter.width,
                 self.current_converter.height) = old_size


if __name__ == "__main__":
    initialize()
    app = Application()
    app.startup()
    app.run()

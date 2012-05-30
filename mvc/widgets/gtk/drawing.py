import gtk
import cairo
from .base import BinMixin

def make_gdk_color(color):
    def convert_value(value):
        return int(round(value * 65535))

    values = tuple(convert_value(c) for c in color)
    return gtk.gdk.Color(*values)


def convert_gtk_color(color):
    return (color.red / 65535.0, color.green / 65535.0,
            color.blue / 65535.0)


class SolidBackground(BinMixin, gtk.EventBox):
    def __init__(self, color=None):
        super(SolidBackground, self).__init__()
        if color is not None:
            self.set_background_color(color)

    def make_color(self, color_value):
        color = make_gdk_color(color_value)
        self.get_colormap().alloc_color(color)
        return color

    def set_background_color(self, color):
        self.modify_base(gtk.STATE_NORMAL, self.make_color(color))
        self.modify_bg(gtk.STATE_NORMAL, self.make_color(color))


class ImageSurface:
    def __init__(self, image):
        format = cairo.FORMAT_RGB24
        if image.get_has_alpha():
            format = cairo.FORMAT_ARGB32
        self.image = cairo.ImageSurface(
            format, int(image.width), int(image.height))
        context = cairo.Context(self.image)
        gdkcontext = gtk.gdk.CairoContext(context)
        gdkcontext.set_source_pixbuf(image, 0, 0)
        gdkcontext.paint()
        self.pattern = cairo.SurfacePattern(self.image)
        self.pattern.set_extend(cairo.EXTEND_REPEAT)
        self.width = image.width
        self.height = image.height

    def get_size(self):
        return self.width, self.height

    def _align_pattern(self, x, y):
        """Line up our image pattern so that it's top-left corner is x, y."""
        m = cairo.Matrix()
        m.translate(-x, -y)
        self.pattern.set_matrix(m)

    def draw(self, context, x, y, width, height, fraction=1.0):
        self._align_pattern(x, y)
        cairo_context = context.context
        cairo_context.save()
        cairo_context.set_source(self.pattern)
        cairo_context.new_path()
        cairo_context.rectangle(x, y, width, height)
        if fraction >= 1.0:
            cairo_context.fill()
        else:
            cairo_context.clip()
            cairo_context.paint_with_alpha(fraction)
        cairo_context.restore()

    def draw_rect(self, context, dest_x, dest_y, source_x, source_y,
            width, height, fraction=1.0):

        self._align_pattern(dest_x-source_x, dest_y-source_y)
        cairo_context = context.context
        cairo_context.save()
        cairo_context.set_source(self.pattern)
        cairo_context.new_path()
        cairo_context.rectangle(dest_x, dest_y, width, height)
        if fraction >= 1.0:
            cairo_context.fill()
        else:
            cairo_context.clip()
            cairo_context.paint_with_alpha(fraction)
        cairo_context.restore()


class DrawingStyle(object):
    def __init__(self, widget, use_base_color=False, state=None):
        if state is None:
            state = widget.state
        self.style = widget.style
        self.text_color = convert_gtk_color(self.style.text[state])
        if use_base_color:
            self.bg_color = convert_gtk_color(self.style.base[state])
        else:
            self.bg_color = convert_gtk_color(self.style.bg[state])


class DrawingContext(object):
    """DrawingContext.  This basically just wraps a Cairo context and adds a
    couple convenience methods.
    """

    def __init__(self, window, drawing_area, expose_area):
        self.window = window
        self.context = window.cairo_create()
        self.context.rectangle(expose_area.x, expose_area.y, 
                expose_area.width, expose_area.height)
        self.context.clip()
        self.width = drawing_area.width
        self.height = drawing_area.height
        self.context.translate(drawing_area.x, drawing_area.y)

    def __getattr__(self, name):
        return getattr(self.context, name)

    def set_color(self, (red, green, blue), alpha=1.0):
        self.context.set_source_rgba(red, green, blue, alpha)

    def set_shadow(self, color, opacity, offset, blur_radius):
        pass

    def gradient_fill(self, gradient):
        old_source = self.context.get_source()
        self.context.set_source(gradient.pattern)
        self.context.fill()
        self.context.set_source(old_source)

    def gradient_fill_preserve(self, gradient):
        old_source = self.context.get_source()
        self.context.set_source(gradient.pattern)
        self.context.fill_preserve()
        self.context.set_source(old_source)


class Gradient(object):
    def __init__(self, x1, y1, x2, y2):
        self.pattern = cairo.LinearGradient(x1, y1, x2, y2)

    def set_start_color(self, (red, green, blue)):
        self.pattern.add_color_stop_rgb(0, red, green, blue)

    def set_end_color(self, (red, green, blue)):
        self.pattern.add_color_stop_rgb(1, red, green, blue)

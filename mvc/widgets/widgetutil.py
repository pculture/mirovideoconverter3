from math import pi as PI
from mvc.widgets import widgetset
from mvc.resources import image_path

def make_surface(image_name):
    path = image_path(image_name + '.png')
    return widgetset.ImageSurface(widgetset.Image(path))

def font_scale_from_osx_points(points):
    """Create a font scale so that it's points large on OS X.

    Assumptions (these should be true for OS X)
        - the default font size is 13pt
        - the DPI is 72ppi
    """
    return points / 13.0

def css_to_color(css_string):
    parts = (css_string[1:3], css_string[3:5], css_string[5:7])
    return tuple((int(value, 16) / 255.0) for value in parts)

def align(widget, xalign=0, yalign=0, xscale=0, yscale=0,
        top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Create an alignment, then add widget to it and return the alignment.
    """
    alignment = widgetset.Alignment(xalign, yalign, xscale, yscale,
                          top_pad, bottom_pad, left_pad, right_pad)
    alignment.add(widget)
    return alignment

def align_center(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will center it horizontally.
    """
    return align(widget, 0.5, 0, 0, 1,
            top_pad, bottom_pad, left_pad, right_pad)

def align_right(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align it left.
    """
    return align(widget, 1, 0, 0, 1, top_pad, bottom_pad, left_pad, right_pad)

def align_left(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align it right.
    """
    return align(widget, 0, 0, 0, 1, top_pad, bottom_pad, left_pad, right_pad)

def align_middle(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will center it vertically.
    """
    return align(widget, 0, 0.5, 1, 0,
            top_pad, bottom_pad, left_pad, right_pad)

def align_top(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align to the top.
    """
    return align(widget, 0, 0, 1, 0, top_pad, bottom_pad, left_pad, right_pad)

def align_bottom(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align to the bottom.
    """
    return align(widget, 0, 1, 1, 0, top_pad, bottom_pad, left_pad, right_pad)

def pad(widget, top=0, bottom=0, left=0, right=0):
    """Wrap a widget in an Alignment that will pad it.
    """
    alignment = widgetset.Alignment(0, 0, 1, 1,
                          top, bottom, left, right)
    alignment.add(widget)
    return alignment

def round_rect(context, x, y, width, height, edge_radius):
    """Specifies path of a rectangle with rounded corners.
    """
    edge_radius = min(edge_radius, min(width, height)/2.0)
    inner_width = width - edge_radius*2
    inner_height = height - edge_radius*2
    x_inner1 = x + edge_radius
    x_inner2 = x + width - edge_radius
    y_inner1 = y + edge_radius
    y_inner2 = y + height - edge_radius

    context.move_to(x+edge_radius, y)
    context.rel_line_to(inner_width, 0)
    context.arc(x_inner2, y_inner1, edge_radius, -PI/2, 0)
    context.rel_line_to(0, inner_height)
    context.arc(x_inner2, y_inner2, edge_radius, 0, PI/2)
    context.rel_line_to(-inner_width, 0)
    context.arc(x_inner1, y_inner2, edge_radius, PI/2, PI)
    context.rel_line_to(0, -inner_height)
    context.arc(x_inner1, y_inner1, edge_radius, PI, PI*3/2)

def round_rect_reverse(context, x, y, width, height, edge_radius):
    """Specifies path of a rectangle with rounded corners.

    This specifies the rectangle in a counter-clockwise fashion.
    """
    edge_radius = min(edge_radius, min(width, height)/2.0)
    inner_width = width - edge_radius*2
    inner_height = height - edge_radius*2
    x_inner1 = x + edge_radius
    x_inner2 = x + width - edge_radius
    y_inner1 = y + edge_radius
    y_inner2 = y + height - edge_radius

    context.move_to(x+edge_radius, y)
    context.arc_negative(x_inner1, y_inner1, edge_radius, PI*3/2, PI)
    context.rel_line_to(0, inner_height)
    context.arc_negative(x_inner1, y_inner2, edge_radius, PI, PI/2)
    context.rel_line_to(inner_width, 0)
    context.arc_negative(x_inner2, y_inner2, edge_radius, PI/2, 0)
    context.rel_line_to(0, -inner_height)
    context.arc_negative(x_inner2, y_inner1, edge_radius, 0, -PI/2)
    context.rel_line_to(-inner_width, 0)

def circular_rect(context, x, y, width, height):
    """Make a path for a rectangle with the left/right side being circles.
    """
    radius = height / 2.0
    inner_width = width - height
    inner_y = y + radius
    inner_x1 = x + radius
    inner_x2 = inner_x1 + inner_width

    context.move_to(inner_x1, y)
    context.rel_line_to(inner_width, 0)
    context.arc(inner_x2, inner_y, radius, -PI/2, PI/2)
    context.rel_line_to(-inner_width, 0)
    context.arc(inner_x1, inner_y, radius, PI/2, -PI/2)

def circular_rect_negative(context, x, y, width, height):
    """The same path as ``circular_rect()``, but going counter clockwise.
    """
    radius = height / 2.0
    inner_width = width - height
    inner_y = y + radius
    inner_x1 = x + radius
    inner_x2 = inner_x1 + inner_width

    context.move_to(inner_x1, y)
    context.arc_negative(inner_x1, inner_y, radius, -PI/2, PI/2)
    context.rel_line_to(inner_width, 0)
    context.arc_negative(inner_x2, inner_y, radius, PI/2, -PI/2)
    context.rel_line_to(-inner_width, 0)

class Shadow(object):
    """Encapsulates all parameters required to draw shadows.
    """
    def __init__(self, color, opacity, offset, blur_radius):
        self.color = color
        self.opacity = opacity
        self.offset = offset
        self.blur_radius = blur_radius

class ThreeImageSurface(object):
    """Takes a left, center and right image and draws them to an arbitrary
    width.  If the width is greater than the combined width of the 3 images,
    then the center image will be tiled to compensate.

    Example:

    >>> timelinebar = ThreeImageSurface("timelinebar")

    This creates a ``ThreeImageSurface`` using the images
    ``images/timelinebar_left.png``, ``images/timelinebar_center.png``, and
    ``images/timelinebar_right.png``.

    Example:

    >>> timelinebar = ThreeImageSurface()
    >>> img_left = make_surface("timelinebar_left")
    >>> img_center = make_surface("timelinebar_center")
    >>> img_right = make_surface("timelinebar_right")
    >>> timelinebar.set_images(img_left, img_center, img_right)

    This does the same thing, but allows you to explicitly set which images
    get used.
    """
    def __init__(self, basename=None):
        self.left = self.center = self.right = None
        self.height = 0
        self.width = None
        if basename is not None:
            left = make_surface(basename + '_left')
            center = make_surface(basename + '_center')
            right = make_surface(basename + '_right')
            self.set_images(left, center, right)

    def set_images(self, left, center, right):
        """Sets the left, center and right images to use.
        """
        self.left = left
        self.center = center
        self.right = right
        if not (self.left.height == self.center.height == self.right.height):
            raise ValueError("Images aren't the same height")
        self.height = self.left.height

    def set_width(self, width):
        """Manually set a width.

        When ThreeImageSurface have a width, then they have pretty much the
        same API as ImageSurface does.  In particular, they can now be nested
        in another ThreeImageSurface.
        """
        self.width = width

    def get_size(self):
        return self.width, self.height

    def draw(self, context, x, y, width, fraction=1.0):
        left_width = min(self.left.width, width)
        self.left.draw(context, x, y, left_width, self.height, fraction)
        self.draw_right(context, x + left_width, y, width - left_width, fraction)

    def draw_right(self, context, x, y, width, fraction=1.0):
        # draws only the right two images

        right_width = min(self.right.width, width)
        center_width = int(width - right_width)

        self.center.draw(context, x, y, center_width, self.height, fraction)
        self.right.draw(context, x + center_width, y, right_width, self.height, fraction)

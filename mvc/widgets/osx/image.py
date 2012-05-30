from AppKit import *
from Foundation import *
from objc import YES, NO, nil

from .base import Widget
from .drawing import DrawingStyle, DrawingContext, flip_context

class Image(NSImage):
    """See https://develop.participatoryculture.org/index.php/WidgetAPI for a description of the API for this class."""

    @classmethod
    def from_file(klass, filename):
        self = klass.alloc().initByReferencingFile_(filename)

        self.width = self.size().width
        self.height = self.size().height
        if self.width * self.height == 0:
            raise ValueError('Image has invalid size: (%d, %d)' % (
                    self.width, self.height))
        return self


class NSImageDisplay(NSView):
    def init(self):
        self = super(NSImageDisplay, self).init()
        self.border = False
        self.image = None
        return self

    def isFlipped(self):
        return YES

    def set_border(self, border):
        self.border = border

    def set_image(self, image):
        self.image = image

    def drawRect_(self, dest_rect):
        if self.image is not None:
            source_rect = self.calculateSourceRectFromDestRect_(dest_rect)
            context = NSGraphicsContext.currentContext()
            context.setShouldAntialias_(YES)
            context.setImageInterpolation_(NSImageInterpolationHigh)
            context.saveGraphicsState()
            flip_context(self.bounds().size.height)
            self.image.drawInRect_fromRect_operation_fraction_(
                dest_rect, source_rect, NSCompositeSourceOver, 1.0)
            context.restoreGraphicsState()
        if self.border:
            context = DrawingContext(self, self.bounds(), dest_rect)
            context.style = DrawingStyle()
            context.set_line_width(1)
            context.set_color((0, 0, 0))    # black
            context.rectangle(0, 0, context.width, context.height)
            context.stroke()

    def calculateSourceRectFromDestRect_(self, dest_rect):
        """Calulate where dest_rect maps to on our image.

        This is tricky because our image might be scaled up, in which case
        the rect from our image will be smaller than dest_rect.
        """
        view_size = self.frame().size
        x_scale = float(self.image.width) / view_size.width
        y_scale = float(self.image.height) / view_size.height

        return NSMakeRect(dest_rect.origin.x * x_scale,
                dest_rect.origin.y * y_scale,
                dest_rect.size.width * x_scale,
                dest_rect.size.height * y_scale)


class ImageDisplay(Widget):
    """See https://develop.participatoryculture.org/index.php/WidgetAPI for a description of the API for this class."""
    def __init__(self, image=None):
        Widget.__init__(self)
        self.create_signal('clicked')
        self.view = NSImageDisplay.alloc().init()
        self.set_image(image)

    def set_image(self, image):
        self.image = image
        if image:
            image.setCacheMode_(NSImageCacheNever)
        self.view.set_image(image)
        self.invalidate_size_request()

    def set_border(self, border):
        self.view.set_border(border)

    def calc_size_request(self):
        if self.image is not None:
            return self.image.width, self.image.height
        else:
            return 0, 0


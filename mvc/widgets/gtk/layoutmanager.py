"""drawing.py -- Contains the LayoutManager class.  LayoutManager is
handles laying out complex objects for the custom drawing code like
text blocks and buttons.
"""

import gtk
import pango


class LayoutManager(object):
    def __init__(self, widget):
        self.pango_context = widget.get_pango_context()
        self.update_style(widget.style)
        self.update_direction(widget.get_direction())
        widget.connect('style-set', self.on_style_set)
        widget.connect('direction-changed', self.on_direction_changed)
        self.widget = widget
        self.reset()

    def reset(self):
        self.current_font = self.font(1.0)
        self.text_color = (0, 0, 0)
        self.text_shadow = None

    def on_style_set(self, widget, previous_style):
        old_font_desc = self.style_font_desc
        self.update_style(widget.style)
        if self.style_font_desc != old_font_desc:
            # bug #17423 font changed, so the widget's width might have changed
            widget.queue_resize()

    def on_direction_changed(self, widget, previous_direction):
        self.update_direction(widget.get_direction())

    def update_style(self, style):
        self.style_font_desc = style.font_desc
        self.style = style

    def update_direction(self, direction):
        if direction == gtk.TEXT_DIR_RTL:
            self.pango_context.set_base_dir(pango.DIRECTION_RTL)
        else:
            self.pango_context.set_base_dir(pango.DIRECTION_LTR)

    def font(self, scale_factor, bold=False, italic=False, family=None):
        return Font(self.pango_context, self.style_font_desc,
                scale_factor, bold, italic)

    def set_font(self, scale_factor, bold=False, italic=False, family=None):
        self.current_font = self.font(scale_factor, bold, italic)

    def set_text_color(self, color):
        self.text_color = color

    def set_text_shadow(self, shadow):
        self.text_shadow = shadow

    def textbox(self, text, underline=False):
        textbox = TextBox(self.pango_context, self.current_font,
                self.text_color, self.text_shadow)
        textbox.set_text(text, underline=underline)
        return textbox

    def button(self, text, pressed=False, disabled=False, style='normal'):
        if style == 'webby':
            return StyledButton(text, self.pango_context, self.current_font,
                    pressed, disabled)
        elif use_native_buttons:
            return NativeButton(text, self.pango_context, self.current_font,
                    pressed, self.style, self.widget)
        else:
            return StyledButton(text, self.pango_context, self.current_font,
                    pressed)

    def update_cairo_context(self, cairo_context):
        cairo_context.update_context(self.pango_context)


class Font(object):
    def __init__(self, context, style_font_desc, scale, bold, italic):
        self.context = context
        self.description = style_font_desc.copy()
        self.description.set_size(int(scale * style_font_desc.get_size()))
        if bold:
            self.description.set_weight(pango.WEIGHT_BOLD)
        if italic:
            self.description.set_style(pango.STYLE_ITALIC)
        self.font_metrics = None

    def get_font_metrics(self):
        if self.font_metrics is None:
            self.font_metrics = self.context.get_metrics(self.description)
        return self.font_metrics

    def ascent(self):
        return pango.PIXELS(self.get_font_metrics().get_ascent())

    def descent(self):
        return pango.PIXELS(self.get_font_metrics().get_descent())

    def line_height(self):
        metrics = self.get_font_metrics()
        # the +1: some glyphs can be slightly taller than ascent+descent
        # (#17329)
        return (pango.PIXELS(metrics.get_ascent()) +
                pango.PIXELS(metrics.get_descent()) + 1)


class TextBox(object):
    def __init__(self, context, font, color, shadow):
        self.layout = pango.Layout(context)
        self.layout.set_wrap(pango.WRAP_WORD_CHAR)
        self.font = font
        self.color = color
        self.layout.set_font_description(font.description.copy())
        self.width = self.height = None
        self.shadow = shadow

    def set_text(self, text, font=None, color=None, underline=False):
        self.text_chunks = []
        self.attributes = []
        self.text_length = 0
        self.underlines = []
        self.append_text(text, font, color, underline)

    def append_text(self, text, font=None, color=None, underline=False):
        if text == None:
            text = u""
        startpos = self.text_length
        self.text_chunks.append(text)
        endpos = self.text_length = self.text_length + len(text)
        if font is not None:
            attr = pango.AttrFontDesc(font.description, startpos, endpos)
            self.attributes.append(attr)
        if underline:
            self.underlines.append((startpos, endpos))
        if color:
            def convert(value):
                return int(round(value * 65535))
            attr = pango.AttrForeground(convert(color[0]), convert(color[1]),
                    convert(color[2]), startpos, endpos)
            self.attributes.append(attr)
        self.text_set = False

    def set_width(self, width):
        if width is not None:
            self.layout.set_width(int(width * pango.SCALE))
        else:
            self.layout.set_width(-1)
        self.width = width

    def set_height(self, height):
        #if height is not None:
        #    self.layout.set_height(int(height * pango.SCALE))
        #else:
        #    self.layout.set_height(-1)
        self.height = height

    def set_wrap_style(self, wrap):
        if wrap == 'word':
            self.layout.set_wrap(pango.WRAP_WORD_CHAR)
        elif wrap == 'char' or wrap == 'truncated-char':
            self.layout.set_wrap(pango.WRAP_CHAR)
        else:
            raise ValueError("Unknown wrap value: %s" % wrap)
        if wrap == 'truncated-char':
            self.layout.set_ellipsize(pango.ELLIPSIZE_END)
        else:
            self.layout.set_ellipsize(pango.ELLIPSIZE_NONE)

    def set_alignment(self, align):
        if align == 'left':
            self.layout.set_alignment(pango.ALIGN_LEFT)
        elif align == 'right':
            self.layout.set_alignment(pango.ALIGN_RIGHT)
        elif align == 'center':
            self.layout.set_alignment(pango.ALIGN_CENTER)
        else:
            raise ValueError("Unknown align value: %s" % align)

    def ensure_layout(self):
        if not self.text_set:
            text = ''.join(self.text_chunks)
            if len(text) > 100:
                text = text[:self._calc_text_cutoff()]
            self.layout.set_text(text)
            attr_list = pango.AttrList()
            for attr in self.attributes:
                attr_list.insert(attr)
            self.layout.set_attributes(attr_list)
            self.text_set = True

    def _calc_text_cutoff(self):
        """This method is a bit of a hack...  GTK slows down if we pass too
        much text to the layout.  Even text that falls below our height has a
        performance penalty.  Try not to have too much more than is necessary.
        """
        if None in (self.width, self.height):
            return -1

        chars_per_line = (self.width * pango.SCALE //
                self.font.get_font_metrics().get_approximate_char_width())
        lines_available = self.height // self.font.line_height()
        # overestimate these because it's better to have too many characters
        # than too little.
        return int(chars_per_line * lines_available * 1.2)

    def line_count(self):
        self.ensure_layout()
        return self.layout.get_line_count()

    def get_size(self):
        self.ensure_layout()
        return self.layout.get_pixel_size()

    def char_at(self, x, y):
        self.ensure_layout()
        x *= pango.SCALE
        y *= pango.SCALE
        width, height = self.layout.get_size()
        if 0 <= x < width and 0 <= y < height:
            index, leading = self.layout.xy_to_index(x, y)
            # xy_to_index returns the nearest character, but that
            # doesn't mean the user actually clicked on it.  Double
            # check that (x, y) is actually inside that char's
            # bounding box
            char_x, char_y, char_w, char_h = self.layout.index_to_pos(index)
            if char_w > 0: # the glyph is LTR
                left = char_x
                right = char_x + char_w
            else: # the glyph is RTL
                left = char_x + char_w
                right = char_x
            if left <= x < right:
                return index
        return None


    def draw(self, context, x, y, width, height):
        self.set_width(width)
        self.set_height(height)
        self.ensure_layout()
        cairo_context = context.context
        cairo_context.save()
        if self.shadow:
            # draw shadow first so that it's underneath the regular text
            # FIXME: we don't use the blur_radius setting
            cairo_context.set_source_rgba(self.shadow.color[0],
                    self.shadow.color[1], self.shadow.color[2],
                    self.shadow.opacity)
            self._draw_layout(context, x + self.shadow.offset[0],
                    y + self.shadow.offset[1], width, height)
        cairo_context.set_source_rgb(*self.color)
        self._draw_layout(context, x, y, width, height)
        cairo_context.restore()
        cairo_context.new_path()

    def _draw_layout(self, context, x, y, width, height):
        line_height = 0
        alignment = self.layout.get_alignment()
        for i in xrange(self.layout.get_line_count()):
            line = self.layout.get_line_readonly(i)
            extents = line.get_pixel_extents()[1]
            next_line_height = line_height + extents[3]
            if next_line_height > height:
                break
            if alignment == pango.ALIGN_CENTER:
                line_x = max(x, x + (width - extents[2]) / 2.0)
            elif alignment == pango.ALIGN_RIGHT:
                line_x = max(x, x + width - extents[2])
            else:
                line_x = x
            baseline = y + line_height + pango.ASCENT(extents)
            context.move_to(line_x, baseline)
            context.context.show_layout_line(line)
            line_height = next_line_height

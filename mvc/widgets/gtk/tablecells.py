# Miro - an RSS based video player application
# Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011
# Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""tableviewcells.py - Cell renderers for TableView."""

import gobject
import gtk
import pango

from .base import make_gdk_color
from .drawing import DrawingStyle, DrawingContext

class CellRenderer(object):
    """Simple Cell Renderer
    https://develop.participatoryculture.org/index.php/WidgetAPITableView"""
    def __init__(self):
        self._renderer = gtk.CellRendererText()
        self.want_hover = False

    def setup_attributes(self, column, attr_map):
        column.add_attribute(self._renderer, 'text', attr_map['value'])

    def set_align(self, align):
        if align == 'left':
            self._renderer.props.xalign = 0.0
        elif align == 'center':
            self._renderer.props.xalign = 0.5
        elif align == 'right':
            self._renderer.props.xalign = 1.0
        else:
            raise ValueError("unknown alignment: %s" % align)

    def set_color(self, color):
        self._renderer.props.foreground_gdk = make_gdk_color(color)

    def set_bold(self, bold):
        font_desc = self._renderer.props.font_desc
        if bold:
            font_desc.set_weight(pango.WEIGHT_BOLD)
        else:
            font_desc.set_weight(pango.WEIGHT_NORMAL)
        self._renderer.props.font_desc = font_desc

    def set_font_scale(self, scale_factor):
        self._renderer.props.scale = scale_factor

class ImageCellRenderer(object):
    """Cell Renderer for images
    https://develop.participatoryculture.org/index.php/WidgetAPITableView"""
    def __init__(self):
        self._renderer = gtk.CellRendererPixbuf()
        self.want_hover = False

    def setup_attributes(self, column, attr_map):
        column.add_attribute(self._renderer, 'pixbuf', attr_map['image'])

class GTKCustomCellRenderer(gtk.GenericCellRenderer):
    """Handles the GTK side of CustomCellRenderer
    https://develop.participatoryculture.org/index.php/WidgetAPITableView"""

    def __init__(self, wrapper):
        super(GTKCustomCellRenderer, self).__init__()
        self.wrapper = wrapper

    def on_get_size(self, widget, cell_area=None):
        style = DrawingStyle(widget, use_base_color=True)
        # NOTE: CustomCellRenderer.cell_data_func() sets up its attributes
        # from the model itself, so we don't have to worry about setting them
        # here.
        width, height = self.wrapper.get_size(style, widget.layout_manager)
        if self.wrapper.IGNORE_PADDING:
            x_offset = y_offset = 0
        else:
            x_offset = self.props.xpad
            y_offset = self.props.ypad
            width += self.props.xpad * 2
            height += self.props.ypad * 2
            if cell_area:
                x_offset += cell_area.x
                y_offset += cell_area.x
                extra_width = max(0, cell_area.width - width)
                extra_height = max(0, cell_area.height - height)
                x_offset += int(round(self.props.xalign * extra_width))
                y_offset += int(round(self.props.yalign * extra_height))
        return x_offset, y_offset, width, height

    def on_render(self, window, widget, background_area, cell_area, expose_area,
            flags):
        selected = (flags & gtk.CELL_RENDERER_SELECTED)
        if selected:
            if widget.flags() & gtk.HAS_FOCUS:
                state = gtk.STATE_SELECTED
            else:
                state = gtk.STATE_ACTIVE
        else:
            state = gtk.STATE_NORMAL
        if self.wrapper.IGNORE_PADDING:
            area = background_area
        else:
            xpad = self.props.xpad
            ypad = self.props.ypad
            area = gtk.gdk.Rectangle(cell_area.x + xpad, cell_area.y + ypad,
                    cell_area.width - xpad * 2, cell_area.height - ypad * 2)
        context = DrawingContext(window, area, expose_area)
        # Draw the base color as our background.  This erases the gradient that
        # GTK draws for selected items.
        window.draw_rectangle(widget.style.base_gc[state], True,
                              background_area.x, background_area.y,
                              background_area.width, background_area.height)
        context.style = DrawingStyle(widget,
                use_base_color=True, state=state)
        widget.layout_manager.update_cairo_context(context.context)
        # hotspot_tracker = widget.hotspot_tracker
        # if (hotspot_tracker and hotspot_tracker.hit and
        #         hotspot_tracker.column == self.column and
        #         hotspot_tracker.path == self.path):
        #     hotspot = hotspot_tracker.name
        # else:
        #     hotspot = None
        # if (self.path, self.column) == widget.hover_info:
        #     hover = widget.hover_pos
        #     hover = (hover[0] - xpad, hover[1] - ypad)
        # else:
        #     hover = None
        # NOTE: CustomCellRenderer.cell_data_func() sets up its attributes
        # from the model itself, so we don't have to worry about setting them
        # here.
        hotspot = hover = None
        widget.layout_manager.reset()
        self.wrapper.render(context, widget.layout_manager, selected,
                hotspot, hover)

    def on_activate(self, event, widget, path, background_area, cell_area,
            flags):
        pass

    def on_start_editing(self, event, widget, path, background_area,
            cell_area, flags):
        pass


gobject.type_register(GTKCustomCellRenderer)


class CustomCellRenderer(object):
    """Customizable Cell Renderer
    https://develop.participatoryculture.org/index.php/WidgetAPITableView"""

    IGNORE_PADDING = True

    def __init__(self):
        self._renderer = GTKCustomCellRenderer(self)
        self.want_hover = False

    def setup_attributes(self, column, attr_map):
        column.set_cell_data_func(self._renderer, self.cell_data_func,
                attr_map)

    def cell_data_func(self, column, cell, model, iter, attr_map):
        cell.column = column
        cell.path = model.get_path(iter)
        row = model[iter]
        # Set attributes on self instead cell This works because cell is just
        # going to turn around and call our methods to do the rendering.
        for name, index in attr_map.items():
            setattr(self, name, row[index])

    def hotspot_test(self, style, layout, x, y, width, height):
        return None

    def get_size(self, context, layout_manager):
        return 0, 0

    def render(self, context, layout_manager, selected, hotspot, hover):
        pass

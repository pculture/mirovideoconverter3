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

"""mvc.widgets.gtk.window -- GTK Window widget."""

import gtk

from .base import WidgetMixin

class Window(WidgetMixin, gtk.Window):

    def __init__(self, title):
        super(Window, self).__init__()
        self.set_title(title)
        self.create_signal('file-drag-motion')
        self.create_signal('file-drag-received')
        self.create_signal('file-drag-leave')
        self.signal_handles = []

    def add(self, widget):
        widget.show()
        super(Window, self).add(widget)

    def accept_file_drag(self, val):
        if not val:
            self.drag_dest_set(0, [], 0)
            for handle in self.signal_handles:
                self.disconnect(handle)
            self.signal_handles = []
        else:
            self.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_DROP,
                               [('text/uri-list', 0, 0)],
                               gtk.gdk.ACTION_COPY)
            for signal, callback in (
                ('drag-motion', self.on_drag_motion),
                ('drag-data-received', self.on_drag_data_received),
                ('drag-leave', self.on_drag_leave)):
                self.signal_handles.append(
                    self.connect(signal, callback))

    def on_drag_motion(self, widget, context, x, y, time):
        self.emit('file-drag-motion')

    def on_drag_data_received(self, widget, context, x, y, selection_data,
                              info, time):
        self.emit('file-drag-received', selection_data.get_uris())

    def on_drag_leave(self, widget, context, time):
        self.emit('file-drag-leave')


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

"""mvc.widgets.gtk.controls -- Control Widgets."""

import logging

import gtk
import gobject

class OptionMenu(gtk.ComboBox):
    def __init__(self, options):
        store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        for (key, value) in options:
            store.append((key, value))
        super(OptionMenu, self).__init__(store)

        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_active_iter(store.get_iter_first())

    def get_selected(self):
        iter_ = self.get_active_iter()
        if not iter_:
            return
        return self.get_model()[iter_][1]

    def set_selected(self, index):
        self.set_active(index)


class Button(gtk.Button):
    def enable(self):
        self.set_sensitive(True)

    def disable(self):
        self.set_sensitive(False)


class Label(gtk.Label):
    def __init__(self, text=None, markup=False):
        super(Label, self).__init__()
        if text:
            if markup:
                self.set_markup(text)
                self.set_track_visited_links(False)
            else:
                self.set_text(text)

    def connect(self, signal, method, *args):
        if signal == 'clicked':
            signal = 'activate-link'
            old_method = method
            def wrapper(widget, link, *a):
                try:
                    old_method(widget, *a)
                except:
                    logging.exception('during activate-link')
                return True
            method = wrapper
        super(Label, self).connect(signal, method, *args)

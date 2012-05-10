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

"""mvc.widgets.gtk.layout -- Layout widgets.  """

import gtk

from .base import WidgetMixin, BinMixin


class BoxMixin(WidgetMixin):
    def pack_start(self, widget, expand=False):
        widget.show()
        super(BoxMixin, self).pack_start(widget, expand=expand)

    def pack_end(self, widget, expand=False):
        widget.show()
        super(BoxMixin, self).pack_end(widget, expand=expand)


class HBox(BoxMixin, gtk.HBox):
    pass


class VBox(BoxMixin, gtk.VBox):
    pass


class Alignment(BinMixin, gtk.Alignment):
    def __init__(self, xalign=0, yalign=0, xscale=0, yscale=0,
                 top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
        BinMixin.__init__(self)
        gtk.Alignment.__init__(self, xalign, yscale, xscale, yscale)
        self.set_padding(top_pad, bottom_pad, left_pad, right_pad)


class Scroller(BinMixin, gtk.ScrolledWindow):
    def __init__(self, horizontal=False, vertical=False):
        super(Scroller, self).__init__()
        h_policy = gtk.POLICY_AUTOMATIC if horizontal else gtk.POLICY_NEVER
        v_policy = gtk.POLICY_AUTOMATIC if vertical else gtk.POLICY_NEVER
        self.set_policy(h_policy, v_policy)

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

"""menus.py -- Menu handling code."""

import struct

import AppKit

from objc import *
from AppKit import *
from Foundation import *

from mvc.widgets import keyboard
from .contextmenu import ContextMenuHandler, MiroContextMenu

# XXX HEAVILY REDUCED VERSION FRO MIRO.  FIXME!


MODIFIERS_MAP = {
    keyboard.MOD:   NSCommandKeyMask,
    keyboard.CMD:   NSCommandKeyMask,
    keyboard.SHIFT: NSShiftKeyMask,
    keyboard.CTRL:  NSControlKeyMask,
    keyboard.ALT:   NSAlternateKeyMask
}

if isinstance(NSBackspaceCharacter, int):
    backspace = NSBackspaceCharacter
else:
    backspace = ord(NSBackspaceCharacter)
    
KEYS_MAP = {
    keyboard.SPACE: " ",
    keyboard.ENTER: "\r",
    keyboard.BKSPACE: struct.pack("H", backspace),
    keyboard.DELETE: NSDeleteFunctionKey,
    keyboard.RIGHT_ARROW: NSRightArrowFunctionKey,
    keyboard.LEFT_ARROW: NSLeftArrowFunctionKey,
    keyboard.UP_ARROW: NSUpArrowFunctionKey,
    keyboard.DOWN_ARROW: NSDownArrowFunctionKey,
    '.': '.',
    ',': ','
}
# add function keys
for i in range(1, 13):
    portable_key = getattr(keyboard, "F%s" % i)
    osx_key = getattr(AppKit, "NSF%sFunctionKey" % i)
    KEYS_MAP[portable_key] = osx_key

REVERSE_MODIFIERS_MAP = dict((i[1], i[0]) for i in MODIFIERS_MAP.items())
REVERSE_KEYS_MAP = dict((i[1], i[0]) for i in KEYS_MAP.items() 
        if i[0] != keyboard.BKSPACE)
REVERSE_KEYS_MAP[u'\x7f'] = keyboard.BKSPACE
REVERSE_KEYS_MAP[u'\x1b'] = keyboard.ESCAPE

def make_context_menu(menu_items):
    nsmenu = MiroContextMenu.alloc().init()
    for item in menu_items:
        if item is None:
            nsitem = NSMenuItem.separatorItem()
        else:
            label, callback = item
            nsitem = NSMenuItem.alloc().init()
            if isinstance(label, tuple) and len(label) == 2:
                label, icon_path = label
                image = NSImage.alloc().initWithContentsOfFile_(icon_path)
                nsitem.setImage_(image)
            if callback is None:
                font_size = NSFont.systemFontSize()
                font = NSFont.fontWithName_size_("Lucida Sans Italic", font_size)
                if font is None:
                    font = NSFont.systemFontOfSize_(font_size)
                attributes = {NSFontAttributeName: font}
                attributed_label = NSAttributedString.alloc().initWithString_attributes_(label, attributes)
                nsitem.setAttributedTitle_(attributed_label)
            else:
                nsitem.setTitle_(label)
                if isinstance(callback, list):
                    submenu = make_context_menu(callback)
                    nsmenu.setSubmenu_forItem_(submenu, nsitem)
                else:
                    handler = ContextMenuHandler.alloc().initWithCallback_(callback)
                    nsitem.setTarget_(handler)
                    nsitem.setAction_('handleMenuItem:')
        nsmenu.addItem_(nsitem)
    return nsmenu

def translate_event_modifiers(event):
    mods = set()
    flags = event.modifierFlags()
    if flags & NSCommandKeyMask:
        mods.add(keyboard.CMD)
    if flags & NSControlKeyMask:
        mods.add(keyboard.CTRL)
    if flags & NSAlternateKeyMask:
        mods.add(keyboard.ALT)
    if flags & NSShiftKeyMask:
        mods.add(keyboard.SHIFT)
    return mods

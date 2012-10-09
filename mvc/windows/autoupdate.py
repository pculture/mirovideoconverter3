# Miro - an RSS based video player application
# Copyright (C) 2012
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

"""Autoupdate functionality """

import ctypes
import _winreg as winreg
import logging

winsparkle = ctypes.cdll.WinSparkle

APPCAST_URL = 'http://miro-updates.participatoryculture.org/mvc-appcast.xml'

def startup():
    enable_automatic_checks()
    winsparkle.win_sparkle_set_appcast_url(APPCAST_URL)
    winsparkle.win_sparkle_init()

def shutdown():
    winsparkle.win_sparkle_cleanup()

def enable_automatic_checks():
    # We should be able to use win_sparkle_set_automatic_check_for_updates,
    # but that's only available after version 0.4 and the current release
    # version is 0.4
    with open_winsparkle_key() as winsparkle_key:
	if not check_for_updates_set(winsparkle_key):
	    set_default_check_for_updates(winsparkle_key)

def open_winsparkle_key():
    """Open the MVC WinSparkle registry key
    
    If any components are not created yet, we will try to create them
    """
    with open_or_create_key(winreg.HKEY_CURRENT_USER, "Software") as software:
	with open_or_create_key(software,
		"Participatory Culture Foundation") as pcf:
	    with open_or_create_key(pcf, "Miro Video Converter") as mvc:
		return open_or_create_key(mvc, "WinSparkle",
			write_access=True)

def open_or_create_key(key, subkey, write_access=False):
    if write_access:
	sam = winreg.KEY_READ | winreg.KEY_WRITE
    else:
	sam = winreg.KEY_READ
    try:
	return winreg.OpenKey(key, subkey, 0, sam)
    except OSError, e:
	if e.errno == 2:
	    # Not Found error.  We should create the key
	    return winreg.CreateKey(key, subkey)
	else:
	    raise

def check_for_updates_set(winsparkle_key):
    try:
	winreg.QueryValueEx(winsparkle_key, "CheckForUpdates")
    except OSError, e:
	if e.errno == 2:
	    # not found error.
	    return False
	else:
	    raise
    else:
	return True


def set_default_check_for_updates(winsparkle_key):
    """Initialize the WinSparkle regstry values with our defaults.

    :param mvc_key winreg.HKey object for to the MVC registry
    """
    logging.info("Writing WinSparkle keys")
    winreg.SetValueEx(winsparkle_key, "CheckForUpdates", 0, winreg.REG_SZ, "1")

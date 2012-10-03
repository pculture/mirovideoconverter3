"""openfiles.py -- open files/folders."""

import logging
import os
import subprocess
import sys


# To open paths we use an OS-specific command.  The approach is from:
# http://stackoverflow.com/questions/6631299/python-opening-a-folder-in-explorer-nautilus-mac-thingie

def check_kde():
    return os.environ.get("KDE_FULL_SESSION", None) != None

def _open_path_osx(path):
    subprocess.call(['open', '--', path])

def _open_path_kde(path):
    subprocess.call(["kfmclient", "exec", "file://" + path])

def _open_path_gnome(path):
    subprocess.call(["gnome-open", path])

def _open_path_windows(path):
    subprocess.call(['explorer', path])

def _open_path(path):
    if sys.platform == 'darwin':
	_open_path_osx(path)
    elif sys.platform == 'linux2':
	if check_kde():
	    _open_path_kde(path)
	else:
	    _open_path_gnome(path)
    elif sys.platform == 'win32':
	_open_path_windows(path)
    else:
	logging.warn("unknown platform: %s", sys.platform)

def reveal_folder(path):
    """Show a folder in the desktop shell (finder/explorer/nautilous, etc)."""
    logging.info("reveal_folder: %s", path)
    if os.path.isdir(path):
	_open_path(path)
    else:
	_open_path(os.path.dirname(path))

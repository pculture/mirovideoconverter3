"""setup-windows.py -- setup script for windows

Usage:

"""
import itertools
from glob import glob
import os
from distutils.core import setup

import py2exe

from mvc import resources

packages = [
    'mvc',
    'mvc.widgets',
    'mvc.widgets.gtk',
    'mvc.ui',
    'mvc.resources',
]

def resources_dir():
    return os.path.dirname(resources.__file__)

def resource_data_files(subdir, globspec='*.*'):
    dest_dir = os.path.join("resources", subdir)
    dir_contents = glob(os.path.join(resources_dir(), subdir, globspec))
    return [(dest_dir, dir_contents)]

def data_files():
    return list(itertools.chain(
        resource_data_files("images"),
        resource_data_files("converters", "*.py"),
    ))

def gtk_includes():
    return ['gtk', 'gobject', 'atk', 'pango', 'pangocairo', 'gio']

def py2exe_includes():
    return gtk_includes()

setup(
    name="Miro Video Converter",
    packages=packages,
    version='3.0',
    console=[
        {'script': 'mvc/__main__.py',
        'dest_base': 'mvc',
        },
    ],
    data_files=data_files(),
    options={
        'py2exe': {
            'skip_archive': True,
            'includes': py2exe_includes(),
        },
    },
)

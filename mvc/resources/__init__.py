import os.path
import glob
import sys

def image_path(name):
    return os.path.join(resources_dir(), 'images', name)

def converter_scripts():
    return glob.glob(os.path.join(resources_dir(), 'converters', '*.py'))


def resources_dir():
    if in_py2exe():
        directory = os.path.join(os.path.dirname(sys.executable), "resources")
    else:
        directory = os.path.dirname(__file__)
    return os.path.abspath(directory)

def in_py2exe():
    return (hasattr(sys,"frozen") and
            sys.frozen in ("windows_exe", "console_exe"))

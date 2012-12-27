import os
import sys

script_vars = {
    'VERSION': '3.0',
}

if sys.platform.startswith("linux"):
    setup_dir = 'linux'
elif sys.platform.startswith("win32"):
    setup_dir = 'windows'
elif sys.platform.startswith("darwin"):
    setup_dir = 'osx'
else:
    sys.stderr.write("Unknown platform: %s" % sys.platform)

setup_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'setup-files', setup_dir))
script_vars['SETUP_DIR'] = setup_dir

execfile(os.path.join(setup_dir, 'setup.py'), script_vars)

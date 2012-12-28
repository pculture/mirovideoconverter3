"""setup-windows.py -- setup script for windows

Usage:

"""
from distutils import log
from distutils.core import Command, setup
from glob import glob
import itertools
import os
import subprocess
import sys

import py2exe

from mvc import resources

env_path = os.path.abspath(os.path.dirname(os.path.dirname(sys.executable)))
nsis_path = os.path.join(env_path, 'nsis-2.46', 'makensis.exe')
scripts_path = os.path.join(env_path, 'Scripts')

packages = [
    'mvc',
    'mvc.widgets',
    'mvc.widgets.gtk',
    'mvc.ui',
    'mvc.resources',
    'mvc.windows',
    'mvc.qtfaststart',
]

def resources_dir():
    return os.path.dirname(resources.__file__)

def resource_data_files(subdir, globspec='*.*'):
    dest_dir = os.path.join("resources", subdir)
    dir_contents = glob(os.path.join(resources_dir(), subdir, globspec))
    return [(dest_dir, dir_contents)]

def ffmpeg_data_files():
    ffmpeg_dir = os.path.join(env_path, 'ffmpeg')
    return [
            ('ffmpeg',
                [os.path.join(ffmpeg_dir, 'ffmpeg.exe')]),
            #('ffmpeg/presets',
            #glob(os.path.join(ffmpeg_dir, 'presets', '*.ffpreset'))),
            ]

def winsparkle_data_files():
    winsparkle_dll = os.path.join(env_path, 'WinSparkle-0.3',
	    "WinSparkle.dll")
    return [
            ('', [winsparkle_dll]),
    ]

def gtk_theme_data_files():
    engine_path = os.path.join(env_path, 'gtk2-themes-2009-09-07-win32_bin',
	    'lib', 'gtk-2.0', '2.10.0', 'engines', 'libclearlooks.dll')
    gtkrc_path = os.path.join(resources_dir(), 'windows', 'gtkrc')
    return [
	    ('etc/gtk-2.0', [gtkrc_path]),
	    ('lib/gtk-2.0/2.10.0/engines', [engine_path])
    ]

def avconv_data_files():
    avconv_dir = os.path.join(env_path, 'avconv')
    return [
            ('avconv',
                glob(os.path.join(avconv_dir, '*.*'))),
            ]

def data_files():
    return list(itertools.chain(
        resource_data_files("images"),
        resource_data_files("converters", "*.py"),
        ffmpeg_data_files(),
        winsparkle_data_files(),
        gtk_theme_data_files(),
        #avconv_data_files(),
    ))

def gtk_includes():
    return ['gtk', 'gobject', 'atk', 'pango', 'pangocairo', 'gio']

def py2exe_includes():
    return gtk_includes()

class bdist_nsis(Command):
    description = "create MVC installer using NSIS"
    user_options = [
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('py2exe')
        self.dist_dir = self.get_finalized_command('py2exe').dist_dir

        log.info("building installer")

        nsis_source = os.path.join(SETUP_DIR, 'mvc.nsi')
        self.copy_file(nsis_source, self.dist_dir)
        for nsis_file in glob(os.path.join(resources_dir(), 'nsis', '*.*')):
            self.copy_file(nsis_file, self.dist_dir)

        plugins_dir = os.path.join(resources_dir(), 'nsis', 'plugins')
        script_path = os.path.join(self.dist_dir, 'mvc.nsi')
        nsis_defines = {
            'CONFIG_PLUGIN_DIR': plugins_dir,
        }
        cmd_line = [nsis_path]
        for name, value in nsis_defines.items():
            cmd_line.append("/D%s=%s" % (name, value))
        cmd_line.append(script_path)

        if subprocess.call(cmd_line) != 0:
            print "ERROR creating the 1 stage installer, quitting"
            return
setup(
    windows=[
        {'script': 'mvc/windows/exe_main.py',
        'dest_base': 'mvc',
	'company_name': 'Participatory Culture Foundation',
        },
    ],
    console=[
        {'script': 'mvc/windows/exe_main.py',
        'dest_base': 'mvcdebug',
	'company_name': 'Participatory Culture Foundation',
        },
    ],
    data_files=data_files(),
    cmdclass={
        'bdist_nsis': bdist_nsis,
        },
    options={
        'py2exe': {
            'includes': py2exe_includes(),
        },
    },
    **SETUP_ARGS
)

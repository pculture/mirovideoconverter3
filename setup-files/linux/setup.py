import glob
import os
import shutil
import subprocess
import sys
from distutils.cmd import Command
from setuptools import setup

if sys.version < '2.7':
    raise RuntimeError('MVC requires Python 2.7')

def icon_data_files():
    sizes = [16, 22, 32, 48]
    data_files = []
    for size in sizes:
        d = os.path.join("icons", "hicolor", "%sx%s" % (size, size), "apps")
        source = os.path.join(SETUP_DIR, d, "mirovideoconverter.png")
        dest = os.path.join("/usr/share/", d)
        data_files.append((dest, [source]))

    return data_files

def application_data_files():
    return [
        ('/usr/share/applications',
         [os.path.join(SETUP_DIR, 'mirovideoconverter.desktop')]),
    ]

def data_files():
    return application_data_files() + icon_data_files()

class sdist_deb(Command):
    description = ("Build a debian source package.")
    user_options = [
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) in "
         "[default: dist]"),
    ]

    def initialize_options(self):
        self.dist_dir = None

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = 'dist'
        self.dist_dir = os.path.abspath(self.dist_dir)

    def run(self):
        self.run_command("sdist")
        self.setup_dirs()
        for debian_dir in glob.glob(os.path.join(SETUP_DIR, 'debian-*')):
            self.build_for_release(debian_dir)
        os.chdir(self.orig_dir)
        print
        print "debian source build complete"
        print "files are in %s" % self.work_dir

    def build_for_release(self, debian_dir):
        os.chdir(self.work_dir)
        source_tree = os.path.join(self.work_dir,
                                   'mirovideoconverter-%s' % VERSION)
        if os.path.exists(source_tree):
            shutil.rmtree(source_tree)
        self.extract_tarball()
        self.copy_debian_directory(debian_dir)
        os.chdir('mirovideoconverter-%s' % VERSION)
        subprocess.check_call(['dpkg-buildpackage', '-S'])

    def setup_dirs(self):
        self.orig_dir = os.getcwd()
        self.work_dir = os.path.join(self.dist_dir, 'deb')
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir)

    def extract_tarball(self):
        tarball = os.path.join(self.dist_dir,
                               "mirovideoconverter-%s.tar.gz" % VERSION)
        subprocess.check_call(["tar", "zxf", tarball])
        shutil.copyfile(tarball,
                        "mirovideoconverter_%s.orig.tar.gz" % VERSION)

    def copy_debian_directory(self, debian_dir):
        dest = os.path.join(self.work_dir,
                            'mirovideoconverter-%s/debian' % VERSION)
        shutil.copytree(debian_dir, dest)

setup(
    cmdclass={
        'sdist_deb': sdist_deb,
    },
    data_files=data_files(),
    scripts=['scripts/miro-video-converter.py'],
    **SETUP_ARGS
)

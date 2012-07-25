import contextlib
import os
import sys
import urllib
import shutil
import subprocess
import time
import zipfile
from optparse import OptionParser

env_dir = build_dir = site_packages_dir = scripts_dir = python_dir = None
options = args = None

def setup_global_dirs(parser_args):
    global env_dir, working_dir, build_dir, site_packages_dir, scripts_dir
    global python_dir

    env_dir = os.path.abspath(parser_args[0])
    working_dir = os.getcwd()
    build_dir = os.path.abspath(os.path.join('mvc-env-build'))
    site_packages_dir = os.path.join(env_dir, "Lib", "site-packages")
    scripts_dir = os.path.join(env_dir, "Scripts")
    python_dir = os.path.join(env_dir, "Python")

def parse_args():
    global options, args

    usage = "usage: %prog [options] env-directory"
    parser = OptionParser(usage)

    parser.add_option("-f", "--force", dest="force",
            action="store_true",
            help="overwrite env directory if it exists")

    parser.add_option("--7-zip-exe", dest="seven_zip_path",
            default="C:\\Program Files\\7-Zip\\7z.exe",
            help="path to 7z.exe")

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("must specify env-directory")
    if len(args) > 1:
        parser.error("can only specify one env-directory")
    setup_global_dirs(args)
    if os.path.exists(env_dir) and not options.force:
        parser.error("%s exists.  Use -f to overwrite" % env_dir)

def writeout(msg, *args):
    """write a line to stdout."""
    print msg % args

def writeout_and_stay(msg, *args):
    """write a line to stdout and stay on the same line."""

    # clear out old line
    print " " * 70 + "\r",
    # write out new line
    print (msg % args) + "\r",
    sys.stdout.flush()

def rmtree_if_exists(directory):
    """Remove a directory tree, if it exists."""
    if os.path.exists(directory):
        if not options.force:
            raise AssertionError("%s exists and force not set" % directory)
        writeout("Removing %s", directory)
        shutil.rmtree(directory)

def check_call(*command_line):
    subprocess.check_call(command_line, shell=True)

@contextlib.contextmanager
def build_dir_context():
    """Context to create a build directory and delete it afterwards.
    """

    rmtree_if_exists(build_dir)
    os.makedirs(build_dir)
    yield
    shutil.rmtree(build_dir)

def download_url(url):
    """Download a url to the build directory."""

    basename = os.path.basename(url)
    download_path = os.path.join(build_dir, basename)
    writeout("* Downloading %s", basename)
    time_info = { 'last': 0}
    def reporthook(block_count, block_size, total_size):
        now = time.time()
        if total_size > 0 and now - time_info['last'] > 0.5:
            percent_complete = (block_count * block_size * 100.0) / total_size
            writeout_and_stay("  %0.1f complete", percent_complete)
            time_info['last'] = now
    urllib.urlretrieve(url, download_path, reporthook)
    writeout_and_stay("  100.0%% complete")

    return download_path

def movetree(source_dir, dest_dir):
    """Move the contents of source_dir into dest_dir

    For each file/directory in source dir, copy it to dest_dir.  If this would
    overwrite a file/directory, then an IOError will be raised
    """
    for name in os.listdir(source_dir):
        source_child = os.path.join(source_dir, name)
        writeout("* moving %s to %s", name, dest_dir)
        shutil.move(source_child, os.path.join(dest_dir, name))

def extract_zip(zip_path, dest_dir):
    writeout("* Extracting %s", zip_path)
    archive = zipfile.ZipFile(zip_path, 'r')
    for name in archive.namelist():
        writeout("**  %s", name)
        archive.extract(name, dest_dir)
    archive.close()

def run_pip_install(package_name, version):
    pip_path = os.path.join(scripts_dir, 'pip.exe')
    check_call(pip_path, 'install', "%s==%s" % (package_name, version))

def install_lessmsi():
    url = "http://lessmsi.googlecode.com/files/lessmsi-v1.0.8.zip"
    zip_path = download_url(url)
    extract_zip(zip_path, os.path.join(build_dir, 'lessmsi'))
    # make all files executable
    for filename in ('lessmsi.exe', 'wix.dll', 'wixcab.dll'):
        path = os.path.join(build_dir, 'lessmsi', filename)
        check_call("chmod", "+x", path)

def run_lessmsi(msi_path, output_dir):
    writeout("* Extracting MSI %s", os.path.basename(msi_path))
    lessmsi_path = os.path.join(build_dir, 'lessmsi', 'lessmsi.exe')
    check_call(lessmsi_path, "/x", msi_path, output_dir)

def make_env_dir():
    rmtree_if_exists(env_dir)
    os.makedirs(env_dir)

def install_virtualenv():
    virtualenv_path = os.path.join(os.path.dirname(__file__), "virtualenv.py")
    python_path = os.path.join(python_dir, "python.exe")
    check_call("python", virtualenv_path, "-p", python_path, '--clear',
            env_dir)

def install_python():
    url = "http://python.org/ftp/python/2.7.3/python-2.7.3.msi"
    download_path = download_url(url)
    build_path = os.path.join(build_dir, 'Python')
    run_lessmsi(download_path, build_path)
    shutil.move(os.path.join(build_path, "SourceDir"), python_dir)

def install_py2exe():
    url = ("http://downloads.sourceforge.net"
            "/project/py2exe/py2exe/0.6.9/py2exe-0.6.9.zip")
    zip_path = download_url(url)
    extract_zip(zip_path, os.path.join(build_dir, 'py2exe'))
    writeout("* Installing py2exe")
    os.chdir(os.path.join(build_dir, 'py2exe', 'py2exe-0.6.9'))
    check_call(os.path.join(scripts_dir, "python.exe"), 'setup.py', 'install')
    os.chdir(working_dir)

def install_pygtk():
    url = ('http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/'
            'pygtk-all-in-one-2.24.2.win32-py2.7.msi')
    msi_path = download_url(url)
    build_path = os.path.join(build_dir, 'pygtk-all-in-one')
    run_lessmsi(msi_path, build_path)

    source_package_dir = os.path.join(build_path, "SourceDir", "Lib",
            "site-packages")
    writeout("* Copying pygtk site-packages")
    movetree(source_package_dir, site_packages_dir)

def install_ffmpeg():
    url = ("http://ffmpeg.zeranoe.com/builds/win32/static/"
            "ffmpeg-20120426-git-a4b58fd-win32-static.7z")
    download_path = download_url(url)
    check_call(options.seven_zip_path, "x", download_path, '-o' + build_dir)

    ffmpeg_dir = os.path.join(build_dir,
            os.path.splitext(os.path.basename(url))[0])
    shutil.move(os.path.join(ffmpeg_dir, "presets"),
            os.path.join(env_dir, "ffmpeg-presets"))

    for exe_name in ("ffmpeg.exe", "ffplay.exe", "ffprobe.exe"):
        shutil.move(os.path.join(ffmpeg_dir, "bin", exe_name),
                os.path.join(scripts_dir, exe_name))


def install_ffmpeg2theora():
    url = "http://v2v.cc/~j/ffmpeg2theora/ffmpeg2theora-0.28.exe"
    exe_name = os.path.basename(url)
    download_path = download_url(url)
    check_call("chmod", "+x", download_path)
    shutil.move(download_path, os.path.join(scripts_dir, exe_name))

def main():
    parse_args()
    make_env_dir()
    with build_dir_context():
        install_lessmsi()
        install_python()
        install_virtualenv()
        install_py2exe()
        install_pygtk()
        install_ffmpeg()
        install_ffmpeg2theora()

if __name__ == '__main__':
    main()

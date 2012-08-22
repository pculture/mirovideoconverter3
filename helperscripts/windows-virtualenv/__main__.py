import contextlib
import hashlib
import os
import sys
import urllib
import urlparse
import shutil
import subprocess
import time
import zipfile
from optparse import OptionParser

env_dir = build_dir = site_packages_dir = scripts_dir = python_dir = None
working_dir = downloads_dir = None
options = args = None

# list of (md5 hash, url) tuples for all files that we download
download_info = [
    ('1694578c49e56eb1dce494408666e465',
        'http://lessmsi.googlecode.com/files/lessmsi-v1.0.8.zip'),
    ('c846d7a5ed186707d3675564a9838cc2', 
        'http://python.org/ftp/python/2.7.3/python-2.7.3.msi'),
    ('788df97c3ceb11368c3a938e5acef0b2', 
        ('http://downloads.sourceforge.net'
            '/project/py2exe/py2exe/0.6.9/py2exe-0.6.9.zip')),
    ('4bddf847f81d8de2d73048b113da3dd5', 
        ('http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/'
            'pygtk-all-in-one-2.24.2.win32-py2.7.msi')),
    ('9633cf25444f41b2fb78b0bb3f509ec3',
        ('http://ffmpeg.zeranoe.com/builds/win32/static/'
            'ffmpeg-20120426-git-a4b58fd-win32-static.7z')),
    ('d7e43beabc017a7d892a3d6663e988d4',
        'http://sourceforge.net/projects/nsis/files/'
        'NSIS%202/2.46/nsis-2.46.zip/download'),
    ('9aa6c2d7229a37a3996270bff411ab22',
        'http://win32.libav.org/win32/libav-win32-20120821.7z'),
]

def get_download_hash(url):
    """Get the md5 hash value for a downloaded file.

    :param url: url for the download
    :returns: md5 hash of the contents of the file, or None if no file found
    """
    download_path = get_download_path(url)
    md5 = hashlib.md5()
    block_size = 1024 * 10
    if not os.path.exists(download_path):
        return None
    with open(download_path, 'rb') as f:
        data = f.read(block_size)
        while data:
            md5.update(data)
            data = f.read(block_size)
    return md5.hexdigest()


def download_files():
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    for md5hash, url in download_info:
        download_path = get_download_path(url)
        if os.path.exists(download_path):
            download_hash = get_download_hash(url)
            if download_hash == md5hash:
                continue
            else:
                writeout("md5 hash verification failed")
                writeout("  %s", url)
                writeout("  correct: %s", md5hash)
                writeout("  downloaded: %s", download_hash)
        download_url(url)

def download_url(url):
    """Download a url to the build directory."""

    download_path = get_download_path(url)
    basename = os.path.basename(download_path)
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


def get_download_path(url):
    """Get the path to a downloaded file.

    :param url:
    """
    parsed_url = urlparse.urlparse(url)
    if parsed_url.netloc == 'sourceforge.net':
        # sourceforge adds an extra "/download" at the end of the url
        basename = os.path.basename(os.path.dirname(parsed_url.path))
    else:
        # default case
        basename = os.path.basename(parsed_url.path)
    return os.path.join(downloads_dir, basename)


def setup_global_dirs(parser_args):
    global env_dir, working_dir, build_dir, site_packages_dir, scripts_dir
    global python_dir, downloads_dir

    env_dir = os.path.abspath(parser_args[0])
    working_dir = os.getcwd()
    downloads_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'downloads',
                'windows-virtualenv'))
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

def install_nsis():
    url = ('http://sourceforge.net/projects/nsis/files/'
            'NSIS%202/2.46/nsis-2.46.zip/download')
    zip_path = get_download_path(url)
    # extract directory to the env directory since all files in the archive
    # are inside nsis-2.46 directory
    extract_zip(zip_path, env_dir)

def install_lessmsi():
    url = "http://lessmsi.googlecode.com/files/lessmsi-v1.0.8.zip"
    zip_path = get_download_path(url)
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
    download_path = get_download_path(url)
    build_path = os.path.join(build_dir, 'Python')
    run_lessmsi(download_path, build_path)
    shutil.move(os.path.join(build_path, "SourceDir"), python_dir)

def install_py2exe():
    url = ("http://downloads.sourceforge.net"
            "/project/py2exe/py2exe/0.6.9/py2exe-0.6.9.zip")
    zip_path = get_download_path(url)
    extract_zip(zip_path, os.path.join(build_dir, 'py2exe'))
    writeout("* Installing py2exe")
    os.chdir(os.path.join(build_dir, 'py2exe', 'py2exe-0.6.9'))
    check_call(os.path.join(scripts_dir, "python.exe"), 'setup.py', 'install')
    os.chdir(working_dir)

def install_pygtk():
    url = ('http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/'
            'pygtk-all-in-one-2.24.2.win32-py2.7.msi')
    msi_path = get_download_path(url)
    build_path = os.path.join(build_dir, 'pygtk-all-in-one')
    run_lessmsi(msi_path, build_path)

    source_package_dir = os.path.join(build_path, "SourceDir", "Lib",
            "site-packages")
    writeout("* Copying pygtk site-packages")
    movetree(source_package_dir, site_packages_dir)

def install_ffmpeg():
    url = ("http://ffmpeg.zeranoe.com/builds/win32/static/"
            "ffmpeg-20120426-git-a4b58fd-win32-static.7z")
    download_path = get_download_path(url)
    check_call(options.seven_zip_path, "x", download_path, '-o' + build_dir)

    archive_dir = os.path.join(build_dir,
            os.path.splitext(os.path.basename(url))[0])
    dest_dir = os.path.join(env_dir, "ffmpeg")

    os.mkdir(dest_dir)
    shutil.move(os.path.join(archive_dir, "presets"),
            os.path.join(dest_dir, "presets"))

    for exe_name in ("ffmpeg.exe", "ffplay.exe", "ffprobe.exe"):
        shutil.move(os.path.join(archive_dir, "bin", exe_name),
                os.path.join(dest_dir, exe_name))

def install_avconv():
    # We use a nightly build of avconv because I (BDK) couldn't find any
    # official builds after version 7.7, released in June 2011
    url = 'http://win32.libav.org/win32/libav-win32-20120821.7z'
    download_path = get_download_path(url)
    check_call(options.seven_zip_path, "x", download_path, '-o' + build_dir)

    archive_dir = os.path.join(build_dir,
            os.path.splitext(os.path.basename(url))[0])
    dest_dir = os.path.join(env_dir, "avconv")
    bin_dir = os.path.join(archive_dir, "usr", "bin")
    lib_dir = os.path.join(archive_dir, "usr", "lib")
    preset_dir = os.path.join(archive_dir, "usr", "share", "avconv")

    os.mkdir(dest_dir)
    for src_dir in (bin_dir, lib_dir, preset_dir):
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), 
                    os.path.join(dest_dir, filename))


def main():
    parse_args()
    make_env_dir()
    download_files()
    with build_dir_context():
        install_lessmsi()
        install_python()
        install_virtualenv()
        install_py2exe()
        install_pygtk()
        install_ffmpeg()
        install_avconv()
        install_nsis()

if __name__ == '__main__':
    main()

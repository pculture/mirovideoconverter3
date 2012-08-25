import logging
import os
import sys

from mvc import execute

ffmpeg_version = None

_search_path_extra = []
def add_to_search_path(directory):
    """Add a path to the list of paths that which() searches."""
    _search_path_extra.append(directory)

def which(name):
    if sys.platform == 'win32':
        name = name + '.exe' # we're looking for ffmpeg.exe in this case
    if sys.platform == 'darwin' and 'Contents/Resources' in __file__:
        # look for a bundled version
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', '..', 'Helpers', name)
        if os.path.exists(path):
            return path
    dirs_to_search = os.environ['PATH'].split(os.pathsep)
    dirs_to_search += _search_path_extra
    for dirname in dirs_to_search:
        fullpath = os.path.join(dirname, name)
        # XXX check for +x bit
        if os.path.exists(fullpath):
            return fullpath
    logging.warn("Can't find path to %s (searched in %s)", name,
            dirs_to_search)

def memoize(func):
    cache = []
    def wrapper():
        if not cache:
            cache.append(func())
        return cache[0]
    return wrapper

@memoize
def get_ffmpeg_executable_path():
    avconv = which('avconv')
    if avconv is not None:
       return avconv
    return which("ffmpeg")

def get_ffmpeg_version():
    global ffmpeg_version
    if ffmpeg_version is None:
        commandline = [get_ffmpeg_executable_path(), '-version']
        p = execute.Popen(commandline, stderr=open(os.devnull, "wb"))
        stdout, _ = p.communicate()
        lines = stdout.split('\n')
        version = lines[0].rsplit(' ', 1)[1].split('.')
        def maybe_int(v):
            try:
                return int(v)
            except ValueError:
                return v
        ffmpeg_version = tuple(maybe_int(v) for v in version)
    return ffmpeg_version

def customize_ffmpeg_parameters(params):
    """Takes a list of parameters and modifies it based on
    platform-specific issues.  Returns the newly modified list of
    parameters.

    :param params: list of parameters to modify

    :returns: list of modified parameters that will get passed to
        ffmpeg
    """
    if get_ffmpeg_version() < (0, 8):
        # Fallback for older versions of FFmpeg (Ubuntu Natty, in particular).
        # see also #18969
        params = ['-vpre' if i == '-preset' else i for i in params]
        try:
            profile_index = params.index('-profile:v')
        except ValueError:
            pass
        else:
            if params[profile_index + 1] == 'baseline':
                params[profile_index:profile_index+2] = [
                    '-coder', '0', '-bf', '0', '-refs', '1',
                    '-flags2', '-wpred-dct8x8']
    return params

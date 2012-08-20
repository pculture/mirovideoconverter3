import os
import subprocess
import sys

ffmpeg_version = None

def which(name):
    if sys.platform == 'win32':
        name = name + '.exe' # we're looking for ffmpeg.exe in this case
    if sys.platform == 'darwin' and 'Contents/Resources' in __file__:
        # look for a bundled version
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', '..', 'Helpers', name)
        if os.path.exists(path):
            return path
    for dirname in os.environ['PATH'].split(os.pathsep):
        fullpath = os.path.join(dirname, name)
        # XXX check for +x bit
        if os.path.exists(fullpath):
            return fullpath

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
        p = subprocess.Popen(commandline,
                             stdout=subprocess.PIPE,
                             stderr=file(os.devnull, "wb"))
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

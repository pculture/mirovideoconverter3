import os

def which(name):
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
    return which("ffmpeg")

@memoize
def get_ffmpeg2theora_executable_path():
    return which("ffmpeg2theora")

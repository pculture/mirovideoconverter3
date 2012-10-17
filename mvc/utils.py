import ctypes
import itertools
import sys

def hms_to_seconds(hours, minutes, seconds):
    return (hours * 3600 +
            minutes * 60 +
            seconds)


def round_even(num):
    """This takes a number, converts it to an integer, then makes
    sure it's even.

    Additional rules: this helper always rounds down to avoid stray black
    pixels (see bz18122).

    This function makes sure that the value returned is always >= 0.
    """
    num = int(num)
    val = num - (num % 2)
    return val if val > 0 else 0


def rescale_video((source_width, source_height),
                  (target_width, target_height),
                  dont_upsize=True):
    """
    Rescale a video given a (width, height) target.  This returns the largest
    (width, height) which maintains the original aspect ratio while fitting
    within the target size.

    If dont_upsize is set, then don't resize it such that the rescaled size
    will be larger than the original size.
    """
    if source_width is None or source_height is None:
        return (round_even(target_width), round_even(target_height))

    if (dont_upsize and
        (source_width <= target_width or source_height <= target_height)):
        return (round_even(source_width), round_even(source_height))

    width_ratio = float(source_width) / float(target_width)
    height_ratio = float(source_height) / float(target_height)
    ratio = max(width_ratio, height_ratio)
    return round_even(source_width / ratio), round_even(source_height / ratio)

def line_reader(handle):
    """Builds a line reading generator for the given handle.  This
    generator breaks on empty strings, \\r and \\n.

    This a little weird, but it makes it really easy to test error
    checking and progress monitoring.
    """
    def _readlines():
        chars = []
        c = handle.read(1)
        while True:
            if c in ["", "\r", "\n"]:
                if chars:
                    yield "".join(chars)
                if not c:
                    break
                chars = []
            else:
                chars.append(c)
            c = handle.read(1)
    return _readlines()


class Matrix(object):
    """2 Dimensional matrix.

    Matrix objects are accessed like a list, except tuples are used as
    indices, for example:

    >>> m = Matrix(5, 5)
    >>> m[3, 4] = 'foo'
    >>> m
    None, None, None, None, None
    None, None, None, None, None
    None, None, None, None, None
    None, None, None, None, None
    None, None, None, 'foo', None
    """

    def __init__(self, columns, rows, initial_value=None):
        self.columns = columns
        self.rows = rows
        self.data = [ initial_value ] * (columns * rows)

    def __getitem__(self, key):
        return self.data[(key[0] * self.rows) + key[1]]

    def __setitem__(self, key, value):
        self.data[(key[0] * self.rows) + key[1]] = value

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return "\n".join([", ".join([repr(r)
                                     for r in list(self.row(i))])
                          for i in xrange(self.rows)])

    def remove(self, value):
        """This sets the value to None--it does NOT remove the cell
        from the Matrix because that doesn't make any sense.
        """
        i = self.data.index(value)
        self.data[i] = None

    def row(self, row):
        """Iterator that yields all the objects in a row."""
        for i in xrange(self.columns):
            yield self[i, row]

    def column(self, column):
        """Iterator that yields all the objects in a column."""
        for i in xrange(self.rows):
            yield self[column, i]


class Cache(object):
    def __init__(self, size):
        self.size = size
        self.dict = {}
        self.counter = itertools.count()
        self.access_times = {}
        self.invalidators = {}

    def get(self, key, invalidator=None):
        if key in self.dict:
            existing_invalidator = self.invalidators[key]
            if (existing_invalidator is None or
                not existing_invalidator(key)):
                self.access_times[key] = self.counter.next()
                return self.dict[key]

        value = self.create_new_value(key, invalidator=invalidator)
        self.set(key, value, invalidator=invalidator)
        return value

    def set(self, key, value, invalidator=None):
        if len(self.dict) == self.size:
            self.shrink_size()
        self.access_times[key] = self.counter.next()
        self.dict[key] = value
        self.invalidators[key] = invalidator

    def remove(self, key):
        if key in self.dict:
            del self.dict[key]
            del self.access_times[key]
        if key in self.invalidators:
            del self.invalidators[key]

    def keys(self):
        return self.dict.iterkeys()

    def shrink_size(self):
        # shrink by LRU
        to_sort = self.access_times.items()
        to_sort.sort(key=lambda m: m[1])
        new_dict = {}
        new_access_times = {}
        new_invalidators = {}
        latest_times = to_sort[len(self.dict) // 2:]
        for (key, time) in latest_times:
            new_dict[key] = self.dict[key]
            new_invalidators[key] = self.invalidators[key]
            new_access_times[key] = time
        self.dict = new_dict
        self.access_times = new_access_times

    def create_new_value(self, val, invalidator=None):
        raise NotImplementedError()


def size_string(nbytes):
    # when switching from the enclosure reported size to the
    # downloader reported size, it takes a while to get the new size
    # and the downloader returns -1.  the user sees the size go to -1B
    # which is weird....  better to return an empty string.
    if nbytes == -1 or nbytes == 0:
        return ""

    # FIXME this is a repeat of util.format_size_for_user ...  should
    # probably ditch one of them.
    if nbytes >= (1 << 30):
        value = "%.1f" % (nbytes / float(1 << 30))
        return "%(size)s GB" % {"size": value}
    elif nbytes >= (1 << 20):
        value = "%.1f" % (nbytes / float(1 << 20))
        return "%(size)s MB" % {"size": value}
    elif nbytes >= (1 << 10):
        value = "%.1f" % (nbytes / float(1 << 10))
        return "%(size)s KB" % {"size": value}
    else:
        return "%(size)s B" % {"size": nbytes}

def convert_path_for_subprocess(path):
    """Convert a path to a form suitable for passing to a subprocess.

    This method converts unicode paths to bytestrings according to the system
    fileencoding.  On windows, it converts the path to a short filename for
    maximum compatibility
    """
    if not isinstance(path, unicode):
	# path already is a bytestring, just return it
	return path
    if sys.platform != 'win32':
	return path.encode(sys.getfilesystemencoding())
    else:
	buf_size = 1024
	short_path_buf = ctypes.create_unicode_buffer(buf_size)
	ctypes.windll.kernel32.GetShortPathNameW(path,
		short_path_buf, buf_size)
	return short_path_buf.value.decode('ascii')

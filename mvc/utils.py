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
                  (target_width, target_height)):
    """
    Rescale a video given a (width, height) target.  This returns the largest
    (width, height) which maintains the original aspect ratio while fitting
    within the target size.
    """
    if not source_width or not source_height:
        return (target_width, target_height)

    if (source_width <= target_width and
        source_height <= target_height):
        return (source_width, source_height)

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



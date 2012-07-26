"""mvc.windows.exelogging -- handle logging inside an exe file

Most of this is copied from the Miro code.
"""

import logging
import os
import sys
import tempfile
from StringIO import StringIO
from logging.handlers import RotatingFileHandler

class ApatheticRotatingFileHandler(RotatingFileHandler):
    """The whole purpose of this class is to prevent rotation errors
    from percolating up into stdout/stderr and popping up a dialog
    that's not particularly useful to users or us.
    """
    def doRollover(self):
        # If you shut down Miro then start it up again immediately
        # afterwards, then we get in this squirrely situation where
        # the log is opened by another process.  We ignore the
        # exception, but make sure we have an open file.  (bug #11228)
        try:
            RotatingFileHandler.doRollover(self)
        except WindowsError:
            if not self.stream or self.stream.closed:
                self.stream = open(self.baseFilename, "a")
            try:
                RotatingFileHandler.doRollover(self)
            except WindowsError:
                pass

    def shouldRollover(self, record):
        # if doRollover doesn't work, then we don't want to find
        # ourselves in a situation where we're trying to do things on
        # a closed stream.
        if self.stream.closed:
            self.stream = open(self.baseFilename, "a")
        return RotatingFileHandler.shouldRollover(self, record)

    def handleError(self, record):
        # ignore logging errors that occur rather than printing them to
        # stdout/stderr which isn't helpful to us

        pass
class AutoLoggingStream(StringIO):
    """Create a stream that intercepts write calls and sends them to
    the log.
    """
    def __init__(self, logging_callback, prefix):
        StringIO.__init__(self)
        # We init from StringIO to give us a bunch of stream-related
        # methods, like closed() and read() automatically.
        self.logging_callback = logging_callback
        self.prefix = prefix

    def write(self, data):
        if isinstance(data, unicode):
            data = data.encode('ascii', 'backslashreplace')
        if data.endswith("\n"):
            data = data[:-1]
        if data:
            self.logging_callback(self.prefix + data)

FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
def setup_logging():
    """Setup logging for when we're running inside a windows exe.

    The object here is to avoid logging anything to stderr/stdout since
    windows will consider that an error.
    """

    log_path = os.path.join(tempfile.gettempdir(), "MVC.log")
    rotater = ApatheticRotatingFileHandler(
        log_path, mode="a", maxBytes=100000, backupCount=5)

    formatter = logging.Formatter(FORMAT)
    rotater.setFormatter(formatter)
    logger = logging.getLogger('')
    logger.addHandler(rotater)
    logger.setLevel(logging.INFO)
    rotater.doRollover()
    sys.stdout = AutoLoggingStream(logging.warn, '(from stdout) ')
    sys.stderr = AutoLoggingStream(logging.error, '(from stderr) ')

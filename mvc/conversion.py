import collections
import os
import time
import tempfile
import threading
import shutil
import subprocess
import logging

def line_reader(handle, block_size=1):
    """Builds a line reading generator for the given handle.  This
    generator breaks on empty strings, \\r and \\n.

    This a little weird, but it makes it really easy to test error
    checking and progress monitoring.
    """
    def _readlines():
        chars = []
        c = handle.read(block_size)
        while c:
            if c in ["", "\r", "\n"]:
                yield "".join(chars)
                chars = []
            else:
                chars.append(c)
            c = handle.read(block_size)
    return _readlines()


class Conversion(object):

    def __init__(self, video, converter, manager):
        self.video = video
        self.converter = converter
        self.manager = manager
        self.output = os.path.join(
            os.path.dirname(video.filename),
            converter.get_output_filename(video))
        self.thread = None
        self.status = 'initialized'
        self.error = None
        self.started_at = None
        self.duration = None
        self.progress = None
        self.eta = None
        self.listeners = set()

    def listen(self, f):
        self.listeners.add(f)

    def unlisten(self, f):
        self.listeners.remove(f)

    def notify_listeners(self):
        self.manager.notify_queue.add(self)

    def run(self):
        self.temp_fd, self.temp_output = tempfile.mkstemp()
        self.thread = threading.Thread(target=self._thread,
                                       name="Conversion: %s => %s (%s)" % (
                self.video.filename, self.temp_output, self.converter.name))
        self.thread.setDaemon(True)
        self.thread.start()

    def _thread(self):
        try:
            popen = subprocess.Popen(self.get_subprocess_arguments(
                    self.temp_output),
                                     bufsize=1,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
            self.started_at = time.time()
            self.status = 'converting'
            for line in line_reader(popen.stdout):
                status = self.converter.process_status_line(line)
                if status is None:
                    continue
                updated = False
                if 'finished' in status:
                    self.error = status.get('error', None)
                    break
                if 'duration' in status:
                    updated = True
                    self.duration = float(status['duration'])
                    if self.progress is None:
                        self.progress = 0.0
                if 'progress' in status:
                    updated = True
                    self.progress = min(float(status['progress']),
                                        self.duration)

                if updated:
                    if self.duration:
                        self.progress_percent = self.progress / self.duration
                        if 0 < self.progress_percent < 1.0:
                            progress = self.progress_percent * 100
                            elapsed = time.time() - self.started_at
                            time_per_percent = elapsed / progress
                            self.eta = int(time_per_percent * (100 - progress))
                        else:
                            self.eta = 0
                    else:
                        self.progress_percent = 0.0
                        self.eta = 0
                    self.notify_listeners()

            self.progress_percent = 1.0
            self.eta = 0
            popen.wait()
        except Exception, e:
            logging.exception('in %s' % (self.thread.name,))
            self.error = str(e)

        if self.error is None:
            self.status = 'staging'
            self.notify_listeners()
            shutil.move(self.temp_output, self.output)
            os.close(self.temp_fd)
            self.status = 'finished'
        else:
            os.unlink(self.temp_output)
            os.close(self.temp_fd)
            self.status = 'failed'
        self.notify_listeners()

    def get_subprocess_arguments(self, output):
        return ([self.converter.get_executable()] +
                self.converter.get_arguments(self.video, output))


class ConversionManager(object):
    def __init__(self):
        self.notify_queue = set()
        self.running = False

    def start_conversion(self, video, converter):
        c = Conversion(video, converter, self)
        self.in_progress.add(c)
        c.run()
        self.running = True
        return c

    def check_notifications(self):
        # get the changed items, but only notify once
        self.notify_queue, changed = set(), self.notify_queue

        for converter in changed:
            for listener in converter.listeners:
                listener(converter)
            if converter.status in ('finished', 'failed'):
                self.in_progress.remove(converter)
                if not self.in_progress:
                    self.running = False


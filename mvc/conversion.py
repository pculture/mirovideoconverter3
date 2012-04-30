import collections
import errno
import os
import time
import tempfile
import threading
import shutil
import subprocess
import logging

from mvc.utils import line_reader

class Conversion(object):

    def __init__(self, video, converter, manager, output_dir=None):
        self.video = video
        self.converter = converter
        self.manager = manager
        if output_dir is None:
            output_dir = os.path.dirname(video.filename)
        self.output = os.path.join(output_dir,
                                   converter.get_output_filename(video))
        self.lines = []
        self.thread = None
        self.popen = None
        self.status = 'initialized'
        self.error = None
        self.started_at = None
        self.duration = None
        self.progress = None
        self.progress_percent = None
        self.eta = None
        self.listeners = set()

    def __str__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return u'<Conversion (%s) %r -> %r>' % (
            self.converter.name, self.video.filename, self.output)

    def listen(self, f):
        self.listeners.add(f)

    def unlisten(self, f):
        self.listeners.remove(f)

    def notify_listeners(self):
        self.manager.notify_queue.add(self)

    def run(self):
        self.temp_fd, self.temp_output = tempfile.mkstemp()
        self.thread = threading.Thread(target=self._thread,
                                       name="Thread:%s" % (self,))
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        if not self.popen:
            return
        self.error = 'manually stopped'
        try:
            self.popen.kill()
            self.popen.wait()
        except EnvironmentError, e:
            logging.exception('while stopping %s' % (self,))
            self.error = str(e)

    def _thread(self):
        os.unlink(self.temp_output) # unlink temp file before FFmpeg gets it
        try:
            self.popen = subprocess.Popen(self.get_subprocess_arguments(
                    self.temp_output),
                                          bufsize=1,
                                          stdin=open(os.devnull, 'rb'),
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
            self.process_output()
            self.popen.wait()
        except OSError, e:
            if e.errno == errno.ENOENT:
                self.error = '%r does not exist' % (
                    self.converter.get_executable(),)
            else:
                logging.exception('OSError in %s' % (self.thread.name,))
                self.error = str(e)
        except Exception, e:
            logging.exception('in %s' % (self.thread.name,))
            self.error = str(e)

        self.finalize()

    def process_output(self):
        self.started_at = time.time()
        self.status = 'converting'
        # We use line_reader, rather than just iterating over the file object,
        # because iterating over the file object gives us all the lines when
        # the process ends, and we're looking for real-time updates.
        for line in line_reader(self.popen.stdout):
            self.lines.append(line) # for debugging, if needed
            status = self.converter.process_status_line(self.video, line)
            if status is None:
                continue
            updated = set()
            if 'finished' in status:
                self.error = status.get('error', None)
                break
            if 'duration' in status:
                updated.update(('duration', 'progress'))
                self.duration = float(status['duration'])
                if self.progress is None:
                    self.progress = 0.0
            if 'progress' in status:
                updated.add('progress')
                self.progress = min(float(status['progress']),
                                    self.duration)
            if 'eta' in status:
                updated.add('eta')
                self.eta = float(status['eta'])

            if updated:
                if self.duration:
                    self.progress_percent = self.progress / self.duration
                else:
                    self.progress_percent = 0.0
                if 'eta' not in updated:
                    if self.duration and 0 < self.progress_percent < 1.0:
                        progress = self.progress_percent * 100
                        elapsed = time.time() - self.started_at
                        time_per_percent = elapsed / progress
                        self.eta = float(
                            time_per_percent * (100 - progress))
                    else:
                        self.eta = 0.0

                self.notify_listeners()

    def finalize(self):
        self.progress = self.duration
        self.progress_percent = 1.0
        self.eta = 0

        if self.error is None:
            self.status = 'staging'
            self.notify_listeners()
            try:
                shutil.move(self.temp_output, self.output)
                os.close(self.temp_fd)
            except EnvironmentError, e:
                logging.exception('while trying to move %r to %r after %s',
                                  self.temp_output, self.output, self)
                self.error = str(e)
                self.status = 'failed'
            else:
                self.status = 'finished'
        else:
            try:
                os.close(self.temp_fd)
                os.unlink(self.temp_output)
            except EnvironmentError:
                pass # ignore errors removing temp files; they may not have
                     # been created
            self.status = 'failed'
        self.notify_listeners()

    def get_subprocess_arguments(self, output):
        return ([self.converter.get_executable()] +
                list(self.converter.get_arguments(self.video, output)))


class ConversionManager(object):
    def __init__(self, simultaneous=None):
        self.notify_queue = set()
        self.in_progress = set()
        self.waiting = collections.deque()
        self.simultaneous = simultaneous
        self.running = False

    def start_conversion(self, video, converter):
        c = Conversion(video, converter, self)
        if (self.simultaneous is not None and
            len(self.in_progress) >= self.simultaneous):
            self.waiting.append(c)
        else:
            self.in_progress.add(c)
            c.run()
            self.running = True
        return c

    def check_notifications(self):
        if not self.running:
            # don't bother checking if we're not running
            return

        self.notify_queue, changed = set(), self.notify_queue

        for conversion in changed:
            for listener in conversion.listeners:
                listener(conversion)
            if conversion.status in ('finished', 'failed'):
                self.conversion_finished(conversion)

    def conversion_finished(self, conversion):
        self.in_progress.discard(conversion)
        while (self.waiting and self.simultaneous is not None and
               len(self.in_progress) < self.simultaneous):
            c = self.waiting.popleft()
            self.in_progress.add(c)
            c.run()
        if not self.in_progress:
            self.running = False

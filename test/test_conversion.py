import json
import os.path
import shutil
import sys
import tempfile
import time

from mvc import video
from mvc import converter
from mvc import conversion

import base


class FakeConverterInfo(converter.ConverterInfo):

    extension = 'fake'

    def get_executable(self):
        return sys.executable

    def get_arguments(self, video, output):
        return ['-u', os.path.join(
                os.path.dirname(__file__), 'testdata', 'fake_converter.py'),
                video.filename, output]

    def process_status_line(self, video, line):
        return json.loads(line)


class ConversionManagerTest(base.Test):

    def setUp(self):
        base.Test.setUp(self)
        self.manager = conversion.ConversionManager()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        base.Test.tearDown(self)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial(self):
        self.assertEqual(self.manager.notify_queue, set())
        self.assertEqual(self.manager.in_progress, set())
        self.assertFalse(self.manager.running)

    def test_conversion(self):
        converter = FakeConverterInfo('Fake')
        output = os.path.join(self.temp_dir, 'webm-0.webm')
        shutil.copyfile(os.path.join(self.testdata_dir, 'webm-0.webm'),
                        output)
        vf = video.VideoFile(output)
        changes = []
        def changed(c):
            changes.append(
                {'status': c.status,
                 'duration': c.duration,
                 'progress': c.progress,
                 'eta': c.eta
                 })
        c = self.manager.start_conversion(vf, converter)
        c.listen(changed)
        self.assertTrue(self.manager.running)
        self.assertTrue(c in self.manager.in_progress)
        finish_by = time.time() + 5
        while time.time() < finish_by and self.manager.running:
            self.manager.check_notifications()
            time.sleep(0.01) # spin a lot to get all the updates
        self.assertFalse(self.manager.running)
        self.assertTrue(c.status, 'finished')
        self.assertTrue(os.path.exists(c.output))
        self.assertEqual(changes, [
                {'status': 'converting', 'duration': 5.0, 'eta': 5.0,
                 'progress': 0.0},
                {'status': 'converting', 'duration': 5.0, 'eta': 4.0,
                 'progress': 1.0},
                {'status': 'converting', 'duration': 5.0, 'eta': 3.0,
                 'progress': 2.0},
                {'status': 'converting', 'duration': 5.0, 'eta': 2.0,
                 'progress': 3.0},
                {'status': 'converting', 'duration': 5.0, 'eta': 1.0,
                 'progress': 4.0},
                {'status': 'finished', 'duration': 5.0, 'eta': 0.0,
                 'progress': 5.0}
                ])

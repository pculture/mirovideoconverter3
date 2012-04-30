from StringIO import StringIO

from mvc import utils

import base

class UtilsTest(base.Test):

    def test_hms_to_seconds(self):
        self.assertEqual(utils.hms_to_seconds(3, 2, 1),
                         3 * 3600 +
                         2 * 60 +
                         1)

    def test_hms_to_seconds_floats(self):
        self.assertEqual(utils.hms_to_seconds(3.0, 2.0, 1.5),
                         3 * 3600 +
                         2 * 60 +
                         1.5)

    def test_round_even(self):
        self.assertEqual(utils.round_even(-1), 0)
        self.assertEqual(utils.round_even(0), 0)
        self.assertEqual(utils.round_even(1), 0)
        self.assertEqual(utils.round_even(2), 2)
        self.assertEqual(utils.round_even(2.5), 2)
        self.assertEqual(utils.round_even(3), 2)

    def test_rescale_video(self):
        target = (1024, 768)
        self.assertEqual(utils.rescale_video(target, target),
                         target)
        self.assertEqual(utils.rescale_video((512, 384), target), # small
                         (512, 384))
        self.assertEqual(utils.rescale_video((2048, 1536), target), # big
                         target)
        self.assertEqual(utils.rescale_video((1400, 768), target), # widescreen
                         (1024, 560))

    def test_line_reader(self):
        lines = """line1
line2
line3\rline4\r
line5"""
        expected = ['line1', 'line2', 'line3', 'line4', 'line5']
        self.assertEqual(list(utils.line_reader(StringIO(lines))), expected)


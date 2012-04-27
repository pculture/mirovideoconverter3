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

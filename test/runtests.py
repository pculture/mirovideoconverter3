try:
    import mvc
except ImportError:
    import os.path, sys
    mvc_path = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(mvc_path)

from test_video import *
from test_converter import *
from test_conversion import *
from test_utils import *

if __name__ == "__main__":
    import unittest
    from mvc.widgets import initialize
    initialize(None)
    unittest.main()

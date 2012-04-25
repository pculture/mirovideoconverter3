try:
    import mvc
except ImportError:
    import os.path, sys
    mvc_path = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(mvc_path)

from test_video import *

if __name__ == "__main__":
    import unittest
    unittest.main()

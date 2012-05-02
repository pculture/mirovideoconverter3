import sys

if sys.platform == 'darwin':
    from .osx import *
else:
    from .gtk import *

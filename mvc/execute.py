"""execute.py -- Run executable programs.

mvc.execute wraps the standard subprocess module in for MVC.
"""

import os
import subprocess
import sys

CalledProcessError = subprocess.CalledProcessError

def default_popen_args():
    retval = {
        'stdin': open(os.devnull, 'rb'),
        'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT,
    }
    if sys.platform == 'win32':
        retval['startupinfo'] = subprocess.STARTUPINFO()
        retval['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return retval

class Popen(subprocess.Popen):
    """subprocess.Popen subclass that adds MVC default behavior.

    By default we:
      - Use a /dev/null equivilent for stdin
      - Use a pipe for stdout
      - Redirect stderr to stdout
      - use STARTF_USESHOWWINDOW to not open a console window on win32

    These are just defaults though, they can be overriden by passing different
    values to the constructor
    """
    def __init__(self, commandline, **kwargs):
        final_args = default_popen_args()
        final_args.update(kwargs)
        subprocess.Popen.__init__(self, commandline, **final_args)

def check_output(commandline, **kwargs):
    """MVC version of subprocess.check_output.

    This performs the same default behavior as the Popen class.
    """
    final_args = default_popen_args()
    # check_output doesn't use stdout
    del final_args['stdout']
    final_args.update(kwargs)
    return subprocess.check_output(commandline, **final_args)

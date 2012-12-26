import sys

if sys.platform.startswith("linux"):
    script = 'setup-linux.py'
elif sys.platform.startswith("win32"):
    script = 'setup-windows.py'
elif sys.platform.startswith("darwin"):
    script = 'setup-osx'
else:
    sys.stderr.write("Unknown platform: %s" % sys.platform)

execfile(script)

#!/bin/bash

# This script installs dependencies for building and running MVC on
# OS X.  It requires MacPorts <http://www.macports.org/>.
#
# You run this sript AT YOUR OWN RISK.  Read through the whole thing
# before running it!
#
# This script must be run with sudo.

# Last updated:    2012-04-30
# Last updated by: Paul Swartz

port install python27 py27-pyobjc py27-pyobj-cocoa py27-py2app ffmpeg-devel
curl -o ffmpeg2theora-0.28.pkg http://v2v.cc/~j/ffmpeg2theora/ffmpeg2theora-0.28.pkg
installer -pkg ffmpeg2theora-0.28.pkg -target /
rm ffmpeg2theora-0.28.pkg

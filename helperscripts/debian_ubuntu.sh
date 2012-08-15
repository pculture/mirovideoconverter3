#!/bin/bash

# This script installs dependencies for building and running MVC on
# Debian Wheezy (currently testing).
#
# You run this sript AT YOUR OWN RISK.  Read through the whole thing
# before running it!
#
# This script must be run with sudo.

# Last updated:    2012-04-26
# Last updated by: Paul Swartz

apt-get install \
    python-gtk2 \
    ffmpeg

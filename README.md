# Miro Video Converter 3 [![Build Status](https://secure.travis-ci.org/pculture/mirovideoconverter3.png)](http://travis-ci.org/pculture/mirovideoconverter3) #

## About ##

[Miro Video Converter](http://www.mirovideoconverter.com) is super simple way to convert almost any video to MP4, WebM (vp8), Ogg Theora, or for Android, iPhone, and more.

This is an in-progress rewrite of the existing application.  If you're looking for that code, it's [over here](http://github.com/pculture/mirovideoconverter).

## Requirements ##

* Python 2.7
* FFmpeg
* GTK2 and its Python bindings (for the GTK UI)

A copy of qtfaststart is bundled within this application, it is licensed
under the GPL version 3 or (at your option) any later version.

The copy was retrieved at:

https://github.com/danielgtaylor/qtfaststart identified by commit eb8594d.

On Debian/Ubuntu, that looks like:

    $ sudo apt-get install -y python2.7 ffmpeg ffmpeg2theora python-gtk2

## Running ##

    $ git clone http://github.com/pculture/mirovideoconverter3
    $ cd mirovideoconverter3
    $ python2.7 test/runtests.py # Unit tests
    $ python2.7 -m mvc.ui.widgets # GTK interface
    $ python2.7 -m mvc.ui.console [filename to convert] [conversion type] # console interface

## Contact ##

If you'd like to help out, the best way to contact us is either the [develop mailing list](http://mailman.pculture.org/listinfo/develop) or the `#miro-hackers` IRC channel on Freenode.

## Other resources ##

* [Wiki page](http://develop.participatoryculture.org/index.php/MVCStart/MVC3Overhaul)

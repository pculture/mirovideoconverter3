#!/bin/sh

~/src/miro/miro/sandbox_20120516/Frameworks/Python.framework/Versions/2.7/bin/python setup.py develop

~/src/miro/miro/sandbox_20120516/Frameworks/Python.framework/Versions/2.7/bin/python setup.py py2app

codesign -fs '3rd Party Mac Developer Application: Participatory Culture Foundation' --entitlements sandbox.entitlements dist/widgets.app

codesign -fs '3rd Party Mac Developer Application: Participatory Culture Foundation' --entitlements ffmpeg.entitlements dist/widgets.app/Contents/Helpers/ffmpeg

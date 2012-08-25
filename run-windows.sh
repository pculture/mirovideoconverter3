#!/bin/sh

if [ ! -e mvc-env ] ; then
        echo "MVC virtualenv is not present.  Run "
        echo
        echo "   python helperscripts/windows-virtualenv/ mvc-env"
        echo
        echo "to build it"
        exit 1
fi

PATH="mvc-env/ffmpeg:mvc-env/avconv:$PATH" PYTHONPATH="." mvc-env/Scripts/python.exe mvc

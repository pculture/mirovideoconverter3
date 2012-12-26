#!/bin/sh

if [ ! -e mvc-env ] ; then
        echo "MVC virtualenv is not present.  Run "
        echo
        echo "   python helperscripts/windows-virtualenv/ mvc-env"
        echo
        echo "to build it"
        exit 1
fi

PYTHONPATH="." mvc-env/Scripts/python.exe setup.py bdist_nsis

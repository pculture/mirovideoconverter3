#!/bin/bash

set -e

if [ -z ${SANDBOX_PATH} ]; then
    echo "you must set SANDBOX_PATH to point to the built miro sandbox"
    exit 1
fi

if [ -z ${BKIT_PATH} ]; then
    echo "you must set BKIT_PATH to point to the miro binary kit"
    exit
fi

export MACOSX_DEPLOYMENT_TARGET=10.6

${SANDBOX_PATH}/Frameworks/Python.framework/Versions/2.7/bin/python setup.py develop

${SANDBOX_PATH}/Frameworks/Python.framework/Versions/2.7/bin/python setup.py py2app

if [ "$1" = "--sign" ]; then
    source sign.sh
fi

if [ "$2" = "--installer" ] ; then
    source build_installer.sh
fi

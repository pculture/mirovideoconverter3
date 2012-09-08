#!/bin/sh

productbuild \
    --component "dist/Miro Video Converter.app" /Applications \
    --sign '3rd Party Mac Developer Installer: Participatory Culture Foundation' \
    --product mvc3_definition.plist mvc3.pkg


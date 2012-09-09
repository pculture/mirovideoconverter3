#!/bin/sh

for i in "dist/Miro Video Converter.app/Contents/Helpers"/*
do
    codesign -fs \
      '3rd Party Mac Developer Application: Participatory Culture Foundation' \
      --entitlements ffmpeg.entitlements "${i}"
done

# Fix up the python framework installation from py2app: it doesn't
# copy over all the files that constitutes it to be a valid framework.
pushd "dist/Miro Video Converter.app/Contents/Frameworks/Python.framework"
ln -sf Versions/Current/Python Python
ln -sf Versions/Current/Resources Resources
ln -sf 2.7 Versions/Current
popd

codesign -fs \
  '3rd Party Mac Developer Application: Participatory Culture Foundation' \
  --entitlements ffmpeg.entitlements \
  "dist/Miro Video Converter.app/Contents/Frameworks/Python.framework/Versions/2.7"

codesign -fs \
  '3rd Party Mac Developer Application: Participatory Culture Foundation' \
  --entitlements sandbox.entitlements "dist/Miro Video Converter.app"



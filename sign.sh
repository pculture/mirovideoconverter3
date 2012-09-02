#!/bin/sh

for i in "dist/Miro Video Converter.app/Contents/Helpers"/*
do
    codesign -fs \
      '3rd Party Mac Developer Application: Participatory Culture Foundation' \
      --entitlements ffmpeg.entitlements "${i}"
done

codesign -fs \
  '3rd Party Mac Developer Application: Participatory Culture Foundation' \
  --entitlements ffmpeg.entitlements \
  "dist/Miro Video Converter.app/Contents/Frameworks/Python.framework/Versions/2.7"

codesign -fs \
  '3rd Party Mac Developer Application: Participatory Culture Foundation' \
  --entitlements sandbox.entitlements "dist/Miro Video Converter.app"



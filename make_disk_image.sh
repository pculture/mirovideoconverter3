#!/bin/sh
#echo "Building app..."
#python2.7 setup.py py2app
echo "Building disk image..."
imgName=`date '+mvc-%Y-%m-%d.dmg'`
imgDirName="dist/img"
imgPath="dist/$imgName"
rm -rf $imgDirName $imgPath
mkdir $imgDirName
cp -r dist/widgets.app $imgDirName/
ln -s /Applications $imgDirName/Applications
echo "Creating DMG file... "
hdiutil create -srcfolder $imgDirName -volname mvc -format UDZO dist/mvc.tmp.dmg
hdiutil convert -format UDZO -imagekey zlib-level=9 -o $imgPath dist/mvc.tmp.dmg
rm dist/mvc.tmp.dmg


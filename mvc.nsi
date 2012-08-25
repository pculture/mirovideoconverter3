
!define PUBLISHER "Participatory Culture Foundation"
!define PUBLISHER_DIR "$PROGRAMFILES\${PUBLISHER}"
!define APP_NAME "Miro Video Converter"
!define EXE_NAME "mvc.exe"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${CONFIG_LONG_APP_NAME}"

outFile "MiroVideoConverter.exe"
InstallDir "${PUBLISHER_DIR}\${APP_NAME}"
 
# default section
section
    SetOutPath $INSTDIR
    WriteUninstaller "$INSTDIR\uninstall.exe"

    File *.pyd
    File *.dll
    File library.zip
    File ${EXE_NAME}
    SetOutPath "$INSTDIR\ffmpeg"
    File /r ffmpeg\*.*
    SetOutPath "$INSTDIR\avconv"
    File /r avconv\*.*
    SetOutPath "$INSTDIR\resources\converters"
    File resources\converters\*.*
    SetOutPath "$INSTDIR\resources\images"
    File resources\images\*.*

    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    # point the new shortcut at the program uninstaller
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"

    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
sectionEnd
 
# uninstaller section start
section "uninstall"
 
    delete "$INSTDIR\uninstall.exe"
    delete "$INSTDIR\*.pyd"
    delete "$INSTDIR\*.dll"
    delete "$INSTDIR\library.zip"
    delete "$INSTDIR\${EXE_NAME}"
    delete "$INSTDIR\resources\converters\*.*"
    delete "$INSTDIR\resources\images\*.*"
    rmdir /r "$INSTDIR\avconv"
    rmdir /r "$INSTDIR\ffmpeg"
    rmdir "$INSTDIR\resources\converters"
    rmdir "$INSTDIR\resources\images"
    rmdir "$INSTDIR\resources"
    rmdir "$INSTDIR"
    rmdir "${PUBLISHER_DIR}"
    rmdir /r "$SMPROGRAMS\${APP_NAME}"
 
# uninstaller section end
sectionEnd

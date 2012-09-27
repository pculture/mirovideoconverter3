; Passed in from command line:
!define  CONFIG_VERSION "0.8.0"

; TODO: Add MIROBAR_EXE
!define CONFIG_PROJECT_URL "http://www.mirovideoconverter.com/"
!define CONFIG_SHORT_APP_NAME "MVC"
!define CONFIG_LONG_APP_NAME  "Miro Video Converter"
!define CONFIG_PUBLISHER "Participatory Culture Foundation"
!define CONFIG_ICON "mvc-logo.ico"
!define CONFIG_EXECUTABLE "mvc.exe"
!define CONFIG_OUTPUT_FILE "MiroVideoConverter.exe"

!define INST_KEY "Software\${CONFIG_PUBLISHER}\${CONFIG_LONG_APP_NAME}"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${CONFIG_LONG_APP_NAME}"

!define UNINSTALL_SHORTCUT "Uninstall ${CONFIG_LONG_APP_NAME}.lnk"
!define MUI_ICON "${CONFIG_ICON}"
!define MUI_UNICON "${CONFIG_ICON}"

;INCLUDES
!addplugindir "${CONFIG_PLUGIN_DIR}"
!addincludedir "${CONFIG_PLUGIN_DIR}"

!include "MUI2.nsh"
!include "nsProcess.nsh"

!define PRODUCT_NAME "${CONFIG_LONG_APP_NAME}"

;GENERAL SETTINGS
Name "${CONFIG_LONG_APP_NAME}"
OutFile "${CONFIG_OUTPUT_FILE}"
InstallDir "$PROGRAMFILES\${CONFIG_PUBLISHER}\${CONFIG_LONG_APP_NAME}"
InstallDirRegKey HKLM "${INST_KEY}" "Install_Dir"
SetCompressor lzma

SetOverwrite on
CRCCheck on

Icon "${CONFIG_ICON}"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Macros
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Function LaunchLink
  SetShellVarContext all
  ExecShell "" "$INSTDIR\${CONFIG_EXECUTABLE}"
FunctionEnd

Function CreateDesktopShortcut
  CreateShortCut "$DESKTOP\${CONFIG_LONG_APP_NAME}.lnk" \
    "$INSTDIR\${CONFIG_EXECUTABLE}" "" "$INSTDIR\${CONFIG_ICON}"
FunctionEnd

Function .onInit
TestRunning:
  ${nsProcess::FindProcess} ${CONFIG_EXECUTABLE} $R0
  StrCmp $R0 0 0 NotRunning
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "It looks like you're already running ${CONFIG_LONG_APP_NAME}.$\n\
    Please shut it down before continuing." \
    IDOK TestRunning
  Goto TestRunning
NotRunning:

FunctionEnd

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Sections                                                                  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Section "-${CONFIG_LONG_APP_NAME}" COM2
  SectionIn RO
  ClearErrors
  SetShellVarContext all

  SetOutPath "$INSTDIR"

  File ${CONFIG_ICON}
  File *.pyd
  File *.dll
  File library.zip
  File ${CONFIG_EXECUTABLE}
  SetOutPath "$INSTDIR\ffmpeg"
  File /r ffmpeg\*.*
  # SetOutPath "$INSTDIR\avconv"
  # File /r avconv\*.*
  SetOutPath "$INSTDIR\resources\converters"
  File resources\converters\*.*
  SetOutPath "$INSTDIR\resources\images"
  File resources\images\*.*
  SetOutPath "$INSTDIR\etc\gtk-2.0"
  File etc\gtk-2.0\gtkrc
  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\engines"
  File lib\gtk-2.0\2.10.0\engines\libclearlooks.dll

  IfErrors 0 files_ok

  MessageBox MB_OK|MB_ICONEXCLAMATION "Installation failed.  An error occured writing to the ${CONFIG_LONG_APP_NAME} Folder."
  Quit
files_ok:
  CreateDirectory "$SMPROGRAMS\${CONFIG_LONG_APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${CONFIG_LONG_APP_NAME}\${CONFIG_LONG_APP_NAME}.lnk" \
    "$INSTDIR\${CONFIG_EXECUTABLE}" "" "$INSTDIR\${CONFIG_ICON}"
  CreateShortCut "$SMPROGRAMS\${CONFIG_LONG_APP_NAME}\${UNINSTALL_SHORTCUT}" \
    "$INSTDIR\uninstall.exe"

SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${INST_KEY}" "InstallDir" $INSTDIR
  WriteRegStr HKLM "${INST_KEY}" "Version" "${CONFIG_VERSION}"
  WriteRegStr HKLM "${INST_KEY}" "" "$INSTDIR\${CONFIG_EXECUTABLE}"

  WriteRegStr HKLM "${UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\${CONFIG_EXECUTABLE}"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion" "${CONFIG_VERSION}"
  WriteRegStr HKLM "${UNINST_KEY}" "URLInfoAbout" "${CONFIG_PROJECT_URL}"
  WriteRegStr HKLM "${UNINST_KEY}" "Publisher" "${CONFIG_PUBLISHER}"

SectionEnd

Section "Uninstall" SEC91

  SetShellVarContext all

  Delete "$INSTDIR\uninstall.exe"
  Delete "$DESKTOP\Miro Video Converter.lnk"
  Delete "$INSTDIR\${CONFIG_ICON}"
  Delete "$INSTDIR\*.pyd"
  Delete "$INSTDIR\*.dll"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\${CONFIG_EXECUTABLE}"
  Delete "$INSTDIR\resources\converters\*.*"
  Delete "$INSTDIR\resources\images\*.*"
  Delete "$INSTDIR\etc\gtk-2.0\gtkrc"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libclearlooks.dll"
  # RMDir /r "$INSTDIR\avconv"
  RMDir /r "$INSTDIR\ffmpeg"
  RMDir "$INSTDIR\lib\gtk-2.0\2.10.0\engines\"
  RMDir "$INSTDIR\lib\gtk-2.0\2.10.0\"
  RMDir "$INSTDIR\lib\gtk-2.0\"
  RMDir "$INSTDIR\lib\"
  RMDir "$INSTDIR\etc\gtk-2.0"
  RMDir "$INSTDIR\etc"
  RMDir "$INSTDIR\resources\converters"
  RMDir "$INSTDIR\resources\images"
  RMDir "$INSTDIR\resources"
  RMDir "$INSTDIR"
  RMDIR "$PROGRAMFILES\${CONFIG_PUBLISHER}"

  RMDir "$PROGRAMFILES\${CONFIG_PUBLISHER}"

  ; Remove Start Menu shortcuts
  Delete "$SMPROGRAMS\${CONFIG_LONG_APP_NAME}\${UNINSTALL_SHORTCUT}"
  Delete "$SMPROGRAMS\${CONFIG_LONG_APP_NAME}\${CONFIG_LONG_APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${CONFIG_LONG_APP_NAME}"

  SetAutoClose true
SectionEnd

;PAGE SETUP
!define MUI_ABORTWARNING ;a confirmation message should be displayed if the user clicks cancel

!define MUI_WELCOMEFINISHPAGE_BITMAP "modern-wizard.bmp"
!insertmacro MUI_PAGE_WELCOME ;welcome page
!insertmacro MUI_PAGE_INSTFILES ;install files page
; Finish page
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_TITLE "${CONFIG_LONG_APP_NAME} has been installed!"
!define MUI_FINISHPAGE_TITLE_3LINES
!define MUI_FINISHPAGE_RUN_TEXT "Run ${CONFIG_LONG_APP_NAME}"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
!define MUI_FINISHPAGE_LINK "${CONFIG_PUBLISHER} homepage."
!define MUI_FINISHPAGE_LINK_LOCATION "${CONFIG_PROJECT_URL}"
!define MUI_FINISHPAGE_NOREBOOTSUPPORT
; hijack the showreadme checkbox and use it for the desktop shortcut
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_CHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcut
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM

!insertmacro MUI_UNPAGE_INSTFILES
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "modern-wizard.bmp"
!insertmacro MUI_UNPAGE_FINISH

;LANGUAGE FILES
!define MUI_LANGSTRINGS
!insertmacro MUI_LANGUAGE "English"

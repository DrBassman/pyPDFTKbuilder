# define the name of the installer
Name "pyPDFTKbuilder setup"
#SetCompressor /SOLID zlib|bzip2|lzma
SetCompressor /SOLID lzma
Outfile "pyPDFTKb_install.exe"
Icon "icons\reshot-pdf-swissKnife.ico"
InstallDir $PROGRAMFILES64\pyPDFTKbuilder
DirText "Install pyPDFTKbuilder on your computer" "" "Browse" "Select directory into which to install pyPDFTKbuilder"

# default section
Section
     # define the output path for this file
    SetOutPath $INSTDIR
    SetShellVarContext all
    # define what to install and place it in the output path
    File /r dist\pyPDFTKbuilder\*
#    SetOutPath $INSTDIR\pyPDFTKbuilder
    CreateShortCut $SMPROGRAMS\pyPDFTKbuilder.lnk $INSTDIR\pyPDFTKbuilder.exe parameters $INSTDIR\_internal\icons\reshot-pdf-swissKnife.ico
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyPDFTKbuilder" "DisplayName" "pyPDFTKbuilder - a Python QT6 interface to PDFTK"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyPDFTKbuilder" "Publisher" "Ryan Losh"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyPDFTKbuilder" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyPDFTKbuilder" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteUninstaller $INSTDIR\Uninstall.exe
SectionEnd


Section "Uninstall"
    MessageBox MB_OKCANCEL "Uninstall PyPDFTKbuilder..." IDOK rm IDCANCEL can
    can:
        goto next
    rm:
        SetShellVarContext all
        Delete $INSTDIR\Uninstall.exe
        Delete $SMPROGRAMS\pyPDFTKbuilder.lnk
        RMDir /r /REBOOTOK $INSTDIR
        DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyPDFTKbuilder"
    next:
SectionEnd
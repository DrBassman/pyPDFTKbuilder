# define the name of the installer
Name "pyPDFTKbuilder setup"
#SetCompressor /SOLID zlib|bzip2|lzma
SetCompressor /SOLID lzma
Outfile "pyPDFTKb_install.exe"
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
    CreateShortCut $SMPROGRAMS\pyPDFTKbuilder.lnk $INSTDIR\pyPDFTKbuilder.exe parameters $INSTDIR\icons\reshot-pdf-swissKnife.ico
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
    next:
SectionEnd
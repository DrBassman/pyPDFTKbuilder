import sys, os
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QListWidgetItem, QWidget, QMessageBox
from PyQt6.QtCore import QProcess, QCoreApplication, QSettings
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence
from PyQt6 import uic
from catQListWidgetItem import catQListWidgetItem, PDFTK_PATH


QCoreApplication.setApplicationName("pyPDFTKbuilder")
QCoreApplication.setOrganizationDomain("losh.com")
QCoreApplication.setOrganizationName("Losh Optometry")
# Found this code through duckduckgo...
# Find the MyDocuments directory
# should be portable across Windows Linux FreeBSD, MacOS, etc.
def getDocumentsPath():
    import ctypes.wintypes
    retval = ''
    # If we're on Windows, return Documents directory...
    if hasattr(ctypes, 'windll'):
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value
        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        retval = str(buf.value)
    # otherwise return ~/Documents if it exists, else return ~
    else:
        if os.path.isdir(os.path.expanduser('~/Documents')):
            retval = str(os.path.expanduser('~/Documents'))
        else:
            retval = str(os.path.expanduser('~'))
    return(retval)


# to build the PDFTK_PATH command line, we need to generate aliases (i.e. A=foo.pdf B = bar.pdf ... )
# For our purposes, if we go from A to ZZ, that gives us 675, which should be more than enough...
#
# therefore, intToAlias takes an integer & returns corresponding Alias 0 == 'A', 1 == 'B', 
# 25 == 'Z', 26 == 'AA', 51 == 'AZ', 52 == 'BA' ... 675 == 'ZZ'
def intToAlias(i):
    retval = ''
    if i > 675:
        return (retval)
    if i // 26:
        retval = chr((i // 26) + ord('A') - 1)
    retval = retval + chr((i % 26) + ord('A'))
    return(retval)


class pyPDFTKbuilder(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(pyPDFTKbuilder, self).__init__(*args, **kwargs)
        # set icon...
        self.setWindowIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/reshot-pdf-swissKnife.svg"))))
        self.ui = uic.loadUi(os.path.abspath(os.path.join(os.path.dirname(__file__), "userInterface.ui")), self)
        self.settings = QSettings()
        self.workingDir = ""

        # Keep track of window last position between runs...
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        # Keep track of working directory...
        if self.settings.contains("workingDir"):
            self.workingDir = self.settings.value("workingDir")
        else:
            self.settings.setValue("workingDir", getDocumentsPath())    

        # Add code to the QPushButtons...
        self.ui.add_pushButton.clicked.connect(self.joinFilesAdd)
        self.ui.remove_pushButton.clicked.connect(self.removeItem)
        self.ui.mUp_pushButton.clicked.connect(self.mUp)
        self.ui.mDown_pushButton.clicked.connect(self.mDown)
        self.ui.saveAs_pushButton.clicked.connect(self.saveAs)
        self.ui.sort_pushButton.clicked.connect(self.sortJoin_listWidget)
        self.ui.clear_pushButton.clicked.connect(self.clearJoin_listWidget)
        self.ui.burstPdfSourcePushButton.clicked.connect(self.burstFileSelect)
        self.ui.burstPdfSavePushButton.clicked.connect(self.burstPdfFile)
        self.ui.mTop_pushButton.clicked.connect(self.mTop)
        self.ui.mBottom_pushButton.clicked.connect(self.mBottom)
        self.ui.copy_pushButton.clicked.connect(self.copy)
        self.ui.shuffleCat_pushButton.clicked.connect(self.shuffleCatToggle)
        self.ui.splitClearPushButton.clicked.connect(self.splitClear)

        # Add code to the Menu Actions...
        self.ui.actionJoin_Files.triggered.connect(self.switchTabJoin)
        self.ui.actionSplit_Files.triggered.connect(self.switchTabSplit)
        self.ui.actionBackground_Stamp_Number.triggered.connect(self.switchTabBSN)

        # Do something if listWidget selection changes...
        self.ui.join_listWidget.currentRowChanged.connect(self.join_itemChanged)

        # Blank out the burstPdfLabel ...
        self.ui.burstPdfLabel.setText("")

        # Change up & down buttons to icons...
        self.ui.mTop_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/up-block-bracket.svg"))))
        self.ui.mTop_pushButton.setText("")
        self.ui.mUp_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/up-block.svg"))))
        self.ui.mUp_pushButton.setText("")
        self.ui.mDown_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/down-block.svg"))))
        self.ui.mDown_pushButton.setText("")
        self.ui.mBottom_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/down-block-bracket.svg"))))
        self.ui.mBottom_pushButton.setText("")
        self.ui.add_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/plus-green.svg"))))
        self.ui.add_pushButton.setText("")
        self.ui.remove_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/minus-red.svg"))))
        self.ui.remove_pushButton.setText("")
        self.ui.clear_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/small-brush.svg"))))
        self.ui.clear_pushButton.setText("")
        self.ui.saveAs_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/file-pdf.svg"))))
        self.ui.saveAs_pushButton.setText("")
        self.ui.burstPdfSourcePushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/file-pdf.svg"))))
        self.ui.burstPdfSourcePushButton.setText("")
        self.ui.burstPdfSavePushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/file-pdf.svg"))))
        self.ui.burstPdfSavePushButton.setText("")
        self.ui.sort_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/sort.svg"))))
        self.ui.sort_pushButton.setText("")
        self.ui.copy_pushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/copy.svg"))))
        self.ui.copy_pushButton.setText("")
        self.ui.splitClearPushButton.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icons/reshot-icon-reset.svg"))))
        self.ui.splitClearPushButton.setText("")

        # Define some keyboard shortcuts...
        self.delShortcut = QShortcut(QKeySequence('Del'), self.ui.join_listWidget)
        self.delShortcut.activated.connect(self.removeItem)
        self.escShortcut = QShortcut(QKeySequence('Esc'), self.ui.join_listWidget)
        self.escShortcut.activated.connect(self.escPressed)

        self.ui.actionAbout.triggered.connect(self.helpAbout)
        self.ui.actionAbout_Qt.triggered.connect(self.helpAboutQt)

        # chdir to Documents directory...
        os.chdir(self.workingDir)




    def joinFilesAdd(self):
        fnames = QFileDialog.getOpenFileNames(self, "Add These Files", self.workingDir, "PDF files (*.pdf)")[0]
        if len(fnames):
            self.ui.join_listWidget.addItems(fnames)
            if not self.ui.saveAs_pushButton.isEnabled():
                self.ui.saveAs_pushButton.setEnabled(True)
            if (len(fnames) > 1) and (not (self.ui.sort_pushButton.isEnabled())):
                self.ui.sort_pushButton.setEnabled(True)
            if not self.ui.clear_pushButton.isEnabled():
                self.ui.clear_pushButton.setEnabled(True)
            self.workingDir = os.path.dirname(fnames[0])
            self.settings.setValue("workingDir", self.workingDir)
            os.chdir(self.workingDir)


    def join_itemChanged(self, new_row):
        num_rows = self.ui.join_listWidget.count()
        top_state = self.ui.mTop_pushButton.isEnabled()
        up_state = self.ui.mUp_pushButton.isEnabled()
        down_state = self.ui.mDown_pushButton.isEnabled()
        bottom_state = self.ui.mBottom_pushButton.isEnabled()
        remove_state = self.ui.remove_pushButton.isEnabled()
        copy_state = self.ui.copy_pushButton.isEnabled()
        clear_state = self.ui.clear_pushButton.isEnabled()
        sort_state = self.ui.sort_pushButton.isEnabled()
        save_state = self.ui.saveAs_pushButton.isEnabled()
        if not remove_state:
            self.ui.remove_pushButton.setEnabled(True)
            remove_state = True
        if num_rows >= 1:
            if not clear_state:
                self.ui.clear_pushButton.setEnabled(True)
                clear_state = True
            if not copy_state:
                self.ui.copy_pushButton.setEnabled(True)
                copy_state = True
            if not save_state:
                self.ui.saveAs_pushButton.setEnabled(True)
                save_state = True
        if num_rows > 1:
            if not sort_state:
                self.ui.sort_pushButton.setEnabled(True)
                sort_state = True
            if new_row == 0:
                if top_state:
                    self.ui.mTop_pushButton.setEnabled(False)
                    top_state = False
                if up_state:
                    self.ui.mUp_pushButton.setEnabled(False)
                    up_state = False
                if not down_state:
                    self.ui.mDown_pushButton.setEnabled(True)
                    down_state = True
                if not bottom_state:
                    self.ui.mBottom_pushButton.setEnabled(True)
                    bottom_state = True
            elif new_row == (num_rows - 1):
                if not top_state:
                    self.ui.mTop_pushButton.setEnabled(True)
                    top_state = True
                if not up_state:
                    self.ui.mUp_pushButton.setEnabled(True)
                    up_state = True
                if down_state:
                    self.ui.mDown_pushButton.setEnabled(False)
                    down_state = False
                if bottom_state:
                    self.ui.mBottom_pushButton.setEnabled(False)
                    bottom_state = False
            else:
                if not top_state:
                    self.ui.mTop_pushButton.setEnabled(True)
                    top_state = True
                if not up_state:
                    self.ui.mUp_pushButton.setEnabled(True)
                    up_state = True
                if not down_state:
                    self.ui.mDown_pushButton.setEnabled(True)
                    down_state = True
                if not bottom_state:
                    self.ui.mBottom_pushButton.setEnabled(True)
                    bottom_state = True
        if num_rows == 0:
            self.ui.mTop_pushButton.setEnabled(False)
            top_state = False
            self.ui.mUp_pushButton.setEnabled(False)
            up_state = False
            self.ui.mDown_pushButton.setEnabled(False)
            down_state = False
            self.ui.mBottom_pushButton.setEnabled(False)
            bottom_state = False
            self.ui.remove_pushButton.setEnabled(False)
            self.ui.copy_pushButton.setEnabled(False)
            copy_state = False
            self.ui.clear_pushButton.setEnabled(False)
            clear_state = False
            self.ui.sort_pushButton.setEnabled(False)
            sort_state = False
            self.ui.saveAs_pushButton.setEnabled(False)
            save_state = False
        if new_row == -1:
            if top_state:
                self.ui.mTop_pushButton.setEnabled(False)
                top_state = False
            if up_state:
                self.ui.mUp_pushButton.setEnabled(False)
                up_state = False
            if down_state:
                self.ui.mDown_pushButton.setEnabled(False)
                down_state = False
            if bottom_state:
                self.ui.mBottom_pushButton.setEnabled(False)
                bottom_state = False
            if remove_state:
                self.ui.remove_pushButton.setEnabled(False)
                remove_state = False
            if copy_state:
                self.ui.copy_pushButton.setEnabled(False)
                copy_state = False
        if self.ui.join_listWidget.count() == 1:
            self.ui.sort_pushButton.setEnabled(False)


    def removeItem(self):
        cur_row = self.ui.join_listWidget.currentRow()
        cur_num_rows = self.ui.join_listWidget.count()
        self.ui.join_listWidget.takeItem(cur_row)
        if cur_row == cur_num_rows - 1:
            cur_row = cur_row - 1
        self.join_itemChanged(cur_row)


    # move_mode has 5 options:  up, down, top, bottom, copy
    def move_item(self, move_mode):
        cur_row = self.ui.join_listWidget.currentRow()
        new_row = -1
        new_cur = -1
        take_row = -1
        if move_mode == "up": # moving item up...
            new_row = cur_row - 1
            new_cur = cur_row - 1
            take_row = cur_row + 1
        elif move_mode == "down": # moving item down...
            new_row = cur_row + 2
            new_cur = cur_row + 1
            take_row = cur_row
        elif move_mode == "top":
            new_row = 0
            new_cur = 0
            take_row = cur_row + 1
        elif move_mode == "bottom":
            new_row = -1
            take_row = cur_row
            new_cur = self.ui.join_listWidget.count() - 1
        elif move_mode == "copy":
            new_row = cur_row + 1
            take_row = -1
            new_cur = new_row
        else:
            print(f"Unsupported move mode ({move_mode})", file=sys.stderr)
            return
        # Remove the current row...
        # save or create a new widget...
        if take_row == -1:
            listWidgetItem = self.ui.join_listWidget.item(cur_row)
            listWidgetItemWidget = self.ui.join_listWidget.itemWidget(listWidgetItem)
            pdfName = listWidgetItemWidget.pdfNameLabel.text()
            cur_cw = catQListWidgetItem(pdfName)
        else:
            cur_cw = self.ui.join_listWidget.itemWidget(self.ui.join_listWidget.currentItem())
        # make a copy (clone) the current QListWidgetItem...
        new_item = self.ui.join_listWidget.currentItem().clone()
        # add the cloned item to the QListWidget...
        if new_row >= 0:
            self.ui.join_listWidget.insertItem(new_row, new_item)
        else:
            self.ui.join_listWidget.addItem(new_item)
        # put the widget on the cloned item...
        self.ui.join_listWidget.setItemWidget(new_item, cur_cw)
        # Remove / Delete / Nuke the Item being moved...
        if take_row >=0:
            self.ui.join_listWidget.takeItem(take_row)
        # Set the current row on the cloned item...
        self.ui.join_listWidget.setCurrentRow(new_cur)


    def mDown(self):
        self.move_item("down")


    def mUp(self):
        self.move_item("up")


    def saveAs(self):
        files = []
        # Get the filename to save the files to...
        output = QFileDialog.getSaveFileName(self, "Save File to...", "", "PDF files (*.pdf)")[0]
        if len(output):
            # Get the list of files from the listWidget...
            i = 0
            pdf2Handles = {}
            ranges = []
            outputOpts = []
            inputAlias = 0
            while i < self.ui.join_listWidget.count():
                listWidgetItem = self.ui.join_listWidget.item(i)
                listWidgetItemWidget = self.ui.join_listWidget.itemWidget(listWidgetItem)
                pdfName = listWidgetItemWidget.pdfNameLabel.text()
                if pdfName not in pdf2Handles:
                    pdf2Handles[pdfName] = intToAlias(inputAlias)
                    inputAlias = inputAlias + 1
                pages = listWidgetItemWidget.pagesLineEdit.text()
                if not len(pages):
                    pages = "1-end"
                qualifier = listWidgetItemWidget.selPagesComboBox.currentData()
                rotation = listWidgetItemWidget.rotateComboBox.currentData()
                files.extend([pdfName])
                ranges.extend([f"{pages}{qualifier}{rotation}"])
                i = i + 1
            # At this point, we should have 4 things:  
            # pdf2Handles dictionary (mapping each unique input PDF to a handle);
            # files list of input PDF files in desired order
            # ranges list of page range for each PDF file (in desired order)
            # input_pws dictionary (mapping handle to password)
            #
            # now, we use these to construct a
            # 'pdftk <input PDF Files> <input_pw> cat|shuffle <page ranges> output out.pdf' command...
            #
            print(PDFTK_PATH)
            cmd = [PDFTK_PATH]
            for f in list(pdf2Handles):
                cmd.extend([f"{pdf2Handles[f]}={f}"])
            if self.ui.shuffleCat_pushButton.isChecked():
                cmd.extend(['shuffle'])
            else:
                cmd.extend(['cat'])
            i = 0
            while i < len(files):
                cmd.extend([f"{pdf2Handles[files[i]]}{ranges[i]}"])
                i = i + 1
            cmd.extend(['output', output])
            proc = QProcess()
            proc.start(cmd[0], cmd[1:])
            while not proc.waitForFinished(-1):
                pass
            if proc.exitStatus() == QProcess.ExitStatus.NormalExit:
                self.ui.statusbar.showMessage(f"Saved [{output}]", 7000)
            else:
                self.ui.statusbar.showMessage(f"Error saving {output}", 7000)
                print(bytes(proc.readAllStandardError()).decode("utf8"), file=sys.stderr)


    def sortJoin_listWidget(self):
        # first, we build 2 lists & a dict
        # lclonedItems : cloned listWidgetItems for the current listWisgetItem
        # lwidgets     : the Widget for the clonedItems
        # dCurList     : keys are PDF names ; values are current position.
        lcloneditems = []
        lwidgets = []
        dCurList = {}
        cur_row = self.ui.join_listWidget.currentRow()
        new_cur_lwi = ""
        cur_pdfName = ""
        i = 0
        list_count = self.ui.join_listWidget.count()
        while i < list_count:
            cur_lwi = self.ui.join_listWidget.item(i)
            cur_widget = self.ui.join_listWidget.itemWidget(cur_lwi)
            pdfName = cur_widget.pdfNameLabel.text()
            clone_lwi = cur_lwi.clone()
            lwidgets.extend([cur_widget])
            lcloneditems.extend([clone_lwi])
            dCurList[f"{pdfName}|{i}"] = i
            if i == cur_row:
                cur_pdfName = pdfName
            i = i + 1
        # Rebuild the join_listWidgetItems
        for key in sorted(dCurList):
            cur_value = dCurList[key]
            self.ui.join_listWidget.addItem(lcloneditems[cur_value])
            self.ui.join_listWidget.setItemWidget(lcloneditems[cur_value], lwidgets[cur_value])
            if key == cur_pdfName:
                new_cur_lwi = lcloneditems[cur_value]
        i = 0
        while i < list_count:
            self.ui.join_listWidget.takeItem(0)
            i = i + 1
        if type(new_cur_lwi) is QListWidgetItem:
            self.ui.join_listWidget.setCurrentItem(new_cur_lwi)
            self.join_itemChanged(self.ui.join_listWidget.currentRow())


    def clearJoin_listWidget(self):
        self.ui.join_listWidget.clear()
        self.ui.saveAs_pushButton.setEnabled(False)
        self.ui.sort_pushButton.setEnabled(False)
        self.ui.clear_pushButton.setEnabled(False)
        self.ui.mUp_pushButton.setEnabled(False)
        self.ui.mDown_pushButton.setEnabled(False)
    

    def burstFileSelect(self):
        fname = QFileDialog.getOpenFileName(self, "Add These Files", self.workingDir, "PDF files (*.pdf)")[0]
        if len(fname):
            self.ui.burstPdfLabel.setText(fname)
            self.ui.burstPdfSavePushButton.setEnabled(True)
            self.workingDir = os.path.dirname(fname)
            self.settings.setValue("workingDir", self.workingDir)
            os.chdir(self.workingDir)


    def burstPdfFile(self):
        fname = self.ui.burstPdfLabel.text()
        out_pattern = f"{os.path.dirname(fname)}/{os.path.basename(fname)}_%03d.pdf"
        cmd = [PDFTK_PATH, fname, 'burst', 'output', out_pattern]
        proc = QProcess()
        proc.start(cmd[0], cmd[1:])
        while not proc.waitForFinished(-1):
            pass
        if proc.exitStatus() == QProcess.ExitStatus.NormalExit:
            self.ui.statusbar.showMessage(f"Saved [{fname}]", 7000)
        else:
            self.ui.statusbar.showMessage(f"Error saving {fname}", 7000)
            print(bytes(proc.readAllStandardError()).decode("utf8"), file=sys.stderr)


    def mTop(self):
        self.move_item("top")
    

    def mBottom(self):
        self.move_item("bottom")
    

    def copy(self):
        self.move_item("copy")


    def switchTabJoin(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.tabWidget.findChild(QWidget, 'tab_join'))


    def switchTabSplit(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.tabWidget.findChild(QWidget, 'tab_split'))


    def switchTabBSN(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.tabWidget.findChild(QWidget, 'tab_bsn'))
    

    def shuffleCatToggle(self):
        curState = self.ui.shuffleCat_pushButton.isChecked()
        if curState:
            self.ui.shuffleCat_pushButton.setText("Shuffle")
        else:
            self.ui.shuffleCat_pushButton.setText("Catenate")


    def escPressed(self):
        self.join_listWidget.setCurrentRow(-1)
    

    def splitClear(self):
        self.ui.burstPdfLabel.setText("")
        self.ui.burstPdfSavePushButton.setEnabled(False)


    def helpAbout(self):
        text = '\
            pyPDFTKbuilder, a PyQt6 rewrite of\
            <a href="http://www.angusj.com/pdftkb/">PDFTKBuilder</a>\
            <br><br>Copyright 2022 Ryan Losh, ALL RIGHTS RESERVED\
            <br><br>This program is free software: you can redistribute it and/or modify\
            it under the terms of the GNU General Public License as published by\
            the Free Software Foundation, version 3 of the License.\
            <br><br>This program is distributed in the hope that it will be useful,\
            but WITHOUT ANY WARRANTY; without even the implied warranty of\
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\
            GNU General Public License for more details.\
            <br><br>You should have received a copy of the GNU General Public License\
            along with this program.  If not, see <a href="https://www.gnu.org/licenses/">https://www.gnu.org/licenses/.</a>\
            <br><br>pyPDFTKbuilder is licensed under GNU GPLv3.\
            <br><br>Yet another graphical interface for the open source\
            <a href="https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/">PDFtk</a>\
        '
        QMessageBox.about(self, "pyPDFTKbuilder", text)


    def helpAboutQt(self):
        QMessageBox.aboutQt(self, "pyPDFTKbuilder")


    def closeEvent(self, event):
        # keep track of window position between runs...
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = pyPDFTKbuilder()
    gui.show()
    retval = app.exec()
    gui.hide()
    sys.exit(retval)
# Form implementation generated from reading ui file 'catQListWidgetItem.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from re import sub
from PyQt6 import QtWidgets
from PyQt6.QtCore import QRect, QSize, QProcess
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QApplication
import sys
from PyPDF4 import PdfFileReader


PDFTK_PATH="/usr/bin/pdftk"


def pdf_num_pages(pdf):
    retval = '<unknown> Pages'
    # try to get number of pages using PyPDF4 library...
    try:
        with open(pdf, 'rb') as pdf_file:
            retval = f"{PdfFileReader(pdf_file).getNumPages()} Pages"
    except:
        # If PyPDF4 library fails, try to get number of pages using pypdftk command...
        try:
            proc = QProcess()
            proc.start(f"{PDFTK_PATH}", [f"{pdf}", "dump_data"])
            while not proc.waitForFinished(-1):
                pass
            if proc.exitStatus() == QProcess.ExitStatus.NormalExit:
                for line in bytes(proc.readAllStandardOutput()).decode("utf8").splitlines():
                    if line.lower().startswith("numberofpages"):
                        retval = f"{int(line.split(':')[1])} Pages"
        except:
        # If both libs fail, 'give up'...
            retval = '<unknown> Pages'
    return(retval)


class catQListWidgetItem(QWidget):
    def __init__(self, fname):
        super(catQListWidgetItem, self).__init__()
        self.setupUi(fname)

    def setupUi(self, fname):
        self.setGeometry(QRect(10, 10, 631, 23))
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pdfNameLabel = QLabel(fname)
        self.horizontalLayout.addWidget(self.pdfNameLabel)
        self.pagesLineEdit = QLineEdit()
        self.pagesLineEdit.setPlaceholderText("Pages")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pagesLineEdit.sizePolicy().hasHeightForWidth())
        self.pagesLineEdit.setSizePolicy(sizePolicy)
        self.pagesLineEdit.setMaximumSize(QSize(75, 16777215))
        self.horizontalLayout.addWidget(self.pagesLineEdit)
        self.selPagesComboBox = QComboBox()
        self.selPagesComboBox.addItem("All Pages", "")
        self.selPagesComboBox.addItem("even", "even")
        self.selPagesComboBox.addItem("odd", "odd")
        self.selPagesComboBox.setCurrentIndex(0)
        self.horizontalLayout.addWidget(self.selPagesComboBox)
        self.rotateComboBox = QComboBox()
        self.rotateComboBox.addItem("Rotation 0º", "")
        self.rotateComboBox.addItem("right 90º", "right")
        self.rotateComboBox.addItem("left 90º", "left")
        self.rotateComboBox.addItem("180º", "down")
        self.rotateComboBox.setCurrentIndex(0)
        self.horizontalLayout.addWidget(self.rotateComboBox)
        self.noPagesLabel = QLabel("noPages")
        self.horizontalLayout.addWidget(self.noPagesLabel)
        self.noPagesLabel.setText(pdf_num_pages(fname))
        self.horizontalLayout.setStretch(0, 75)
        self.horizontalLayout.setStretch(5, 10)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = catQListWidgetItem('//some/file/name.pdf')
    ex.show()
    sys.exit(app.exec())

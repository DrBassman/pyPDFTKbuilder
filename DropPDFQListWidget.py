#!/usr/bin/python
"""
Updated for PyQt6 & creating QListWidget subclass
Drop only accepts PDF file URLs.

Code started out as...
ZetCode PyQt5 tutorial

This is a simple drag and
drop example.

Author: Jan Bodnar
Website: zetcode.com
"""
import sys, typing
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QApplication
from catQListWidgetItem import catQListWidgetItem


class DropPDFQListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)


    def dragEnterEvent(self, e):
        hasPDFs = False
        for url in e.mimeData().urls():
            if url.scheme() == "file" and url.toLocalFile()[-4:].lower() == ".pdf":
                hasPDFs = True
        if hasPDFs:
            e.accept()
        else:
            e.ignore()


    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
           e.accept()
        else:
            e.ignore()


    def dropEvent(self, e):
        fs = []
        cur_item = self.currentRow()
        for url in e.mimeData().urls():
            f = url.toLocalFile()
            if f[-4:].lower() == ".pdf":
                fs.extend([f])
        if len(fs):
            self.addItems(fs)
            # Change selection to update pushbutton states...
            if cur_item == 0:
                self.setCurrentRow(-1)
            else:
                self.setCurrentRow(0)
            self.setCurrentRow(cur_item)


    def addItem(self, label:str) -> None:
        if type(label) is str:
            cw = catQListWidgetItem(label)
            lwi = QListWidgetItem()
            lwi.setSizeHint(cw.sizeHint())
            super().addItem(lwi)
            self.setItemWidget(lwi, cw)
        elif type(label) is QListWidgetItem:
            super().addItem(label)


    def addItems(self, labels: typing.Iterable[str]) -> None:
        for label in labels:
            self.addItem(label)
#        return super().addItems(labels)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QWidget()
    ddqlw = DropPDFQListWidget(ex)
    ddqlw.move(30, 30)
    ddqlw.resize(740,540)
    ex.setWindowTitle('Simple drag and drop')
    ex.setGeometry(300, 300, 800, 600)
    ex.show()
    app.exec()
import sys, typing
from PyQt6.QtWidgets import QLabel, QWidget, QApplication, QPushButton
from catQListWidgetItem import catQListWidgetItem


class DropPDFQLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)


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
        for url in e.mimeData().urls():
            f = url.toLocalFile()
            if f[-4:].lower() == ".pdf":
                fs.extend([f])
        if len(fs):
            #  If more than 1 file dropped, use first & ignore the rest...
            self.setText(fs[0])
            self.parentWidget().findChild(QPushButton, "burstPdfSavePushButton").setEnabled(True)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QWidget()
    ddqlw = DropPDFQLabel(ex)
    ddqlw.move(30, 30)
    ddqlw.resize(740,540)
    ex.setWindowTitle('Simple drag and drop')
    ex.setGeometry(300, 300, 800, 600)
    ex.show()
    app.exec()
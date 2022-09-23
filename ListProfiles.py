
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, qApp
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem, QPushButton, QHeaderView
from PyQt5.QtCore import Qt

from Dialog import MyDialog

class ListProfileWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        titleWdiget = QLabel("<h2>Reader Profiles</h2>")
        titleWdiget.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(titleWdiget)

        self.tableWidget = QTableWidget()
        # self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(5)

        self.tableWidget.setHorizontalHeaderLabels(["Pseudonym", "Gender", "Age", "Reading style", "Books"])
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.layout.addWidget(self.tableWidget)

        self.layout.setContentsMargins(10, 20, 10, 20)
        self.setLayout(self.layout)

    def setReadersData(self, readers=[]):
        self.tableWidget.setRowCount(len(readers))
        i = 0
        for reader in readers:
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(reader[j]))

            btn = QPushButton("", self.tableWidget)
            btn.setIcon(QIcon('icons/books.png'))
            btn.clicked.connect(self.handleEditBtn)
            self.tableWidget.setCellWidget(i, 4, btn)

            i += 1
    # slot function for handling the event when user click 'edit' button of
    def handleEditBtn(self):
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        if index.isValid():
            print(index.row(), index.column())
            self.showBooksReader(index.row())

    # show the list of books read by selected reader
    def showBooksReader(self, idx):
        Lines = self._readBooksReadFile()
        book_idxs = Lines[idx].strip().split(",")
        book_idxs = book_idxs[1:]
        books = self._readBooksFile()
        titleStr = ""
        for index in book_idxs:
            titleStr += books[int(index)-1] + "\n"

        booksDialog = MyDialog(self)
        booksDialog.setMsg(titleStr)
        booksDialog.exec()

    def _readBooksReadFile(self):
        readerfile = open('texts/booksread.txt', 'r')
        Lines = readerfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines

    def _readBooksFile(self):
        readerfile = open('texts/books.txt', 'r')
        Lines = readerfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines
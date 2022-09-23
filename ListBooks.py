from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, qApp
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem, QPushButton, QHeaderView
from PyQt5.QtCore import Qt

from EditDialog import *
from Dialog import *

class ListBookWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()

        titleWdiget = QLabel("<h2>Books in Repository</h2>")
        titleWdiget.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(titleWdiget)

        addBookBtn = QPushButton("Add New", self)
        addBookBtn.setIcon(QIcon('icons/add.png'))
        addBookBtn.setMaximumWidth(100)
        addBookBtn.clicked.connect(self.addBook)
        self.layout.addWidget(addBookBtn)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.setBooksData()

        self.tableWidget.setHorizontalHeaderLabels(["Titre du livre", "Éditer", "Effacer"])
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.layout.addWidget(self.tableWidget)

        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

    # Reading the 'books.txt' file and returning the list of books in repository
    def _readBooksRepoFile(self):
        readerfile = open('texts/books.txt', 'r')
        Lines = readerfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines

    def setBooksData(self):
        books = self._readBooksRepoFile()
        self.tableWidget.setRowCount(len(books))
        i = 0
        for book in books:
            self.tableWidget.setItem(i, 0, QTableWidgetItem(book))

            btn = QPushButton("", self.tableWidget)
            btn.setIcon(QIcon('icons/edit.png'))
            btn.clicked.connect(self.handleEditBtn)
            self.tableWidget.setCellWidget(i, 1, btn)

            btn = QPushButton("", self.tableWidget)
            btn.setIcon(QIcon('icons/trash.png'))
            btn.clicked.connect(self.handleRemoveBtn)
            self.tableWidget.setCellWidget(i, 2, btn)

            i += 1

    # slot function for handling the event when user click 'edit' button of
    def handleEditBtn(self):
        # getting row index and column index of each edit button
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        if index.isValid():
            bookIdx = index.row()
            bookDialog = EditDialog(self)
            bookDialog.setMsg("Veuillez insérer le titre du livre")
            bookDialog.setMinimumWidth(300)

            # reading title of book from books.txt file
            booksfile = open('texts/books.txt', 'r')
            lines = booksfile.readlines()

            for i, line in enumerate(lines):
                line = line.replace('\n', '')
                lines[i] = line

            bookDialog.setTargetBox(lines[bookIdx])
            if bookDialog.exec():
                title = bookDialog.getTargetBox()
                self.tableWidget.setItem(bookIdx, 0, QTableWidgetItem(title))
                # updating the content of 'books.txt' file
                lines[bookIdx] = title
                writefile = open('texts/books.txt', 'w')
                for line in lines:
                    writefile.write(line)
                    writefile.write("\n")
                writefile.close()
            else:
                print("Cancle!")

        self.InitTextFiles()                

    # slot function for handling the event when user click 'remove' button
    def handleRemoveBtn(self):
        # getting row index and column index of each edit button
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        if index.isValid():
            bookIdx = index.row()
            self.tableWidget.removeRow(bookIdx)

            # upgrading txt files
            self.clearTxtFiles(bookIdx)
            self.InitTextFiles()

    # slot function for handling the event when user click 'add new' button
    def addBook(self):
        # asking the title of book for adding
        bookDialog = EditDialog(self)
        bookDialog.setMsg("Veuillez insérer le titre du livre.")
        if bookDialog.exec():
            title = bookDialog.getTargetBox()
            # if book already exits in books.txt, then show error message
            readerfile = open('texts/books.txt', 'r')
            Lines = readerfile.readlines()
            books = []
            for line in Lines:
                books.append(line.strip())
            if title in books:
                dialog = MyDialog()
                dialog.setMsg("Le livre du même nom existe déjà.")
                dialog.exec()
                return

            # adding new row at end of table
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(title))

            btn = QPushButton("", self.tableWidget)
            btn.setIcon(QIcon('icons/edit.png'))
            btn.clicked.connect(self.handleEditBtn)
            self.tableWidget.setCellWidget(rowPosition, 1, btn)

            btn = QPushButton("", self.tableWidget)
            btn.setIcon(QIcon('icons/trash.png'))
            self.tableWidget.setCellWidget(rowPosition, 2, btn)

            # adding new row at end of 'books.txt' file
            booksfile = open('texts/books.txt', 'a')
            booksfile.write('\n')
            booksfile.write(title)
            booksfile.close()

            # updating scoring matrix and saving it as file
            scoringfile = open('texts/scoring.txt', 'r')
            Lines = scoringfile.readlines()
            scores = []
            for line in Lines:
                score_row = line.strip().split(",")
                score_row.append("0")
                scores.append(score_row)
            scoringfile = open('texts/scoring.txt', 'w')
            for score in scores:
                row = ",".join(score)
                scoringfile.write(row)
                scoringfile.write("\n")
            scoringfile.close()
            self.InitTextFiles()
        else:
            print("Cancle!")

    def clearTxtFiles(self, idx):
        # updating the books.txt file
        readerfile = open('texts/books.txt', 'r')
        Lines = readerfile.readlines()
        Lines.pop(idx)

        writefile = open('texts/books.txt', 'w')

        for line in Lines:
            writefile.write(line)
        writefile.close()

        # updating the booksread.txt file
        readerfile = open('texts/booksread.txt', 'r')
        Lines = readerfile.readlines()
        checkedLines = []
        for line in Lines:
            line_arr = line.strip().split(",")
            if str(idx+1) in line_arr:
                line_arr.remove(str(idx+1))
            checkedLine = ",".join(line_arr)
            checkedLines.append(checkedLine)

        writefile = open('texts/booksread.txt', 'w')

        for line in checkedLines:
            writefile.write(line)
            writefile.write("\n")
        writefile.close()

        # updating scoring matrix and saving it as file
        scoringfile = open('texts/scoring.txt', 'r')
        Lines = scoringfile.readlines()
        scores = []
        for line in Lines:
            scoreRow = line.strip().split(",")
            del scoreRow[idx]
            scores.append(scoreRow)
        scoringfile = open('texts/scoring.txt', 'w')
        for score in scores:
            row = ",".join(score)
            scoringfile.write(row)
            scoringfile.write("\n")
        scoringfile.close()
        self.InitTextFiles()

    def InitTextFiles(self):
        with open("texts/reader.txt") as f_input:
            data = f_input.read().rstrip('\n')
        with open("texts/reader.txt", 'w') as f_output:    
            f_output.write(data)

        with open("texts/booksread.txt") as f_input:
            data = f_input.read().rstrip('\n')
        with open("texts/booksread.txt", 'w') as f_output:    
            f_output.write(data)

        with open("texts/books.txt") as f_input:
            data = f_input.read().rstrip('\n')
        with open("texts/books.txt", 'w') as f_output:    
            f_output.write(data)
        
        with open("texts/scoring.txt") as f_input:
            data = f_input.read().rstrip('\n')
        with open("texts/scoring.txt", 'w') as f_output:    
            f_output.write(data)
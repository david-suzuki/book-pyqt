from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QLabel, QPushButton, QWidget, QFormLayout, QLineEdit, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from CheckableComboBox import *
from Dialog import MyDialog

class RateBookWidget(QWidget):
    def __init__(self, parent=None, reader=""):
        super().__init__(parent)

        self.reader = reader

        self.layout = QVBoxLayout()

        # title of screen
        self.titleWdiget = QLabel("<h2>Rate a Book</h2>")
        self.titleWdiget.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.titleWdiget)

        # form of screen
        self.formLayout = QFormLayout()
        self.pseudonymEdt = QLineEdit(self)
        self.pseudonymEdt.setMinimumHeight(30)
        self.pseudonymEdt.setText(reader)
        self.pseudonymEdt.setReadOnly(True)
        self.formLayout.addRow('Pseudonym:', self.pseudonymEdt)
        self.bookCmb = QComboBox(self)
        readbooks = self.booksReadByReader()
        self.bookCmb.addItems(readbooks)
        self.bookCmb.setMinimumHeight(30)
        self.formLayout.addRow('Read books:', self.bookCmb)
        self.rateEdt = QLineEdit(self)
        self.rateEdt.setMinimumHeight(30)
        self.formLayout.addRow('Rate:', self.rateEdt)
        self.rateLst = QListWidget(self)
        self.InitRatingLst()
        self.formLayout.addRow('Rate List:', self.rateLst)

        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(0, 20, 0, 20)

        self.layout.addLayout(self.formLayout)

        self.buttonLayout = QHBoxLayout()
        okButton = QPushButton("Ok", self)
        okButton.setMinimumHeight(30)
        okButton.setMaximumWidth(100)
        okButton.clicked.connect(self.rateBook)
        cancelButton = QPushButton("Cancel", self)
        cancelButton.setMinimumHeight(30)
        cancelButton.setMaximumWidth(100)

        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(okButton)
        self.buttonLayout.addWidget(cancelButton)
        self.layout.addLayout(self.buttonLayout)
        self.layout.addStretch()
        self.layout.setContentsMargins(40, 40, 40, 10)

        self.setLayout(self.layout)

    # getting the ratings of books read by reader from scoring matrix
    def InitRatingLst(self):
        row = self._getRowForMatrix(self.reader)

        # getting the books from 'books.txt' file
        books = self.getBooksFromTxt()

        scoringfile = open('texts/scoring.txt', 'r')
        Lines = scoringfile.readlines()
        scores = Lines[row].strip().split(",")
        for i, score in enumerate(scores):
            if int(score) != 0:
                lineText = books[i] + " " + score
                line_number = self.rateLst.count()
                self.rateLst.insertItem(line_number, lineText)

    # getting the list of books read by reader among all books
    def booksReadByReader(self):
        # Reading the 'booksread.txt' file
        readerfile = open('texts/booksread.txt', 'r')
        Lines = readerfile.readlines()
        books = self.getBooksFromTxt()
        readBooks = []
        for line in Lines:
            line_arr = line.strip().split(",")
            if line_arr[0] == self.reader:
                for i in range(1, len(line_arr)):
                    readBooks.append(books[int(line_arr[i])-1])
                break
        return readBooks
    
    def getBooksFromTxt(self):
        booksfile = open("texts/books.txt", 'r')
        Lines = booksfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines

    def rateBook(self):
        selectedBook = self.bookCmb.currentText()
        rating = self.rateEdt.text()
        # rating is not number, then show error message
        if not rating.isnumeric():
            dialog = MyDialog()
            dialog.setMsg("Veuillez insérer le numéro pour l'évaluation.")
            dialog.exec()
            return

        # if rating is between 1 and 5, then show error message
        if int(rating) < 1 or int(rating) > 5:
            dialog = MyDialog()
            dialog.setMsg("Veuillez insérer le numéro pour l'évaluation.")
            dialog.exec()
            return

        items = []
        for x in range(self.rateLst.count()):
            items.append(self.rateLst.item(x).text()[:-2])

        lineText = selectedBook + " " + rating
        # if rated book dose not exist in list, then add
        if selectedBook in items:
            line_number = items.index(selectedBook)
            self.rateLst.item(line_number).setText(lineText)
        else:    
            line_number = self.rateLst.count()
            self.rateLst.insertItem(line_number, lineText)
        
        # updating scoring matrix in file
        self.updateScoringMatrixFile(selectedBook, rating)

    # getting the column index for scoring matrix
    def _getColumnForMatrix(self, book):
        booksfile = open('texts/books.txt', 'r')
        Lines = booksfile.readlines()
        books = []
        for line in Lines:
            books.append(line.strip())
        return books.index(book)

    def _getRowForMatrix(self, reader):
        readerfile = open('texts/reader.txt', 'r')
        Lines = readerfile.readlines()
        readers = []
        for line in Lines:
            readers.append(line.strip().split(",")[0])
        return readers.index(reader)

    def updateScoringMatrixFile(self, book, rating):
        # getting the column number for scoring matrix
        col = self._getColumnForMatrix(book)

        # getting the row number for scoring matrix
        row = self._getRowForMatrix(self.reader)

        scoringfile = open('texts/scoring.txt', 'r')
        Lines = scoringfile.readlines()
        scoring = []
        for line in Lines:
            s_row = line.strip().split(",")
            scoring.append(s_row)

        scoring[row][col] = rating

        scoringMatrixFile = open('texts/scoring.txt', 'w')
        for row in scoring:
            scoringMatrixFile.write(",".join(map(str, row)))
            scoringMatrixFile.write("\n")
        scoringMatrixFile.close()

        with open("texts/scoring.txt") as f_input:
            data = f_input.read().rstrip('\n')
        with open("texts/scoring.txt", 'w') as f_output:    
            f_output.write(data)
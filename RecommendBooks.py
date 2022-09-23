from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget, QFormLayout, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt
from CheckableComboBox import *
from Dialog import MyDialog
from EditDialog import EditDialog
import math

class RecommendBooksWidget(QWidget):
    def __init__(self, parent=None, reader=""):
        super().__init__(parent)

        self.similarityMtx = self.calcSimilarityMatrix()

        self.reader = reader

        self.layout = QVBoxLayout()

        # title of screen
        self.titleWdiget = QLabel("<h2>Recommander des livres</h2>")
        self.titleWdiget.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.titleWdiget)

        # form of screen
        self.formLayout = QFormLayout()
        self.pseudonymEdt = QLineEdit(self)
        self.pseudonymEdt.setMinimumHeight(30)
        self.pseudonymEdt.setText(reader)
        self.pseudonymEdt.setReadOnly(True)
        self.formLayout.addRow('Pseudonym:', self.pseudonymEdt)
        self.recommendLst = QListWidget(self)
        self.recommendBooks = self.getRecommendedBooks(self.similarityMtx)
        for book in self.recommendBooks:
            line_number = self.recommendLst.count()
            self.recommendLst.insertItem(line_number, book)
        self.formLayout.addRow('Recommended Books:', self.recommendLst)

        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(0, 20, 0, 20)

        self.layout.addLayout(self.formLayout)

        self.buttonLayout = QHBoxLayout()
        okButton = QPushButton("Read", self)
        okButton.clicked.connect(self.readBook)
        okButton.setMinimumHeight(30)
        okButton.setMaximumWidth(100)

        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(okButton)
        self.layout.addLayout(self.buttonLayout)
        self.layout.addStretch()
        self.layout.setContentsMargins(40, 40, 40, 10)

        self.setLayout(self.layout)

    def readBook(self):
        seleted_index = self.recommendLst.currentRow()
        # if there is not selected row in list, then show error message
        if seleted_index == -1:
            dialog = MyDialog()
            dialog.setMsg("Veuillez sélectionner le livre lu.")
            dialog.exec()
            return

        # getting index in books.txt file for selected book in list
        selected_book = self.recommendBooks[seleted_index]
        books = self._readBooksFile()
        book_index = books.index(selected_book)

        # updating the 'booksread.txt' file
        Lines = self._readBooksReadFile()
        readerBooks = []
        for line in Lines:
            line = line.split(",")
            # if current reader is same with name in booksread.text
            if line[0] == self.reader:
                i = 0
                for i, book_indice in enumerate(line[1:]):
                    if int(book_indice) > book_index:
                        break
                line.insert(i + 1, str(book_index+1))
            readerBooks.append(line)
        
        writefile = open('texts/booksread.txt', 'w')
        for book in readerBooks:
            newbook = ",".join(book)
            writefile.write(newbook)
            writefile.write("\n")
        writefile.close()

        with open("texts/booksread.txt") as f_input:
            data = f_input.read().rstrip('\n')
        with open("texts/booksread.txt", 'w') as f_output:    
            f_output.write(data)

        # removing the book from recommended books list
        self.recommendLst.takeItem(seleted_index)

        # showing the dialog asking if rating current book
        ratingDialog = EditDialog(self)
        ratingDialog.setMsg("Veuillez noter ce livre.")
        if ratingDialog.exec():
            targetReader = ratingDialog.getTargetBox()
            if not targetReader or not targetReader.isnumeric or int(targetReader) < 1 or int(targetReader) > 5:
                dialog = MyDialog()
                dialog.setMsg("Veuillez insérer une évaluation valide.")
                dialog.exec()
            else:
                self.ratingThisBook(book_index, targetReader)    
        else:
            dialog = MyDialog()
            dialog.setMsg("Veuillez noter ce livre plus tard.")
            dialog.exec()
            return

    def _getRowForMatrix(self, reader):
        readerfile = open('texts/reader.txt', 'r')
        Lines = readerfile.readlines()
        readers = []
        for line in Lines:
            readers.append(line.strip().split(",")[0])
        return readers.index(reader)

    # rating this book
    def ratingThisBook(self, book, rating):
        row = self._getRowForMatrix(self.reader)
        col = book
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

    # gettting list recommended books based on similarity matrix
    def getRecommendedBooks(self, similarityMtx):
        # getting the index of current reader in reader.txt file
        readerLines = self._readReaderFile()
        readers = []
        for line in readerLines:
            reader = line.split(",")[0]
            readers.append(reader)
        readerIdx = readers.index(self.reader)

        # getting the similarity matrix row of current reader
        similarity_mtx_row = similarityMtx[readerIdx]
        
        # getting max value in row
        similarity_max_index = self.getJuniorMaxIndex(similarity_mtx_row)

        # list of books read by current reader
        target_reader_lines = self._readBooksReadFile()
        target_reader_books = target_reader_lines[readerIdx]
        target_books = self.getListBooksRead(target_reader_books)

        # list of books read by similarity reader
        similarity_reader_lines = self._readBooksReadFile()
        similarity_reader_books = similarity_reader_lines[similarity_max_index]
        similarity_books = self.getListBooksRead(similarity_reader_books)

        # getting indices of books read by similarity reader but not read by target reader
        list_difference = []
        for item in similarity_books:
            if item not in target_books:
                list_difference.append(item)

        # getting books and showing
        books = self._readBooksFile()
        recommendBooks = []
        for ele in list_difference:
            recommendBooks.append(books[ele-1])

        return recommendBooks

    def getJuniorMaxIndex(self, row):
        temp = row.copy()
        i = temp.index(1)
        del temp[i]
        juniorMax = max(temp)
        return row.index(juniorMax)

    def getListBooksRead(self, row):
        items = row.split(",")
        del items[0]
        return list(map(int, items))

    # calculating cosine similarity between two vectors
    def calcSimilarityValue(self, r1, r2):
        molecule = 0
        for i in range(len(r1)):
            molecule += r1[i] * r2[i]

        denominator1 = 0
        for i in range(len(r1)):
            denominator1 += r1[i] * r1[i]

        denominator2 = 0
        for i in range(len(r2)):
            denominator2 += r2[i] * r2[i]

        if denominator1 == 0 or denominator2 == 0:
            similarity = 0
        else:
            similarity = molecule / (math.sqrt(denominator1) * math.sqrt(denominator2))

        return round(similarity, 2)

    # calculating similarity matrix
    def calcSimilarityMatrix(self):
        scoringMtx = self.calcScoringMatrix()
        m = len(scoringMtx)
        n = len(scoringMtx[0])
        similarityMtx = [[1]*m for _ in range(m)]
        for i in range(m):
            for j in range(i+1, m):
                similarity = self.calcSimilarityValue(scoringMtx[i], scoringMtx[j])
                similarityMtx[i][j] = similarity
                similarityMtx[j][i] = similarity

        return similarityMtx
    
    # calculating scoring matrix form file
    def calcScoringMatrix(self):
        scoringRows = self._readScoringFile()

        mtx = []
        for row in scoringRows:
            r = row.split(",")
            mtx.append(list(map(int, r)))
        return mtx

    # reading scoring.txt file
    def _readScoringFile(self):
        scoringfile = open('texts/scoring.txt', 'r')
        Lines = scoringfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines

    def _readReaderFile(self):
        readerfile = open('texts/reader.txt', 'r')
        Lines = readerfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines
    
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


from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QLabel, QPushButton, QWidget, QFormLayout, QLineEdit, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from CheckableComboBox import *
from Dialog import MyDialog

GENDERS = ['HOMME', 'FEMME', 'PEU IMPORTE']
AGES = ['<= 18 ans', 'Entre 18 ans et 25 ans', '> 25 ans']
READING_STYLES = ['Science-fiction', 'Biographie', 'Horreur', 'Romance', 'Fable', 'Histoire', 'Comédie']

class DetailProfileWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # variable for indicating current screen is create or edit
        self.screenStatus = 'create'

        # variable for representing index in reader.txt and booksreade.txt file
        self.index = 0

        self.layout = QVBoxLayout()

        # title of screen
        self.titleWdiget = QLabel("<h2>Create Reader Profile</h2>")
        self.titleWdiget.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.titleWdiget)

        # form of screen
        self.formLayout = QFormLayout()
        self.pseudonymEdt = QLineEdit(self)
        self.pseudonymEdt.setMinimumHeight(30)
        self.formLayout.addRow('Pseudonym:', self.pseudonymEdt)
        self.genderCmb = QComboBox(self)
        self.genderCmb.addItems(GENDERS)
        self.genderCmb.setMinimumHeight(30)
        self.formLayout.addRow('Gender:', self.genderCmb)
        self.ageCmb = QComboBox(self)
        self.ageCmb.addItems(AGES)
        self.ageCmb.setMinimumHeight(30)
        self.formLayout.addRow('Age:', self.ageCmb)
        self.styleCmb = QComboBox(self)
        self.styleCmb.addItems(READING_STYLES)
        self.styleCmb.setMinimumHeight(30)
        self.formLayout.addRow('Reading style:', self.styleCmb)
        
        self.readBookTxt = CheckableComboBox()
        self.readBookTxt.setMinimumHeight(30)
        booksInRepo = self._readBooksRepoFile()
        self.readBookTxt.addItems(booksInRepo)
        self.formLayout.addRow('Read books:', self.readBookTxt)

        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(0, 20, 0, 20)

        self.layout.addLayout(self.formLayout)

        self.buttonLayout = QHBoxLayout()
        okButton = QPushButton("Ok", self)
        okButton.setMinimumHeight(30)
        okButton.setMaximumWidth(100)
        okButton.clicked.connect(self._saveReader)
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

    def _readBooksRepoFile(self):
        readerfile = open('texts/books.txt', 'r')
        Lines = readerfile.readlines()

        for i, line in enumerate(Lines):
            line = line.replace('\n', '')
            Lines[i] = line

        return Lines

    def _saveReader(self):
        pseudonym = self.pseudonymEdt.text()
        if not pseudonym:
            dialog = MyDialog()
            dialog.setMsg("Veuillez insérer un pseudonyme.")
            dialog.exec()
            return
        gender = self.genderCmb.currentIndex() + 1
        age = self.ageCmb.currentIndex() + 1
        readingstyle = self.styleCmb.currentIndex() + 1
        readbooks = self.readBookTxt.currentData()

        if self.screenStatus == 'create':
            # if same reader already exist, then shows error message
            readerfile = open('texts/reader.txt', 'r')
            Lines = readerfile.readlines()
            readers = []
            for line in Lines:
                reader = line.strip().split(",")[0]
                readers.append(reader)
            if pseudonym in readers:
                dialog = MyDialog()
                dialog.setMsg("Le lecteur du même nom existe déjà.")
                dialog.exec()
                return

            # writing to txt files
            readerline= pseudonym + "," + str(gender) + "," + str(age) + "," + str(readingstyle)
            readerfile = open('texts/reader.txt', 'a')
            readerfile.write('\n')
            readerfile.write(readerline)
            readerfile.close()

            booksreadline = pseudonym
            for book in readbooks:
                booksreadline += "," + str(book+1)
            bookreadfile = open('texts/booksread.txt', 'a')
            bookreadfile.write('\n')
            bookreadfile.write(booksreadline)
            bookreadfile.close()

            # adding new row to scoring matrix and save it as file
            numberBooks = len(self._readBooksRepoFile())
            scorelist = [0]*numberBooks
            scoreRow = ",".join(map(str, scorelist))
            scoringfile = open('texts/scoring.txt', 'a')
            scoringfile.write("\n")
            scoringfile.write(scoreRow)
            scoringfile.close()
        elif self.screenStatus == 'edit':
            # replacing the corresponding line with new values
            readerline= pseudonym + "," + str(gender) + "," + str(age) + "," + str(readingstyle) + "\n"
            readerfile = open('texts/reader.txt', 'r')
            Lines = readerfile.readlines()
            Lines[self.index] = readerline
            
            booksreadline = pseudonym
            for book in readbooks:
                booksreadline += "," + str(book+1)
            booksreadline += "\n"
            bookreadfile = open('texts/booksread.txt', 'r')
            BooksLines = bookreadfile.readlines()
            BooksLines[self.index] = booksreadline

            writefile = open('texts/reader.txt', 'w')

            for line in Lines:
                writefile.write(line)
            writefile.close()

            bookwritefile = open('texts/booksread.txt', 'w')
            for line in BooksLines:
                bookwritefile.write(line)
            bookwritefile.close()

        # display the success message
        dialog = MyDialog()
        dialog.setMsg("Le nouveau lecteur est créé avec succès.")
        dialog.exec()

        # removing the empty line at end of file
        self.InitTextFiles()
        
    def setScreenTitle(self, text):
        self.titleWdiget.setText(text)
        self.screenStatus = 'edit'
    
    def setDetailInfoms(self, data):
        self.index = data['index']
        self.pseudonymEdt.setText(data['pseudonym'])
        self.genderCmb.setCurrentText(data['gender'])
        self.ageCmb.setCurrentText(data['age'])
        self.styleCmb.setCurrentText(data['style'])
        self.readBookTxt.setInitCheckItems(data['readbooks'])

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

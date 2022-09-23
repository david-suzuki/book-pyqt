import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction, QStackedWidget

from ListProfiles import *
from DetailProfile import *
from EditDialog import *
from ListBooks import *
from RateBook import *
from RecommendBooks import *


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Book Recommendation")
        self.resize(600, 400)
        self.centralWidget = QStackedWidget()
        self.setCentralWidget(self.centralWidget)

        self.readers = self._readTxtFiles()

        listProfileWidget = ListProfileWidget(self)
        listProfileWidget.setReadersData(self.readers)
        self.centralWidget.addWidget(listProfileWidget)

        self._createActions()
        self._createMenuBar()
        self._connectActions()  

    def _createMenuBar(self):
        menuBar = self.menuBar()
        profileMenu = QMenu("&Reader profiles", self)
        menuBar.addMenu(profileMenu)
        profileMenu.addAction(self.listProfilesAction)
        profileMenu.addAction(self.createProfileAction)
        profileMenu.addAction(self.editProfileAction)
        profileMenu.addAction(self.removeProfileAction)

        bookMenu = QMenu("&Visit the books repository", self)
        menuBar.addMenu(bookMenu)
        bookMenu.addAction(self.listBooksAction)

        recommedMenu = QMenu("&Recommendation ", self)
        menuBar.addMenu(recommedMenu)
        recommedMenu.addAction(self.rateBookAction)
        recommedMenu.addAction(self.recommendBookAction)

    def _createActions(self):
        # Creating actions for profile menu
        self.listProfilesAction = QAction("&List", self)
        self.createProfileAction = QAction("&Create", self)
        self.editProfileAction = QAction("&Edit", self)
        self.removeProfileAction = QAction("&Remove", self)

        # Creating actions for book menu
        self.listBooksAction = QAction("&List", self)

        # Creating actions for recommendation menu
        self.rateBookAction = QAction("&Rating book", self)
        self.recommendBookAction = QAction("&Recommending book", self)

    def _connectActions(self):
        self.createProfileAction.triggered.connect(self.createProfile)
        self.editProfileAction.triggered.connect(lambda: self.askReaderName('edit'))
        self.listProfilesAction.triggered.connect(self.listProfiles)
        self.removeProfileAction.triggered.connect(lambda: self.askReaderName('remove'))

        self.listBooksAction.triggered.connect(self.listBooks)

        self.rateBookAction.triggered.connect(lambda: self.askReaderName('rate'))
        self.recommendBookAction.triggered.connect(lambda: self.askReaderName('recommend'))

    def _readTxtFiles(self):
        readerfile = open('texts/reader.txt', 'r')
        Lines = readerfile.readlines()
        readers = []
        for line in Lines:
            line_arr = line.strip().split(",")
            reader = []
            idx = 0
            for item in line_arr:
                if idx == 0:
                    reader.append(item)
                elif idx == 1:
                    reader.append(GENDERS[int(item)-1])
                elif idx == 2:
                    reader.append(AGES[int(item)-1])
                elif idx == 3:
                    reader.append(READING_STYLES[int(item)-1])
                idx += 1
            readers.append(reader)
        return readers

    # Read 'booksread.txt' file and select the line of reader with name
    def _readReaderBooksTxtFile(self, name):
        booksfile = open('texts/booksread.txt', 'r')
        Lines = booksfile.readlines()
        books = []
        for line in Lines:
            line_arr = line.strip().split(",")
            if line_arr[0] == name:
                idx = 0
                for item in line_arr:
                    if idx != 0:
                        books.append(int(item)-1)
                    idx += 1
                break
        return books

    def createProfile(self):
        detailProfileWidget = DetailProfileWidget(self)
        self.centralWidget.addWidget(detailProfileWidget)
        self.centralWidget.setCurrentWidget(detailProfileWidget)

    def askReaderName(self, action='edit'):
        editDialog = EditDialog(self)

        if action == 'edit':
            editDialog.setMsg("Veuillez insérer le lecteur pour l'édition.")
            if editDialog.exec():
                targetReader = editDialog.getTargetBox()
                if targetReader:
                    self.editProfile(targetReader)
            else:
                print("Cancel!")
        elif action == 'remove':
            editDialog.setMsg("Veuillez insérer le nom du lecteur pour suppression")
            if editDialog.exec():
                targetReader = editDialog.getTargetBox()
                if targetReader:
                    self.removeProfile(targetReader)
            else:
                print("Cancel!")
        elif action == 'rate':
            editDialog.setMsg("Veuillez insérer le nom du lecteur pour l'évaluation")
            if editDialog.exec():
                targetReader = editDialog.getTargetBox()
                if targetReader:
                    self.rateBook(targetReader)
            else:
                print("Cancel!")
        elif action == 'recommend':
            editDialog.setMsg("Veuillez insérer le nom du lecteur pour recommandation.")
            if editDialog.exec():
                targetReader = editDialog.getTargetBox()
                if targetReader:
                    self.recommendBook(targetReader)
            else:
                print("Cancel!")

    def editProfile(self, target):
        detailProfileWidget = DetailProfileWidget(self)
        detailProfileWidget.setScreenTitle('<h2>Modifier le profil du lecteur</h2>')

        # get target reader data for editing
        targetReader = {}
        readers = self._readTxtFiles()
        idx = 0
        for reader in readers:
            if reader[0] == target:
                targetReader['index'] = idx
                targetReader['pseudonym'] = reader[0]
                targetReader['gender'] = reader[1]
                targetReader['age'] = reader[2]
                targetReader['style'] = reader[3]
                targetReader['readbooks'] = self._readReaderBooksTxtFile(reader[0])
                break
            idx += 1
        if len(targetReader) == 0:
            dialog = MyDialog()
            dialog.setMsg("Le nom du lecteur est erroné.")
            dialog.exec()
            return
        # pass the information of target reader to detail screen
        detailProfileWidget.setDetailInfoms(targetReader)
        self.centralWidget.addWidget(detailProfileWidget)
        self.centralWidget.setCurrentWidget(detailProfileWidget)

    def listProfiles(self):
        listProfileWidget = ListProfileWidget(self)
        self.readers = self._readTxtFiles()
        listProfileWidget.setReadersData(self.readers)
        self.centralWidget.addWidget(listProfileWidget)
        self.centralWidget.setCurrentWidget(listProfileWidget)

    def removeProfile(self, target):
        # getting reader index for removing
        readers = self._readTxtFiles()
        idx = 0
        for reader in readers:
            if reader[0] == target:
                break
            idx += 1

        # if there is not reader, then show error message
        if idx >= len(readers):
            dialog = MyDialog()
            dialog.setMsg("Le nom du lecteur est erroné.")
            dialog.exec()
            return
        
        # upgrading txt files
        readerfile = open('texts/reader.txt', 'r')
        Lines = readerfile.readlines()
        del Lines[idx]

        bookreadfile = open('texts/booksread.txt', 'r')
        BooksLines = bookreadfile.readlines()
        del BooksLines[idx]

        scoringfile = open('texts/scoring.txt', 'r')
        scoreLines = scoringfile.readlines()
        del scoreLines[idx]

        writefile = open('texts/reader.txt', 'w')
        for line in Lines:
            writefile.write(line)
        writefile.close()

        bookwritefile = open('texts/booksread.txt', 'w')
        for line in BooksLines:
            bookwritefile.write(line)
        bookwritefile.close()

        scorewritefile = open('texts/scoring.txt', 'w')
        for line in scoreLines:
            scorewritefile.write(line)
        scorewritefile.close()

        # Redisplaying the list of readers
        self.listProfiles()

    def listBooks(self):
        listBookWidget = ListBookWidget(self)
        self.centralWidget.addWidget(listBookWidget)
        self.centralWidget.setCurrentWidget(listBookWidget)

    def rateBook(self, target):
        # if target dosen't exist in readers, show error message
        if not self.validateReader(target):
            dialog = MyDialog()
            dialog.setMsg("Veuillez insérer le nom du lecteur correct.")
            dialog.exec()
            return

        rateBookWidget = RateBookWidget(self, target)
        self.centralWidget.addWidget(rateBookWidget)
        self.centralWidget.setCurrentWidget(rateBookWidget)

    def recommendBook(self, target):
        # if target dosen't exist in readers, show error message
        if not self.validateReader(target):
            dialog = MyDialog()
            dialog.setMsg("Veuillez insérer le nom du lecteur correct.")
            dialog.exec()
            return
        recommedBookWidget = RecommendBooksWidget(self, target)
        self.centralWidget.addWidget(recommedBookWidget)
        self.centralWidget.setCurrentWidget(recommedBookWidget)

    def validateReader(self, pseudonym):
        readerfile = open('texts/reader.txt', 'r')
        Lines = readerfile.readlines()
        readers = []
        for line in Lines:
            readers.append(line.strip().split(",")[0])
        if not pseudonym in readers:
            return False
        return True

def InitTextFiles():
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

def InitScoringMatrix():
    # row number of scoring matrix
    readerfile = open('texts/reader.txt', 'r')
    Lines = readerfile.readlines()
    m = len(Lines)
    # column number of scoring matrix
    readerfile = open('texts/books.txt', 'r')
    Lines = readerfile.readlines()
    n = len(Lines)

    # saving the scoring matrix as file
    arr = [[0]*m]*n
    scoringMatrixFile = open('texts/scoring.txt', 'w')
    for row in arr:
        scoringMatrixFile.write(",".join(map(str, row)))
        scoringMatrixFile.write("\n")
    scoringMatrixFile.close()

    with open("texts/scoring.txt") as f_input:
        data = f_input.read().rstrip('\n')
    with open("texts/scoring.txt", 'w') as f_output:    
        f_output.write(data)

if __name__ == "__main__":
    # initialize the txt files for operation
    InitTextFiles()
    # initialize the scoring matrix and save it as file
    InitScoringMatrix()
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


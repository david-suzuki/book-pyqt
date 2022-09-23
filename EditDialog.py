from PyQt5.QtWidgets import *

class EditDialog(QDialog):
    """Dialog."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Info!")
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        self.message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(self.message)
        
        self.targetEdt = QLineEdit()
        self.layout.addWidget(self.targetEdt)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def setMsg(self, msg):
        self.message.setText(msg)

    def getTargetBox(self):
        return self.targetEdt.text()

    def setTargetBox(self, text):
        self.targetEdt.setText(text)
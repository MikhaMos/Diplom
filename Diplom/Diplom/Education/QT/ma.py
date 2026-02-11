import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QLabel,
    QVBoxLayout, QMenu,QTextEdit
)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("hello")
        self.resize(500,350)

        layout = QVBoxLayout()

        self.inputField = QLineEdit()
        button = QPushButton('&Say Hello', clicked = self.satHello)
        self.output = QTextEdit()

        layout.addWidget(self.inputField)
        layout.addWidget(button)
        layout.addWidget(self.output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def satHello(self):
        inputText = self.inputField.text()
        self.output.setText(f"hello {inputText}")

   

app=QApplication(sys.argv)
app.setStyleSheet("""
    QWidget {
        font-size: 25 px;
    }
    QPushButton {
        font-size: 20px;
    }
                  """)

window = MainWindow()
window.show()
app.exec()


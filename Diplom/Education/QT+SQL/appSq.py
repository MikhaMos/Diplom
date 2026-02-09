import sys
from PySide6.QtWidgets import QApplication
from datetime import datetime
import os
from PySide6 import QtUiTools
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QStackedWidget, QStatusBar,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox, QGroupBox, QFileDialog, QComboBox, QSpinBox)

from database import Database

class SurveyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control panel")
        self.resize(800,600)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file=os.path.join(current_dir,'Page.ui')

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        
        self.db = Database()
        self.question_groups = []
        

        self.rename_question()
        self.setup_connections()
        self.setup_navigation()
        

    def rename_question(self):
        self. question_groups = []

        for q in range(1,5):
            groupbox_name = f'groupBox_q{q}'
            groupbox = self.ui.findChild(QGroupBox, groupbox_name)
            if groupbox:
                radio_buttons=[]
                
                for i in range(1,11):
                    btn_name = f'radioButton_q{q}_{i}'
                    btn = groupbox.findChild(QRadioButton, btn_name)
                    if btn:
                        radio_buttons.append(btn)
            self.question_groups.append(radio_buttons)
        print(f'question_groups: {len(self.question_groups)}')

    def create_button_groups(self):
        for group in self.question_groups:
            if group:
                button_group = QGroupBox(self)
                for btn in group:
                    button_group.addButton(btn)
                self.button_groups.append(button_group)
        print(f'button_group: {self.button_groups}')

    def setup_navigation(self):
        self.ui.listWidget.currentRowChanged.connect(
            self.ui.stackedWidget.setCurrentIndex
        )
        self.ui.listWidget.addItems(["Main","Survey"])


    def setup_connections(self):
        self.ui.SaveButton.clicked.connect(self.submit_survey)

    def get_selected_answers(self):
        answers = []
        print(f'answers: {answers}')
        for group in self.question_groups:
            selected = 0
            print(f"group: {group}")
            for i, btn in enumerate(group, 1):
                print(f"btn: {btn}")
                if btn.isChecked():
                    selected = i
                    break
            answers.append(selected)
        print(f"answers: {answers}")
        return answers

    def  submit_survey(self):
        answers = self.get_selected_answers()
        if 0 in answers:
            QMessageBox.warning(
                self,
                "Error",
                "Please answer all questions"
            )
        try:
            self.db.save_survey(answers)
            QMessageBox.information(
                self,
                "Success",
                "Survey submitted successfully"
            )
            for group in self.question_groups:
                for btn in group:
                    if btn:
                        btn.setAutoExclusive(False)
                        btn.setChecked(False)
                        btn.setAutoExclusive(True)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    def closeEvent(self, event):
        self.db.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = SurveyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

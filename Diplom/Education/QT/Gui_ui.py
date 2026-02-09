# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Gui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(291, 456)
        self.inputField = QLineEdit(Form)
        self.inputField.setObjectName(u"inputField")
        self.inputField.setGeometry(QRect(30, 20, 221, 61))
        self.button = QPushButton(Form)
        self.button.setObjectName(u"button")
        self.button.setGeometry(QRect(20, 90, 221, 21))
        self.output = QTextEdit(Form)
        self.output.setObjectName(u"output")
        self.output.setGeometry(QRect(20, 120, 231, 271))
        self.button2 = QPushButton(Form)
        self.button2.setObjectName(u"button2")
        self.button2.setGeometry(QRect(20, 400, 231, 23))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.button.setText(QCoreApplication.translate("Form", u"PushButton", None))
        self.button2.setText(QCoreApplication.translate("Form", u"PushButton", None))
    # retranslateUi


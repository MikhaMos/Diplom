# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menu1 = QMenu(self.menubar)
        self.menu1.setObjectName(u"menu1")
        self.menu2 = QMenu(self.menubar)
        self.menu2.setObjectName(u"menu2")
        self.menu3 = QMenu(self.menubar)
        self.menu3.setObjectName(u"menu3")
        self.menu4 = QMenu(self.menubar)
        self.menu4.setObjectName(u"menu4")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu1.menuAction())
        self.menubar.addAction(self.menu2.menuAction())
        self.menubar.addAction(self.menu3.menuAction())
        self.menubar.addAction(self.menu4.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menu1.setTitle(QCoreApplication.translate("MainWindow", u"1", None))
        self.menu2.setTitle(QCoreApplication.translate("MainWindow", u"2", None))
        self.menu3.setTitle(QCoreApplication.translate("MainWindow", u"3", None))
        self.menu4.setTitle(QCoreApplication.translate("MainWindow", u"4", None))
    # retranslateUi


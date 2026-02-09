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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(20, 30, 191, 531))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.XLabel = QLabel(self.verticalLayoutWidget)
        self.XLabel.setObjectName(u"XLabel")
        self.XLabel.setMaximumSize(QSize(15, 15))

        self.horizontalLayout.addWidget(self.XLabel)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.XForwardButton = QPushButton(self.verticalLayoutWidget)
        self.XForwardButton.setObjectName(u"XForwardButton")

        self.verticalLayout_3.addWidget(self.XForwardButton)

        self.XBackwardButton = QPushButton(self.verticalLayoutWidget)
        self.XBackwardButton.setObjectName(u"XBackwardButton")

        self.verticalLayout_3.addWidget(self.XBackwardButton)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetNoConstraint)
        self.YLabel = QLabel(self.verticalLayoutWidget)
        self.YLabel.setObjectName(u"YLabel")
        self.YLabel.setMaximumSize(QSize(15, 15))

        self.horizontalLayout_2.addWidget(self.YLabel)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.YForwardButton = QPushButton(self.verticalLayoutWidget)
        self.YForwardButton.setObjectName(u"YForwardButton")

        self.verticalLayout_4.addWidget(self.YForwardButton)

        self.YBackwardButton = QPushButton(self.verticalLayoutWidget)
        self.YBackwardButton.setObjectName(u"YBackwardButton")

        self.verticalLayout_4.addWidget(self.YBackwardButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SetNoConstraint)
        self.ZLabel = QLabel(self.verticalLayoutWidget)
        self.ZLabel.setObjectName(u"ZLabel")
        self.ZLabel.setMaximumSize(QSize(15, 15))

        self.horizontalLayout_3.addWidget(self.ZLabel)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.ZForwardButton = QPushButton(self.verticalLayoutWidget)
        self.ZForwardButton.setObjectName(u"ZForwardButton")

        self.verticalLayout_5.addWidget(self.ZForwardButton)

        self.ZBackwardButton = QPushButton(self.verticalLayoutWidget)
        self.ZBackwardButton.setObjectName(u"ZBackwardButton")

        self.verticalLayout_5.addWidget(self.ZBackwardButton)


        self.horizontalLayout_3.addLayout(self.verticalLayout_5)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setSizeConstraint(QLayout.SetNoConstraint)
        self.ALabel = QLabel(self.verticalLayoutWidget)
        self.ALabel.setObjectName(u"ALabel")
        self.ALabel.setMaximumSize(QSize(15, 15))

        self.horizontalLayout_4.addWidget(self.ALabel)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.AForwardButton = QPushButton(self.verticalLayoutWidget)
        self.AForwardButton.setObjectName(u"AForwardButton")

        self.verticalLayout_6.addWidget(self.AForwardButton)

        self.ABackwardButton = QPushButton(self.verticalLayoutWidget)
        self.ABackwardButton.setObjectName(u"ABackwardButton")

        self.verticalLayout_6.addWidget(self.ABackwardButton)


        self.horizontalLayout_4.addLayout(self.verticalLayout_6)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setSizeConstraint(QLayout.SetNoConstraint)
        self.BLabel = QLabel(self.verticalLayoutWidget)
        self.BLabel.setObjectName(u"BLabel")
        self.BLabel.setMaximumSize(QSize(15, 15))

        self.horizontalLayout_5.addWidget(self.BLabel)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.BForwardButton = QPushButton(self.verticalLayoutWidget)
        self.BForwardButton.setObjectName(u"BForwardButton")

        self.verticalLayout_7.addWidget(self.BForwardButton)

        self.BBackwardButton = QPushButton(self.verticalLayoutWidget)
        self.BBackwardButton.setObjectName(u"BBackwardButton")

        self.verticalLayout_7.addWidget(self.BBackwardButton)


        self.horizontalLayout_5.addLayout(self.verticalLayout_7)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setSizeConstraint(QLayout.SetNoConstraint)
        self.CLabel = QLabel(self.verticalLayoutWidget)
        self.CLabel.setObjectName(u"CLabel")
        self.CLabel.setMaximumSize(QSize(15, 15))

        self.horizontalLayout_6.addWidget(self.CLabel)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.CForwardButton = QPushButton(self.verticalLayoutWidget)
        self.CForwardButton.setObjectName(u"CForwardButton")

        self.verticalLayout_9.addWidget(self.CForwardButton)

        self.CBackwardButton = QPushButton(self.verticalLayoutWidget)
        self.CBackwardButton.setObjectName(u"CBackwardButton")

        self.verticalLayout_9.addWidget(self.CBackwardButton)


        self.horizontalLayout_6.addLayout(self.verticalLayout_9)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.Output = QTextEdit(self.centralwidget)
        self.Output.setObjectName(u"Output")
        self.Output.setGeometry(QRect(520, 120, 261, 431))
        self.Output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.lnput = QLineEdit(self.centralwidget)
        self.lnput.setObjectName(u"lnput")
        self.lnput.setGeometry(QRect(380, 40, 401, 61))
        self.positions = QTextEdit(self.centralwidget)
        self.positions.setObjectName(u"positions")
        self.positions.setGeometry(QRect(230, 360, 191, 161))
        self.positions.setAutoFillBackground(False)
        self.positions.setFrameShape(QFrame.NoFrame)
        self.positions.setFrameShadow(QFrame.Plain)
        self.positions.setLineWidth(0)
        self.positions.setUndoRedoEnabled(True)
        self.positions.setReadOnly(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.XLabel.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.XForwardButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.XBackwardButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.YLabel.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.YForwardButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.YBackwardButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.ZLabel.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.ZForwardButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.ZBackwardButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.ALabel.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.AForwardButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.ABackwardButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.BLabel.setText(QCoreApplication.translate("MainWindow", u"B", None))
        self.BForwardButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.BBackwardButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.CLabel.setText(QCoreApplication.translate("MainWindow", u"C", None))
        self.CForwardButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.CBackwardButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
    # retranslateUi


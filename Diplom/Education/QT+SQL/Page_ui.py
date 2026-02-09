# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Page.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QStackedWidget, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(763, 531)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(30, 90, 701, 441))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.horizontalLayoutWidget_6 = QWidget(self.page)
        self.horizontalLayoutWidget_6.setObjectName(u"horizontalLayoutWidget_6")
        self.horizontalLayoutWidget_6.setGeometry(QRect(40, 60, 301, 141))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget_6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton_4 = QPushButton(self.horizontalLayoutWidget_6)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.verticalLayout_2.addWidget(self.pushButton_4)

        self.pushButton_2 = QPushButton(self.horizontalLayoutWidget_6)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_2.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.horizontalLayoutWidget_6)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.verticalLayout_2.addWidget(self.pushButton_3)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton_5 = QPushButton(self.horizontalLayoutWidget_6)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.verticalLayout_3.addWidget(self.pushButton_5)

        self.pushButton_6 = QPushButton(self.horizontalLayoutWidget_6)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.verticalLayout_3.addWidget(self.pushButton_6)

        self.pushButton_7 = QPushButton(self.horizontalLayoutWidget_6)
        self.pushButton_7.setObjectName(u"pushButton_7")

        self.verticalLayout_3.addWidget(self.pushButton_7)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.Out = QTextEdit(self.page)
        self.Out.setObjectName(u"Out")
        self.Out.setGeometry(QRect(20, 220, 241, 211))
        self.stackedWidget.addWidget(self.page)
        self.Survey = QWidget()
        self.Survey.setObjectName(u"Survey")
        self.verticalLayoutWidget = QWidget(self.Survey)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(20, 20, 681, 291))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.Question1 = QHBoxLayout()
        self.Question1.setSpacing(0)
        self.Question1.setObjectName(u"Question1")
        self.label_1 = QLabel(self.verticalLayoutWidget)
        self.label_1.setObjectName(u"label_1")
        self.label_1.setMaximumSize(QSize(60, 16777215))

        self.Question1.addWidget(self.label_1)

        self.groupBox_q1 = QGroupBox(self.verticalLayoutWidget)
        self.groupBox_q1.setObjectName(u"groupBox_q1")
        self.horizontalLayoutWidget = QWidget(self.groupBox_q1)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 617, 66))
        self.answers1 = QHBoxLayout(self.horizontalLayoutWidget)
        self.answers1.setSpacing(10)
        self.answers1.setObjectName(u"answers1")
        self.answers1.setContentsMargins(0, 0, 0, 0)
        self.radioButton_q1_1 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_1.setObjectName(u"radioButton_q1_1")
        self.radioButton_q1_1.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_1)

        self.radioButton_q1_2 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_2.setObjectName(u"radioButton_q1_2")
        self.radioButton_q1_2.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_2)

        self.radioButton_q1_3 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_3.setObjectName(u"radioButton_q1_3")
        self.radioButton_q1_3.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_3)

        self.radioButton_q1_4 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_4.setObjectName(u"radioButton_q1_4")
        self.radioButton_q1_4.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_4)

        self.radioButton_q1_5 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_5.setObjectName(u"radioButton_q1_5")
        self.radioButton_q1_5.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_5)

        self.radioButton_q1_6 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_6.setObjectName(u"radioButton_q1_6")
        self.radioButton_q1_6.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_6)

        self.radioButton_q1_7 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_7.setObjectName(u"radioButton_q1_7")
        self.radioButton_q1_7.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_7)

        self.radioButton_q1_8 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_8.setObjectName(u"radioButton_q1_8")
        self.radioButton_q1_8.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_8)

        self.radioButton_q1_9 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_9.setObjectName(u"radioButton_q1_9")
        self.radioButton_q1_9.setMaximumSize(QSize(25, 16777215))

        self.answers1.addWidget(self.radioButton_q1_9)

        self.radioButton_q1_10 = QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_q1_10.setObjectName(u"radioButton_q1_10")
        self.radioButton_q1_10.setMaximumSize(QSize(40, 16777215))

        self.answers1.addWidget(self.radioButton_q1_10)


        self.Question1.addWidget(self.groupBox_q1)


        self.verticalLayout.addLayout(self.Question1)

        self.Question2 = QHBoxLayout()
        self.Question2.setSpacing(0)
        self.Question2.setObjectName(u"Question2")
        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(60, 16777215))

        self.Question2.addWidget(self.label_2)

        self.groupBox_q2 = QGroupBox(self.verticalLayoutWidget)
        self.groupBox_q2.setObjectName(u"groupBox_q2")
        self.widget = QWidget(self.groupBox_q2)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 617, 66))
        self.answers2_2 = QHBoxLayout(self.widget)
        self.answers2_2.setSpacing(10)
        self.answers2_2.setObjectName(u"answers2_2")
        self.answers2_2.setContentsMargins(0, 0, 0, 0)
        self.radioButton_q2_1 = QRadioButton(self.widget)
        self.radioButton_q2_1.setObjectName(u"radioButton_q2_1")
        self.radioButton_q2_1.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_1)

        self.radioButton_q2_2 = QRadioButton(self.widget)
        self.radioButton_q2_2.setObjectName(u"radioButton_q2_2")
        self.radioButton_q2_2.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_2)

        self.radioButton_q2_3 = QRadioButton(self.widget)
        self.radioButton_q2_3.setObjectName(u"radioButton_q2_3")
        self.radioButton_q2_3.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_3)

        self.radioButton_q2_4 = QRadioButton(self.widget)
        self.radioButton_q2_4.setObjectName(u"radioButton_q2_4")
        self.radioButton_q2_4.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_4)

        self.radioButton_q2_5 = QRadioButton(self.widget)
        self.radioButton_q2_5.setObjectName(u"radioButton_q2_5")
        self.radioButton_q2_5.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_5)

        self.radioButton_q2_6 = QRadioButton(self.widget)
        self.radioButton_q2_6.setObjectName(u"radioButton_q2_6")
        self.radioButton_q2_6.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_6)

        self.radioButton_q2_7 = QRadioButton(self.widget)
        self.radioButton_q2_7.setObjectName(u"radioButton_q2_7")
        self.radioButton_q2_7.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_7)

        self.radioButton_q2_8 = QRadioButton(self.widget)
        self.radioButton_q2_8.setObjectName(u"radioButton_q2_8")
        self.radioButton_q2_8.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_8)

        self.radioButton_q2_9 = QRadioButton(self.widget)
        self.radioButton_q2_9.setObjectName(u"radioButton_q2_9")
        self.radioButton_q2_9.setMaximumSize(QSize(25, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_9)

        self.radioButton_q2_10 = QRadioButton(self.widget)
        self.radioButton_q2_10.setObjectName(u"radioButton_q2_10")
        self.radioButton_q2_10.setMaximumSize(QSize(40, 16777215))

        self.answers2_2.addWidget(self.radioButton_q2_10)


        self.Question2.addWidget(self.groupBox_q2)


        self.verticalLayout.addLayout(self.Question2)

        self.Question3 = QHBoxLayout()
        self.Question3.setSpacing(0)
        self.Question3.setObjectName(u"Question3")
        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(60, 16777215))

        self.Question3.addWidget(self.label_3)

        self.groupBox_q3 = QGroupBox(self.verticalLayoutWidget)
        self.groupBox_q3.setObjectName(u"groupBox_q3")
        self.widget1 = QWidget(self.groupBox_q3)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(0, 0, 617, 65))
        self.answers3_2 = QHBoxLayout(self.widget1)
        self.answers3_2.setSpacing(10)
        self.answers3_2.setObjectName(u"answers3_2")
        self.answers3_2.setContentsMargins(0, 0, 0, 0)
        self.radioButton_q3_10 = QRadioButton(self.widget1)
        self.radioButton_q3_10.setObjectName(u"radioButton_q3_10")
        self.radioButton_q3_10.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_10)

        self.radioButton_q3_2 = QRadioButton(self.widget1)
        self.radioButton_q3_2.setObjectName(u"radioButton_q3_2")
        self.radioButton_q3_2.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_2)

        self.radioButton_q3_3 = QRadioButton(self.widget1)
        self.radioButton_q3_3.setObjectName(u"radioButton_q3_3")
        self.radioButton_q3_3.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_3)

        self.radioButton_q3_4 = QRadioButton(self.widget1)
        self.radioButton_q3_4.setObjectName(u"radioButton_q3_4")
        self.radioButton_q3_4.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_4)

        self.radioButton_q3_5 = QRadioButton(self.widget1)
        self.radioButton_q3_5.setObjectName(u"radioButton_q3_5")
        self.radioButton_q3_5.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_5)

        self.radioButton_q3_6 = QRadioButton(self.widget1)
        self.radioButton_q3_6.setObjectName(u"radioButton_q3_6")
        self.radioButton_q3_6.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_6)

        self.radioButton_q3_7 = QRadioButton(self.widget1)
        self.radioButton_q3_7.setObjectName(u"radioButton_q3_7")
        self.radioButton_q3_7.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_7)

        self.radioButton_q3_8 = QRadioButton(self.widget1)
        self.radioButton_q3_8.setObjectName(u"radioButton_q3_8")
        self.radioButton_q3_8.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_8)

        self.radioButton_q3_9 = QRadioButton(self.widget1)
        self.radioButton_q3_9.setObjectName(u"radioButton_q3_9")
        self.radioButton_q3_9.setMaximumSize(QSize(25, 16777215))

        self.answers3_2.addWidget(self.radioButton_q3_9)

        self.radioButton_40 = QRadioButton(self.widget1)
        self.radioButton_40.setObjectName(u"radioButton_40")
        self.radioButton_40.setMaximumSize(QSize(40, 16777215))

        self.answers3_2.addWidget(self.radioButton_40)


        self.Question3.addWidget(self.groupBox_q3)


        self.verticalLayout.addLayout(self.Question3)

        self.Question4 = QHBoxLayout()
        self.Question4.setSpacing(0)
        self.Question4.setObjectName(u"Question4")
        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(60, 16777215))

        self.Question4.addWidget(self.label_4)

        self.groupBox_q4 = QGroupBox(self.verticalLayoutWidget)
        self.groupBox_q4.setObjectName(u"groupBox_q4")
        self.widget2 = QWidget(self.groupBox_q4)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setGeometry(QRect(0, 0, 617, 66))
        self.answers4 = QHBoxLayout(self.widget2)
        self.answers4.setSpacing(10)
        self.answers4.setObjectName(u"answers4")
        self.answers4.setContentsMargins(0, 0, 0, 0)
        self.radioButton_q4_1 = QRadioButton(self.widget2)
        self.radioButton_q4_1.setObjectName(u"radioButton_q4_1")
        self.radioButton_q4_1.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_1)

        self.radioButton_q4_2 = QRadioButton(self.widget2)
        self.radioButton_q4_2.setObjectName(u"radioButton_q4_2")
        self.radioButton_q4_2.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_2)

        self.radioButton_q4_3 = QRadioButton(self.widget2)
        self.radioButton_q4_3.setObjectName(u"radioButton_q4_3")
        self.radioButton_q4_3.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_3)

        self.radioButton_q4_4 = QRadioButton(self.widget2)
        self.radioButton_q4_4.setObjectName(u"radioButton_q4_4")
        self.radioButton_q4_4.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_4)

        self.radioButton_q4_5 = QRadioButton(self.widget2)
        self.radioButton_q4_5.setObjectName(u"radioButton_q4_5")
        self.radioButton_q4_5.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_5)

        self.radioButton_q4_6 = QRadioButton(self.widget2)
        self.radioButton_q4_6.setObjectName(u"radioButton_q4_6")
        self.radioButton_q4_6.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_6)

        self.radioButton_q4_7 = QRadioButton(self.widget2)
        self.radioButton_q4_7.setObjectName(u"radioButton_q4_7")
        self.radioButton_q4_7.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_7)

        self.radioButton_q4_8 = QRadioButton(self.widget2)
        self.radioButton_q4_8.setObjectName(u"radioButton_q4_8")
        self.radioButton_q4_8.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_8)

        self.radioButton_q4_9 = QRadioButton(self.widget2)
        self.radioButton_q4_9.setObjectName(u"radioButton_q4_9")
        self.radioButton_q4_9.setMaximumSize(QSize(25, 16777215))

        self.answers4.addWidget(self.radioButton_q4_9)

        self.radioButton_q4_10 = QRadioButton(self.widget2)
        self.radioButton_q4_10.setObjectName(u"radioButton_q4_10")
        self.radioButton_q4_10.setMaximumSize(QSize(40, 16777215))

        self.answers4.addWidget(self.radioButton_q4_10)


        self.Question4.addWidget(self.groupBox_q4)


        self.verticalLayout.addLayout(self.Question4)

        self.SaveButton = QPushButton(self.Survey)
        self.SaveButton.setObjectName(u"SaveButton")
        self.SaveButton.setGeometry(QRect(500, 350, 131, 51))
        self.stackedWidget.addWidget(self.Survey)
        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setGeometry(QRect(10, 30, 771, 41))
        self.listWidget.setFrameShape(QFrame.NoFrame)
        self.listWidget.setFrameShadow(QFrame.Sunken)
        self.listWidget.setFlow(QListView.LeftToRight)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 763, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.label_1.setText(QCoreApplication.translate("MainWindow", u"Question 1", None))
        self.groupBox_q1.setTitle("")
        self.radioButton_q1_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.radioButton_q1_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.radioButton_q1_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.radioButton_q1_4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.radioButton_q1_5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.radioButton_q1_6.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.radioButton_q1_7.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.radioButton_q1_8.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.radioButton_q1_9.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.radioButton_q1_10.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Question 2", None))
        self.groupBox_q2.setTitle("")
        self.radioButton_q2_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.radioButton_q2_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.radioButton_q2_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.radioButton_q2_4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.radioButton_q2_5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.radioButton_q2_6.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.radioButton_q2_7.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.radioButton_q2_8.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.radioButton_q2_9.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.radioButton_q2_10.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Question 3", None))
        self.groupBox_q3.setTitle("")
        self.radioButton_q3_10.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.radioButton_q3_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.radioButton_q3_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.radioButton_q3_4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.radioButton_q3_5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.radioButton_q3_6.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.radioButton_q3_7.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.radioButton_q3_8.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.radioButton_q3_9.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.radioButton_40.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Question 4", None))
        self.groupBox_q4.setTitle("")
        self.radioButton_q4_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.radioButton_q4_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.radioButton_q4_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.radioButton_q4_4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.radioButton_q4_5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.radioButton_q4_6.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.radioButton_q4_7.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.radioButton_q4_8.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.radioButton_q4_9.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.radioButton_q4_10.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.SaveButton.setText(QCoreApplication.translate("MainWindow", u"ButtonResponce", None))
    # retranslateUi


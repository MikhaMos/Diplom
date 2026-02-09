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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QStackedWidget, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(880, 702)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(200, 80, 671, 551))
        self.ControlPage = QWidget()
        self.ControlPage.setObjectName(u"ControlPage")
        self.MoveBox = QGroupBox(self.ControlPage)
        self.MoveBox.setObjectName(u"MoveBox")
        self.MoveBox.setGeometry(QRect(490, 10, 171, 471))
        self.verticalLayoutWidget_2 = QWidget(self.MoveBox)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 10, 160, 461))
        self.verticalLayout_6 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.XForward = QPushButton(self.verticalLayoutWidget_2)
        self.XForward.setObjectName(u"XForward")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.XForward.sizePolicy().hasHeightForWidth())
        self.XForward.setSizePolicy(sizePolicy)
        self.XForward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_5.addWidget(self.XForward)

        self.XBackward = QPushButton(self.verticalLayoutWidget_2)
        self.XBackward.setObjectName(u"XBackward")
        sizePolicy.setHeightForWidth(self.XBackward.sizePolicy().hasHeightForWidth())
        self.XBackward.setSizePolicy(sizePolicy)
        self.XBackward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_5.addWidget(self.XBackward)


        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.YForward = QPushButton(self.verticalLayoutWidget_2)
        self.YForward.setObjectName(u"YForward")
        self.YForward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_8.addWidget(self.YForward)

        self.YBackward = QPushButton(self.verticalLayoutWidget_2)
        self.YBackward.setObjectName(u"YBackward")
        self.YBackward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_8.addWidget(self.YBackward)


        self.verticalLayout_6.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.ZForward = QPushButton(self.verticalLayoutWidget_2)
        self.ZForward.setObjectName(u"ZForward")
        self.ZForward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_9.addWidget(self.ZForward)

        self.ZBackward = QPushButton(self.verticalLayoutWidget_2)
        self.ZBackward.setObjectName(u"ZBackward")
        self.ZBackward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_9.addWidget(self.ZBackward)


        self.verticalLayout_6.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.AForward = QPushButton(self.verticalLayoutWidget_2)
        self.AForward.setObjectName(u"AForward")
        self.AForward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_10.addWidget(self.AForward)

        self.ABackward = QPushButton(self.verticalLayoutWidget_2)
        self.ABackward.setObjectName(u"ABackward")
        self.ABackward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_10.addWidget(self.ABackward)


        self.verticalLayout_6.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.BForward = QPushButton(self.verticalLayoutWidget_2)
        self.BForward.setObjectName(u"BForward")
        self.BForward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_11.addWidget(self.BForward)

        self.BBackward = QPushButton(self.verticalLayoutWidget_2)
        self.BBackward.setObjectName(u"BBackward")
        self.BBackward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_11.addWidget(self.BBackward)


        self.verticalLayout_6.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.CForward = QPushButton(self.verticalLayoutWidget_2)
        self.CForward.setObjectName(u"CForward")
        self.CForward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_12.addWidget(self.CForward)

        self.CBackward = QPushButton(self.verticalLayoutWidget_2)
        self.CBackward.setObjectName(u"CBackward")
        self.CBackward.setMaximumSize(QSize(16777215, 50))

        self.horizontalLayout_12.addWidget(self.CBackward)


        self.verticalLayout_6.addLayout(self.horizontalLayout_12)

        self.OutputCode = QGroupBox(self.ControlPage)
        self.OutputCode.setObjectName(u"OutputCode")
        self.OutputCode.setGeometry(QRect(0, 10, 491, 471))
        self.verticalLayoutWidget_5 = QWidget(self.OutputCode)
        self.verticalLayoutWidget_5.setObjectName(u"verticalLayoutWidget_5")
        self.verticalLayoutWidget_5.setGeometry(QRect(10, 10, 471, 451))
        self.verticalLayout_9 = QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.Code = QTextEdit(self.verticalLayoutWidget_5)
        self.Code.setObjectName(u"Code")
        self.Code.setReadOnly(True)

        self.verticalLayout_9.addWidget(self.Code)

        self.ParametrsButtons = QGroupBox(self.ControlPage)
        self.ParametrsButtons.setObjectName(u"ParametrsButtons")
        self.ParametrsButtons.setGeometry(QRect(0, 480, 491, 71))
        self.horizontalLayoutWidget = QWidget(self.ParametrsButtons)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 471, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.HomeButton = QPushButton(self.horizontalLayoutWidget)
        self.HomeButton.setObjectName(u"HomeButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.HomeButton.sizePolicy().hasHeightForWidth())
        self.HomeButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.HomeButton)

        self.PointButton = QPushButton(self.horizontalLayoutWidget)
        self.PointButton.setObjectName(u"PointButton")
        sizePolicy1.setHeightForWidth(self.PointButton.sizePolicy().hasHeightForWidth())
        self.PointButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.PointButton)

        self.pushButton_23 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_23.setObjectName(u"pushButton_23")
        sizePolicy1.setHeightForWidth(self.pushButton_23.sizePolicy().hasHeightForWidth())
        self.pushButton_23.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pushButton_23)

        self.pushButton_24 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_24.setObjectName(u"pushButton_24")
        sizePolicy1.setHeightForWidth(self.pushButton_24.sizePolicy().hasHeightForWidth())
        self.pushButton_24.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pushButton_24)

        self.stackedWidget.addWidget(self.ControlPage)
        self.SurvayPage = QWidget()
        self.SurvayPage.setObjectName(u"SurvayPage")
        self.StatusSurvey = QGroupBox(self.SurvayPage)
        self.StatusSurvey.setObjectName(u"StatusSurvey")
        self.StatusSurvey.setGeometry(QRect(10, 10, 161, 81))
        self.verticalLayoutWidget_3 = QWidget(self.StatusSurvey)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 160, 80))
        self.verticalLayout_7 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.verticalLayoutWidget_3)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_7.addWidget(self.label_8)

        self.label_9 = QLabel(self.verticalLayoutWidget_3)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_7.addWidget(self.label_9)

        self.label_10 = QLabel(self.verticalLayoutWidget_3)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_7.addWidget(self.label_10)

        self.Question = QGroupBox(self.SurvayPage)
        self.Question.setObjectName(u"Question")
        self.Question.setGeometry(QRect(10, 120, 651, 81))
        self.horizontalLayoutWidget_7 = QWidget(self.Question)
        self.horizontalLayoutWidget_7.setObjectName(u"horizontalLayoutWidget_7")
        self.horizontalLayoutWidget_7.setGeometry(QRect(0, 0, 651, 81))
        self.horizontalLayout_13 = QHBoxLayout(self.horizontalLayoutWidget_7)
        self.horizontalLayout_13.setSpacing(1)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.horizontalLayoutWidget_7)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_13.addWidget(self.label_11)

        self.radioButton = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_2)

        self.radioButton_3 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_3.setObjectName(u"radioButton_3")
        self.radioButton_3.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_3)

        self.radioButton_4 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_4.setObjectName(u"radioButton_4")
        self.radioButton_4.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_4)

        self.radioButton_5 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_5.setObjectName(u"radioButton_5")
        self.radioButton_5.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_5)

        self.radioButton_6 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_6.setObjectName(u"radioButton_6")
        self.radioButton_6.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_6)

        self.radioButton_8 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_8.setObjectName(u"radioButton_8")
        self.radioButton_8.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_8)

        self.radioButton_7 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_7.setObjectName(u"radioButton_7")
        self.radioButton_7.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_7)

        self.radioButton_9 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_9.setObjectName(u"radioButton_9")
        self.radioButton_9.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_9)

        self.radioButton_10 = QRadioButton(self.horizontalLayoutWidget_7)
        self.radioButton_10.setObjectName(u"radioButton_10")
        self.radioButton_10.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout_13.addWidget(self.radioButton_10)

        self.HistorySurvey = QGroupBox(self.SurvayPage)
        self.HistorySurvey.setObjectName(u"HistorySurvey")
        self.HistorySurvey.setGeometry(QRect(20, 410, 331, 131))
        self.HistorySurvey.setFlat(False)
        self.verticalLayoutWidget_4 = QWidget(self.HistorySurvey)
        self.verticalLayoutWidget_4.setObjectName(u"verticalLayoutWidget_4")
        self.verticalLayoutWidget_4.setGeometry(QRect(0, 20, 311, 111))
        self.verticalLayout_8 = QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.textEdit_2 = QTextEdit(self.verticalLayoutWidget_4)
        self.textEdit_2.setObjectName(u"textEdit_2")

        self.verticalLayout_8.addWidget(self.textEdit_2)

        self.SentAnswer = QPushButton(self.SurvayPage)
        self.SentAnswer.setObjectName(u"SentAnswer")
        self.SentAnswer.setGeometry(QRect(530, 480, 111, 41))
        self.stackedWidget.addWidget(self.SurvayPage)
        self.StatusPanel = QLabel(self.centralwidget)
        self.StatusPanel.setObjectName(u"StatusPanel")
        self.StatusPanel.setGeometry(QRect(10, 90, 51, 21))
        self.StatusPanel_2 = QGroupBox(self.centralwidget)
        self.StatusPanel_2.setObjectName(u"StatusPanel_2")
        self.StatusPanel_2.setGeometry(QRect(10, 120, 161, 81))
        self.verticalLayoutWidget = QWidget(self.StatusPanel_2)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 160, 80))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.TimeLabel = QLabel(self.centralwidget)
        self.TimeLabel.setObjectName(u"TimeLabel")
        self.TimeLabel.setGeometry(QRect(10, 10, 121, 16))
        self.StatusRobot = QGroupBox(self.centralwidget)
        self.StatusRobot.setObjectName(u"StatusRobot")
        self.StatusRobot.setGeometry(QRect(690, 0, 181, 21))
        self.horizontalLayoutWidget_8 = QWidget(self.StatusRobot)
        self.horizontalLayoutWidget_8.setObjectName(u"horizontalLayoutWidget_8")
        self.horizontalLayoutWidget_8.setGeometry(QRect(0, 0, 181, 21))
        self.horizontalLayout_14 = QHBoxLayout(self.horizontalLayoutWidget_8)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.horizontalLayoutWidget_8)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_14.addWidget(self.label_5)

        self.label_6 = QLabel(self.horizontalLayoutWidget_8)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_14.addWidget(self.label_6)

        self.label_7 = QLabel(self.horizontalLayoutWidget_8)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_14.addWidget(self.label_7)

        self.Positions = QGroupBox(self.centralwidget)
        self.Positions.setObjectName(u"Positions")
        self.Positions.setGeometry(QRect(10, 480, 171, 141))
        self.OutputPos = QTextEdit(self.Positions)
        self.OutputPos.setObjectName(u"OutputPos")
        self.OutputPos.setGeometry(QRect(0, 0, 171, 141))
        self.OutputPos.setReadOnly(True)
        self.OutLog = QGroupBox(self.centralwidget)
        self.OutLog.setObjectName(u"OutLog")
        self.OutLog.setGeometry(QRect(10, 220, 171, 221))
        self.verticalLayoutWidget_7 = QWidget(self.OutLog)
        self.verticalLayoutWidget_7.setObjectName(u"verticalLayoutWidget_7")
        self.verticalLayoutWidget_7.setGeometry(QRect(0, 0, 171, 221))
        self.verticalLayout_11 = QVBoxLayout(self.verticalLayoutWidget_7)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.Output = QTextEdit(self.verticalLayoutWidget_7)
        self.Output.setObjectName(u"Output")
        self.Output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.Output.setReadOnly(True)

        self.verticalLayout_11.addWidget(self.Output)

        self.PagesButton = QGroupBox(self.centralwidget)
        self.PagesButton.setObjectName(u"PagesButton")
        self.PagesButton.setGeometry(QRect(10, 30, 861, 51))
        self.horizontalLayoutWidget_2 = QWidget(self.PagesButton)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(0, 0, 861, 51))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.ControlPageButton = QPushButton(self.horizontalLayoutWidget_2)
        self.ControlPageButton.setObjectName(u"ControlPageButton")
        sizePolicy1.setHeightForWidth(self.ControlPageButton.sizePolicy().hasHeightForWidth())
        self.ControlPageButton.setSizePolicy(sizePolicy1)
        self.ControlPageButton.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.ControlPageButton)

        self.SurveyPageButton = QPushButton(self.horizontalLayoutWidget_2)
        self.SurveyPageButton.setObjectName(u"SurveyPageButton")
        sizePolicy1.setHeightForWidth(self.SurveyPageButton.sizePolicy().hasHeightForWidth())
        self.SurveyPageButton.setSizePolicy(sizePolicy1)
        self.SurveyPageButton.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.SurveyPageButton)

        self.pushButton_5 = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy1)
        self.pushButton_5.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_5)

        self.pushButton_6 = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy1.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy1)
        self.pushButton_6.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_6)

        self.pushButton_7 = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_7.setObjectName(u"pushButton_7")
        sizePolicy1.setHeightForWidth(self.pushButton_7.sizePolicy().hasHeightForWidth())
        self.pushButton_7.setSizePolicy(sizePolicy1)
        self.pushButton_7.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_7)

        self.pushButton_8 = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_8.setObjectName(u"pushButton_8")
        sizePolicy1.setHeightForWidth(self.pushButton_8.sizePolicy().hasHeightForWidth())
        self.pushButton_8.setSizePolicy(sizePolicy1)
        self.pushButton_8.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_8)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 880, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.MoveBox.setTitle("")
        self.XForward.setText(QCoreApplication.translate("MainWindow", u"X+", None))
        self.XBackward.setText(QCoreApplication.translate("MainWindow", u"X-", None))
        self.YForward.setText(QCoreApplication.translate("MainWindow", u"Y+", None))
        self.YBackward.setText(QCoreApplication.translate("MainWindow", u"Y-", None))
        self.ZForward.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.ZBackward.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.AForward.setText(QCoreApplication.translate("MainWindow", u"A+", None))
        self.ABackward.setText(QCoreApplication.translate("MainWindow", u"A-", None))
        self.BForward.setText(QCoreApplication.translate("MainWindow", u"B+", None))
        self.BBackward.setText(QCoreApplication.translate("MainWindow", u"B-", None))
        self.CForward.setText(QCoreApplication.translate("MainWindow", u"C+", None))
        self.CBackward.setText(QCoreApplication.translate("MainWindow", u"C-", None))
        self.OutputCode.setTitle("")
        self.Code.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.ParametrsButtons.setTitle("")
        self.HomeButton.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.PointButton.setText(QCoreApplication.translate("MainWindow", u"Point", None))
        self.pushButton_23.setText("")
        self.pushButton_24.setText("")
        self.StatusSurvey.setTitle("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Question.setTitle("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.radioButton_4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.radioButton_5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.radioButton_6.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.radioButton_8.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.radioButton_7.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.radioButton_9.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.radioButton_10.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.HistorySurvey.setTitle(QCoreApplication.translate("MainWindow", u"\u0418\u0441\u0442\u043e\u0440\u0438\u044f", None))
        self.SentAnswer.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c", None))
        self.StatusPanel.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.StatusPanel_2.setTitle("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.TimeLabel.setText(QCoreApplication.translate("MainWindow", u"Time: ", None))
        self.StatusRobot.setTitle("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Positions.setTitle("")
        self.OutLog.setTitle("")
        self.PagesButton.setTitle("")
        self.ControlPageButton.setText(QCoreApplication.translate("MainWindow", u"\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435", None))
        self.SurveyPageButton.setText(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0440\u043e\u0441", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
    # retranslateUi


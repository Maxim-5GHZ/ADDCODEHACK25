# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1067, 634)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.verticalLayout.addItem(self.horizontalSpacer)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.login_main_button = QPushButton(self.centralwidget)
        self.login_main_button.setObjectName(u"login_main_button")
        self.login_main_button.setEnabled(True)
        font = QFont()
        font.setPointSize(12)
        self.login_main_button.setFont(font)
        self.login_main_button.setCheckable(False)

        self.horizontalLayout_3.addWidget(self.login_main_button)

        self.register_main_button = QPushButton(self.centralwidget)
        self.register_main_button.setObjectName(u"register_main_button")
        self.register_main_button.setFont(font)

        self.horizontalLayout_3.addWidget(self.register_main_button)


        self.horizontalLayout.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_analyze = QLabel(self.centralwidget)
        self.label_analyze.setObjectName(u"label_analyze")

        self.verticalLayout_4.addWidget(self.label_analyze)

        self.pushButton_Anayze_field = QPushButton(self.centralwidget)
        self.pushButton_Anayze_field.setObjectName(u"pushButton_Anayze_field")

        self.verticalLayout_4.addWidget(self.pushButton_Anayze_field)


        self.horizontalLayout_4.addLayout(self.verticalLayout_4)


        self.horizontalLayout_2.addLayout(self.horizontalLayout_4)

        self.label_history = QLabel(self.centralwidget)
        self.label_history.setObjectName(u"label_history")

        self.horizontalLayout_2.addWidget(self.label_history)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1067, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.login_main_button.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043e\u0439\u0442\u0438", None))
        self.register_main_button.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c\u0441\u044f", None))
        self.label_analyze.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pushButton_Anayze_field.setText(QCoreApplication.translate("MainWindow", u"\u0410\u043d\u0430\u043b\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043f\u043e\u043b\u0435", None))
        self.label_history.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi


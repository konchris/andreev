# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_helium.ui'
#
# Created: Wed Apr 23 20:54:29 2014
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(715, 279)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(250, 220))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.editSetVolume = QtGui.QLineEdit(self.groupBox)
        self.editSetVolume.setGeometry(QtCore.QRect(20, 120, 101, 20))
        self.editSetVolume.setObjectName(_fromUtf8("editSetVolume"))
        self.labelFlow = QtGui.QLabel(self.groupBox)
        self.labelFlow.setGeometry(QtCore.QRect(10, 60, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelFlow.setFont(font)
        self.labelFlow.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelFlow.setObjectName(_fromUtf8("labelFlow"))
        self.btnSetVolume = QtGui.QPushButton(self.groupBox)
        self.btnSetVolume.setGeometry(QtCore.QRect(130, 120, 71, 23))
        self.btnSetVolume.setObjectName(_fromUtf8("btnSetVolume"))
        self.labelVolume = QtGui.QLabel(self.groupBox)
        self.labelVolume.setGeometry(QtCore.QRect(20, 20, 181, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelVolume.setFont(font)
        self.labelVolume.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelVolume.setObjectName(_fromUtf8("labelVolume"))
        self.editRefresh = QtGui.QLineEdit(self.groupBox)
        self.editRefresh.setGeometry(QtCore.QRect(20, 170, 51, 20))
        self.editRefresh.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.editRefresh.setObjectName(_fromUtf8("editRefresh"))
        self.editRange = QtGui.QLineEdit(self.groupBox)
        self.editRange.setGeometry(QtCore.QRect(120, 170, 51, 20))
        self.editRange.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.editRange.setObjectName(_fromUtf8("editRange"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(80, 170, 16, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(180, 170, 16, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 150, 46, 13))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(120, 150, 71, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.groupBox)
        self.curvewidget = CurveWidget(self.centralwidget)
        self.curvewidget.setOrientation(QtCore.Qt.Horizontal)
        self.curvewidget.setObjectName(_fromUtf8("curvewidget"))
        self.horizontalLayout.addWidget(self.curvewidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 715, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Helium Monitor by David Weber", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFlow.setText(QtGui.QApplication.translate("MainWindow", "100 L/h", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSetVolume.setText(QtGui.QApplication.translate("MainWindow", "Set Volume", None, QtGui.QApplication.UnicodeUTF8))
        self.labelVolume.setText(QtGui.QApplication.translate("MainWindow", "7864320 L", None, QtGui.QApplication.UnicodeUTF8))
        self.editRefresh.setText(QtGui.QApplication.translate("MainWindow", "2", None, QtGui.QApplication.UnicodeUTF8))
        self.editRange.setText(QtGui.QApplication.translate("MainWindow", "20", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "s", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "s", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Interpolate", None, QtGui.QApplication.UnicodeUTF8))

from guiqwt.plot import CurveWidget

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Dashboard.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.background = QtWidgets.QLabel(self.centralwidget)
        self.background.setGeometry(QtCore.QRect(0, 0, 800, 480))
        self.background.setStyleSheet("QLabel#background{\n"
"    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(255, 255, 255, 255), stop:0.736318 rgba(0, 80, 120, 255));\n"
"}")
        self.background.setText("")
        self.background.setObjectName("background")
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(280, 140, 251, 181))
        self.logo.setStyleSheet("")
        self.logo.setObjectName("logo")
        self.speedometer = QtWidgets.QLCDNumber(self.centralwidget)
        self.speedometer.setGeometry(QtCore.QRect(60, 150, 171, 141))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.speedometer.setFont(font)
        self.speedometer.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.speedometer.setStyleSheet("color: white;\n"
"background-color: rgba(255,255,255,0)")
        self.speedometer.setSmallDecimalPoint(False)
        self.speedometer.setDigitCount(3)
        self.speedometer.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.speedometer.setProperty("intValue", 45)
        self.speedometer.setObjectName("speedometer")
        self.mphLabel = QtWidgets.QLabel(self.centralwidget)
        self.mphLabel.setGeometry(QtCore.QRect(130, 280, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.mphLabel.setFont(font)
        self.mphLabel.setStyleSheet("font-size: 20;\n"
"color:white;")
        self.mphLabel.setObjectName("mphLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(210, 10, 401, 102))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftArrow = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.leftArrow.setStyleSheet("border-image: url(:/img/leftArrow);")
        self.leftArrow.setObjectName("leftArrow")
        self.horizontalLayout.addWidget(self.leftArrow)
        self.gearPositionLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.gearPositionLabel.setStyleSheet("color: white;\n"
"font: 75 28pt \"MS Shell Dlg 2\";")
        self.gearPositionLabel.setObjectName("gearPositionLabel")
        self.horizontalLayout.addWidget(self.gearPositionLabel)
        self.rightArrow = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.rightArrow.setStyleSheet("border-image: url(:/img/rightArrow);")
        self.rightArrow.setObjectName("rightArrow")
        self.horizontalLayout.addWidget(self.rightArrow)
        self.shutdownButton = QtWidgets.QPushButton(self.centralwidget)
        self.shutdownButton.setGeometry(QtCore.QRect(20, 20, 51, 51))
        self.shutdownButton.setStyleSheet("QPushButton{\n"
"    border-image: url(:/img/shutdown);\n"
"}\n"
"QPushButton:pressed {\n"
"    border-image: url(:/img/shutdownRed);\n"
"}")
        self.shutdownButton.setText("")
        self.shutdownButton.setObjectName("shutdownButton")
        self.warningLabel = QtWidgets.QLabel(self.centralwidget)
        self.warningLabel.setGeometry(QtCore.QRect(620, 330, 71, 71))
        self.warningLabel.setStyleSheet("background-image: url(:/img/warningYellow);")
        self.warningLabel.setObjectName("warningLabel")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(540, 210, 231, 61))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.milesText = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.milesText.setFont(font)
        self.milesText.setStyleSheet("color: white;\n"
"font: 16pt \"MS Shell Dlg 2\";")
        self.milesText.setObjectName("milesText")
        self.gridLayout.addWidget(self.milesText, 0, 1, 1, 1)
        self.milesUnitLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.milesUnitLabel.setFont(font)
        self.milesUnitLabel.setStyleSheet("color: white;\n"
"font: 14pt \"MS Shell Dlg 2\";")
        self.milesUnitLabel.setObjectName("milesUnitLabel")
        self.gridLayout.addWidget(self.milesUnitLabel, 0, 2, 1, 1)
        self.milesLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.milesLabel.setFont(font)
        self.milesLabel.setStyleSheet("color: white;\n"
"font: 16pt \"MS Shell Dlg 2\";")
        self.milesLabel.setObjectName("milesLabel")
        self.gridLayout.addWidget(self.milesLabel, 0, 0, 1, 1)
        self.chargePercentageBar = QtWidgets.QProgressBar(self.centralwidget)
        self.chargePercentageBar.setGeometry(QtCore.QRect(540, 160, 231, 41))
        self.chargePercentageBar.setStyleSheet(" QProgressBar::chunk {\n"
"     background-color: #3add36;\n"
"     width: 1px;\n"
" }\n"
"\n"
" QProgressBar {\n"
"     border: 2px solid grey;\n"
"     border-radius: 0px;\n"
"     text-align: center;\n"
" }")
        self.chargePercentageBar.setProperty("value", 90)
        self.chargePercentageBar.setInvertedAppearance(False)
        self.chargePercentageBar.setObjectName("chargePercentageBar")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(320, 410, 160, 51))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.hazardsLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.hazardsLabel.setStyleSheet("background-image: url(:/img/hazards);")
        self.hazardsLabel.setText("")
        self.hazardsLabel.setObjectName("hazardsLabel")
        self.horizontalLayout_3.addWidget(self.hazardsLabel)
        self.cruiseControlLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.cruiseControlLabel.setStyleSheet("background-image: url(:/img/cruiseControl);")
        self.cruiseControlLabel.setText("")
        self.cruiseControlLabel.setObjectName("cruiseControlLabel")
        self.horizontalLayout_3.addWidget(self.cruiseControlLabel)
        self.lowBeamsLogo = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.lowBeamsLogo.setStyleSheet("background-image: url(:/img/lowbeams);")
        self.lowBeamsLogo.setText("")
        self.lowBeamsLogo.setObjectName("lowBeamsLogo")
        self.horizontalLayout_3.addWidget(self.lowBeamsLogo)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.logo.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><img src=\":/img/logo\"width=\"220\" height=\"190\"/></p></body></html>"))
        self.mphLabel.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">MPH</span></p></body></html>"))
        self.leftArrow.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><br/></p></body></html>"))
        self.gearPositionLabel.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">D</p></body></html>"))
        self.rightArrow.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><br/></p></body></html>"))
        self.warningLabel.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><br/></p></body></html>"))
        self.milesText.setText(_translate("MainWindow", "74"))
        self.milesUnitLabel.setText(_translate("MainWindow", "mi"))
        self.milesLabel.setText(_translate("MainWindow", "<html><head/><body><p>Miles range:</p></body></html>"))
import resource_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

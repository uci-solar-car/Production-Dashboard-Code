import traceback
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, pyqtSlot
from Dashboard_ui import *
from time import sleep

class Test(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # self.counter = 0
        # self.emitterTimer = QTimer()
        # self.emitterTimer.setSingleShot(False)
        # self.t = None
        # self.emitterTimer.timeout.connect(self.threadTest)
        # self.emitterTimer.start(3000)

        self.startBlink()

    def threadTest(self):
        class ThreadTest(QThread):
            signal = pyqtSignal(int)
            def __init__(self):
                QThread.__init__(self)
            def run(self):
                newVal = self.counter + 1
                self.signal.emit(newVal)

        try:
            self.t = ThreadTest()
            self.t.counter = self.counter
            self.t.signal.connect(self.updateVal)

            self.t.start()

        except:
            print(traceback.format_exc())

    def updateVal(self, newVal):
        self.counter = newVal
        print(self.counter)

    def startBlink(self):
        class StartBlink(QThread):
            def __init__(self):
                QThread.__init__(self)

            def run(self):
                while True:
                    self.leftArrowIcon.setStyleSheet("border-image: url(:/img/leftArrowOn);")
                    self.msleep(1)
                    self.rightArrowIcon.setStyleSheet("border-image: url(:/img/rightArrowOn);")
                    self.msleep(500)
                    self.leftArrowIcon.setStyleSheet("border-image: url(:/img/leftArrow);")
                    self.msleep(1)
                    self.rightArrowIcon.setStyleSheet("border-image: url(:/img/rightArrow);")
                    self.msleep(500)

        try:
            self.t = StartBlink()
            self.t.leftArrowIcon = self.leftArrowIcon
            self.t.rightArrowIcon = self.rightArrowIcon
            self.t.start()

        except:
            print(traceback.format_exc())



def main():
    try:

        app = QApplication(sys.argv)
        form = Test()
        form.show()
    except:
        print(traceback.format_exc())
    finally:
        app.exec_()

if __name__ == '__main__':
    main()
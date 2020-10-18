import struct
import traceback
import sys

import serial
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, pyqtSlot
from Dashboard_ui import *
from time import sleep

# wireless communication port initialization
serialPort = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)

class Test(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # connect shutdown button
        self.shutdownButton.pressed.connect(self.shutdown)

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
                    self.leftArrowStack.setCurrentIndex(1)
                    self.rightArrowStack.setCurrentIndex(1)
                    self.msleep(500)
                    self.leftArrowStack.setCurrentIndex(0)
                    self.rightArrowStack.setCurrentIndex(0)
                    self.msleep(500)
                    sql_str_msg = "" + str(72) + ", " + str(129) + ", " + str(66) + ", " + str(20) + ", " + str(
                        21) + ", " + str(23)
                    if serialPort.isOpen() is False:
                        serialPort.open()
                    serialPort.write(sql_str_msg.encode());

        try:
            self.t = StartBlink()
            self.t.leftArrowStack = self.leftArrowStack
            self.t.rightArrowStack = self.rightArrowStack
            self.t.start()

            # (BMS.getVoltage(), BMS.getAvgBatteryTemp(), BMS.getSOC(), BMS.getCurrent(), BMS.getAvgPackCurrent(), BMS.getHighestTemp(), BMS.getHighestTempThermistorID(), MCU.getSpeed())

        except:
            print(traceback.format_exc())

    def shutdown(self):
        """Shutdown the rpi when shutdown button is pressed. Save the log prior to shut down"""

        try:
            ##            call('sudo shutdown now', shell=True)
            app.exit()
            sys.exit()
        except:
            print(traceback.format_exc())



def main():
    global app
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
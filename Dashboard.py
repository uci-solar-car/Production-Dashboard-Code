# Changelog
# 11/26/2019 Changelog
# Updated variables related to BMS
# 10/20/2019 Changelog
# Added shutdown button and warning telltale

# 10/1/2019 Changelog
# Added initial widgets
import json
import sys
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, pyqtSlot
from Dashboard_ui import *
from subprocess import call
from collections import OrderedDict
from CAN import *

class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # initialize CAN object and start reading thread
        self.CAN = CAN_Control()

        self.startTime = datetime.now()
        self.logFilePath = '\\home\\pi\\Documents\\Logs\\{}.json'.format(self.startTime.__str__())

        self.logDict = OrderedDict()

        ### battery management system signals ###
        # visible on dashboard
        self.voltage = 0    # instantaneous voltage of the battery pack
        self.avgBatteryTemperature = 0  # average temperature of battery pack
        self.stateOfCharge = 0
        self.milesRange = 0

        # hidden
        self.current = 0            # instantaneous current of the pack
        self.avgPackCurrent = 0     # average temperature of battery pack
        self.highestTemperature = 0     # current highest temperature of the battery pack
        self.highestTemperatureThermistorID = 0     # id of thermistor with highest temperature

        ### motor controller signals ###

        ### mppt charger controller signals ###

        ### other signals ###

        self.shutdownButton.pressed.connect(self.shutdown)

        # initialize log file
        self.initLogFile()

        # append to the logDict every minute
        self.appendLogDictTimer = QTimer(self)
        self.appendLogDictTimer.setSingleShot(False)
        self.appendLogDictTimer.timeout.connect(self.appendLogDict)
        self.appendLogDictTimer.start(60000)

        # save json file every 5 minutes
        self.saveLogJsonTimer = QTimer(self)
        self.saveLogJsonTimer.setSingleShot(False)
        self.saveLogJsonTimer.timeout.connect(self.saveLogJson)
        self.saveLogJsonTimer.start(300000)

    def readThread(self):
        """Thread for reading and deciphering incoming CAN messages"""
        class ReadThread(QThread):

            def __init__(self):
                QThread.__init__(self)

            def run(self):
                while True:
                    ID, data = self.CAN.read()
                    if ID is not None and data is not None:
                        if ID == 0x001 or ID == 0x002:
                        # incoming message from BMS
                            if ID == 0x001:
                                self.BMS.decodeMessage1(data)
                            else:
                                self.BMS.decodeMessage2(data)
                            self.updateStatusBMS.emit()
                            self.batteryUpdateSignal.emit()
        try:
            self.readThread = ReadThread()
            myThread = self.readThread
            myThread.CAN = self.CAN
            myThread.BMS = self.CAN.BMS
            myThread.updateStatusBMS_Signal.connect(self.updateStatusBMS)
            myThread.batteryUpdateSignal.connect(self.batteryUpdate)

        except:
            print(traceback.format_exc())

    def updateStatusBMS(self):
        """Update variables of battery"""
        try:
            BMS = self.CAN.BMS
            self.voltage = BMS.getVoltage()
            self.avgBatteryTemperature = BMS.getAvgBatteryTemp()
            self.stateOfCharge = BMS.getSOC()
            self.milesRange = 0
            self.current = BMS.getCurrent()  # instantaneous current of the pack
            self.avgPackCurrent = BMS.getAvgPackCurrent()  # average temperature of battery pack
            self.highestTemperature = BMS.getHighestTemp()  # current highest temperature of the battery pack
            self.highestTemperatureThermistorID = BMS.getHighetTempThermistorID()  # id of therm. with highest temp
        except:
            print(traceback.format_exc())

    def batteryUpdateGUI(self):
        """Updates battery stats (percentage, voltage, miles, temperature) on GUI"""
        class BatteryUpdateGUIThread(QThread):

            def __init__(self):
                QThread.__init__(self)

            def run(self):
                # update battery variables

                # update the GUI battery status
                self.chargePercentageBar.setValue(str(self.stateOfCharge))
                self.milesText.setText(str(self.miles))
                self.voltageText.setText(str(self.voltage))
                self.batteryTemperatureText.setText(str(self.batteryTemperature))

        try:
            self.batteryUpdateGUIThread = BatteryUpdateGUIThread()
            myThread = self.batteryUpdateGUIThread
            myThread.BMS = self.CAN.BMS

            # battery data to display on Dashboard
            myThread.voltage = self.voltage
            myThread.avgBatteryTemperature = self.avgBatteryTemperature
            myThread.stateOfCharge = self.stateOfCharge
            myThread.milesRange = self.milesRange

            # GUI display widgets
            myThread.chargePercentageBar = self.chargePercentageBar
            myThread.milesText = self.milesText
            myThread.voltageText = self.voltageText
            myThread.batteryTemperatureText = self.batteryTemperatureText

            myThread.start()

        except:
            print(traceback.format_exc())

    def speedUpdate(self):
        """Updates speedometer on GUI"""
        class SpeedUpdateThread(QThread):
            def __init__(self):
                QThread.__init__(self)
            def run(self):
                if int(self.speed) != int(self.prevSpeed):
                    self.speedometer.intValue(int(self.speed))

        try:
            self.speedUpdateThread = SpeedUpdateThread()
            myThread = self.speedUpdateThread
            myThread.speed = self.speed
            myThread.prevSpeed = self.prevSpeed
            myThread.speedometer = self.speedometer
            myThread.start()
        except:
            print(traceback.format_exc())

    def leftTurnSignal(self):
        """Check to see if left blinker was activated"""

    def rightTurnSignal(self):
        """Check to see if right blinker was activated"""

    def shutdown(self):
        """Shutdown the rpi when shutdown button is pressed. Save the log prior to shut down"""
        try:
            self.appendLogDictTimer.stop()
            self.saveLogJsonTimer.stop()
            self.saveLogDict()
            self.endLogFile()
            call('sudo shutdown now', shell=True)
        except:
            print(traceback.format_exc())

    def initLogFile(self):
        """Initialize the log file and write the starting time as the file header"""
        try:
            with open(self.logFilePath, 'w') as f:
                header = 'Starting time: {}'.format(self.startTime.__str__)
                f.write(header)
                f.close()
        except:
            print(traceback.format_exc())

    def saveLogJson(self):
        """Convert the log dict into json and write into a json file. Clear the log dict after json file is updated"""
        try:
            with open(self.logFilePath, 'a') as f:
                logJson = json.dumps(self.logDict, sort_keys=True, indent=4)
                f.write(logJson)
                f.close()
            self.logDict.clear()
        except FileNotFoundError as err:
            print(str(err))
        except:
            print(traceback.format_exc())

    def endLogFile(self):
        """End the log file by marking an ending time stamp"""
        try:
            with open(self.logFilePath, 'w') as f:
                self.endTime = datetime.now()
                header = 'Ending time: {}'.format(self.endTime.__str__)
                f.write(header)
                f.close()
        except:
            print(traceback.format_exc())

    def appendLogDict(self):
        """Called every minute. Adds another entry to the logDict"""
        try:
            timestamp = datetime.now().__str__()
            self.logDict[timestamp] = {}

            # battery information
            self.logDict[timestamp]['Voltage'] = self.voltage
            self.logDict[timestamp]['AverageBatteryTemperature'] = self.avgBatteryTemperature
            self.logDict[timestamp]['StateOfCharge'] = self.stateOfCharge
            self.logDict[timestamp]['MilesRange'] = self.milesRange
            self.logDict[timestamp]['AveragePackCurrent'] = self.avgPackCurrent
            self.logDict[timestamp]['HighestBatteryTemperature'] = self.highestTemperature
            self.logDict[timestamp]['ThermistorID'] = self.highestTemperatureThermistorID

        except KeyError as err:
            print(str(err))
            pass
        except:
            print(traceback.format_exc())

def main():
    app = QApplication(sys.argv)
    form = Dashboard()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
# Changelog
# 11/29/2019 Changelog
# Added call for MCU and speed signal

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

ReadThreadPointer = None

class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.shutdownButton.pressed.connect(self.shutdown)
        
        self.startTime = datetime.now()
        self.logFilePath = '//home//pi//Documents//Logs//{}.json'.format(self.startTime.__str__())
        self.logDict = OrderedDict()

        # initialize log file
        self.initLogFile()

        # append to the logDict every minute
        self.appendLogDictTimer = QTimer()
        self.appendLogDictTimer.setSingleShot(False)
        self.appendLogDictTimer.timeout.connect(self.appendLogDict)
        self.appendLogDictTimer.start(60000)

        # save json file every 5 minutes
        self.saveLogJsonTimer = QTimer()
        self.saveLogJsonTimer.setSingleShot(False)
        self.saveLogJsonTimer.timeout.connect(self.saveLogJson)
        self.saveLogJsonTimer.start(300000)

        # update the GUI display every 250 ms
        self.updateGUI_Timer = QTimer()
        self.updateGUI_Timer.setSingleShot(False)
        self.updateGUI_Timer.timeout.connect(self.updateGUI)
        self.updateGUI_Timer.start(250)

    def readThread(self):
        """Thread for reading and deciphering incoming CAN messages"""
        class ReadThread(QThread):
            updateStatusBMS_Signal = pyqtSignal()
            batteryUpdateGUI_Signal = pyqtSignal()

            def __init__(self):
                QThread.__init__(self)

            def run(self):
                while True:
                    try:
                        ID, data = self.CAN.readMessage()
                        if ID is not None and data is not None:
                            if ID == 0x001:
                                self.BMS.decodeMessage1(data)
                            elif ID == 0x002:
                                self.BMS.decodeMessage2(data)
                            elif ID == 0x003:
                                self.MCU.decodeMessage(data)
                    except:
                        print(traceback.format_exc())
        try:
            global ReadThreadPointer
            ReadThreadPointer = ReadThread()
            ReadThreadPointer.CAN = self.CAN
            ReadThreadPointer.BMS = self.CAN.BMS
            ReadThreadPointer.MCU = self.CAN.MCU
            ReadThreadPointer.start()
        except:
            print(traceback.format_exc())

    def updateGUI(self):
        """Updates the GUI display every 250 ms"""
        class UpdateGUI(QThread):

            def __init__(self):
                QThread.__init__(self)

            def run(self):
                try:
                    ##### update signal variables #####
                    # BMS
                    BMS = self.BMS
                    voltage = BMS.getVoltage()
                    stateOfCharge = BMS.getSOC()
                    avgBatteryTemperature = BMS.getAvgBatteryTemp()

                    # MCU
                    MCU = self.MCU
                    speed = MCU.getSpeed()

                    ###### update GUI display based on new signal variables #####
                    # BMS
                    self.chargePercentageBar.setValue(int(stateOfCharge))
                    self.milesText.setText('{} mi'.format(0))
                    self.voltageText.setText('{} V'.format(voltage))
                    self.batteryTemperatureText.setText('{} C'.format(avgBatteryTemperature))

                    # MCU
                    self.speedometer.display(speed)

                except:
                    print(traceback.format_exc())
            
                
        try:

            updateGUI_Thread = UpdateGUI()
            updateGUI_Thread.BMS = self.CAN.BMS
            updateGUI_Thread.MCU = self.CAN.MCU

            # GUI widgets
            updateGUI_Thread.chargePercentageBar = self.chargePercentageBar
            updateGUI_Thread.milesText = self.milesText
            updateGUI_Thread.voltageText = self.voltageText
            updateGUI_Thread.batteryTemperatureText = self.batteryTemperatureText
            updateGUI_Thread.speedometer = self.speedometer

            updateGUI_Thread.start()
        except:
            print(traceback.format_exc())

    def shutdown(self):
        """Shutdown the rpi when shutdown button is pressed. Save the log prior to shut down"""
        try:
            self.appendLogDictTimer.stop()
            self.saveLogJsonTimer.stop()
            self.appendLogDict()
            self.saveLogJson()
            self.endLogFile()
            
##            call('sudo shutdown now', shell=True)
            exit()
        except:
            print(traceback.format_exc())

    def initLogFile(self):
        """Initialize the log file and write the starting time as the file header"""
        try:
            with open(self.logFilePath, 'w') as f:
                header = 'Starting time: {}\n'.format(self.startTime.__str__())
                f.write(header)
                f.close()
        except:
            print(traceback.format_exc())

    def saveLogJson(self):
        """Convert the log dict into json and write into a json file. Clear the log dict after json file is updated"""
        class SaveLogJson(QThread):
            def __init__(self):
                QThread.__init__(self)
            def run(self):
                try:
                    with open(self.logFilePath, 'a') as f:
                        logJson = json.dumps(self.logDict, sort_keys=True, indent=4)
                        f.write(logJson)
                        f.close()
                    self.logDict.clear()
                except FileNotFoundError as err:
                    print(traceback.format_exc())
                except:
                    print(traceback.format_exc())

        try:
            myThread = SaveLogJson()
            myThread.logFilePath = self.logFilePath
            myThread.logDict = self.logDict
            myThread.start()
            """
            with open(self.logFilePath, 'a') as f:
                logJson = json.dumps(self.logDict, sort_keys=True, indent=4)
                f.write(logJson)
                f.close()
            self.logDict.clear()
        except FileNotFoundError as err:
            print(str(err))
            """
        except:
            print(traceback.format_exc())

    def endLogFile(self):
        """End the log file by marking an ending time stamp"""
        try:
            with open(self.logFilePath, 'a') as f:
                self.endTime = datetime.now()
                header = '\nEnding time: {}'.format(self.endTime.__str__())
                f.write(header)
                f.close()
        except:
            print(traceback.format_exc())

    def appendLogDict(self):
        """Called every minute. Adds another entry to the logDict"""
        class AppendLogDict(QThread):

            def __init__(self):
                QThread.__init__(self)

            def run(self):
                try:
                    self.logDict[self.timestamp] = {}
                    self.logDict[self.timestamp]['Voltage'] = BMS.getVoltage()
                    self.logDict[self.timestamp]['AverageBatteryTemperature'] = BMS.getAvgBatteryTemp()
                    self.logDict[self.timestamp]['StateOfCharge'] = BMS.getSOC()
                    self.logDict[self.timestamp]['MilesRange'] = 0
                    self.logDict[self.timestamp]['Current'] = BMS.getCurrent()
                    self.logDict[self.timestamp]['AveragePackCurrent'] = BMS.getAvgPackCurrent()
                    self.logDict[self.timestamp]['HighestBatteryTemperature'] = BMS.getHighestTemp()
                    self.logDict[self.timestamp]['ThermistorID'] = BMS.getHighetTempThermistorID()
                    self.logDict[self.timestamp]['Speed'] = MCU.getSpeed()
                except KeyError as err:
                    print(str(err))
                except:
                    print(traceback.format_exc())

        try:
            myThread = AppendLogDict()
            myThread.BMS = self.CAN.BMS
            myThread.MCU = self.CAN.MCU
            myThread.timestamp = datetime.now().__str__()
            myThread.logDict = self.logDict
            myThread.start()

            """
            BMS = self.CAN.BMS
            timestamp = datetime.now().__str__()
            self.logDict[timestamp] = {}

            # battery information
            self.logDict[timestamp]['Voltage'] = BMS.getVoltage()
            self.logDict[timestamp]['AverageBatteryTemperature'] = BMS.getAvgBatteryTemp()
            self.logDict[timestamp]['StateOfCharge'] = BMS.getSOC()
            self.logDict[timestamp]['MilesRange'] = 0
            self.logDict[timestamp]['Current'] = BMS.getCurrent()
            self.logDict[timestamp]['AveragePackCurrent'] = BMS.getAvgPackCurrent()
            self.logDict[timestamp]['HighestBatteryTemperature'] = BMS.getHighestTemp() 
            self.logDict[timestamp]['ThermistorID'] = BMS.getHighetTempThermistorID()
            
        except KeyError as err:
            print(str(err))
            pass
            """
        except:
            print(traceback.format_exc())

def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("fusion")
        form = Dashboard()
        form.show()

        # create object for CAN_Control and start reading from CAN-bus
        form.CAN = CAN_Control()
        form.readThread()

    except:
        print(traceback.format_exc())
    finally:
        app.exec_()

if __name__ == '__main__':
    main()

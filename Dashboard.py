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


class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # initialize CAN_Control, BMS, MCU 
        self.CAN = CAN_Control()
        self.BMS = self.CAN.BMS
        self.MCU = self.CAN.MCU

        # connect shutdown button
        self.shutdownButton.pressed.connect(self.shutdown)
        
        self.startTime = datetime.now()
        self.logFilePath = '//home//pi//Documents//Logs//{}.json'.format(self.startTime.__str__())
        self.logDict = OrderedDict()

        # start read thread
        self.readThread = None
        self.startReadThread()

        # initialize log file
        self.initLogFile()

        # append to the logDict every minute
        self.appendLogDictThread = None
        self.appendLogDictTimer = QTimer()
        self.appendLogDictTimer.setSingleShot(False)
        self.appendLogDictTimer.timeout.connect(self.appendLogDict)
        self.appendLogDictTimer.start(60000)

        # save json file every 5 minutes
        self.saveLogJsonThread = None
        self.saveLogJsonTimer = QTimer()
        self.saveLogJsonTimer.setSingleShot(False)
        self.saveLogJsonTimer.timeout.connect(self.saveLogJson)
        self.saveLogJsonTimer.start(300000)

        # update the GUI display every 250 ms
        self.updateGUI_Thread = None
        self.updateGUI_Timer = QTimer()
        self.updateGUI_Timer.setSingleShot(False)
        self.updateGUI_Timer.timeout.connect(self.updateGUI)
        self.updateGUI_Timer.start(250)

    def startReadThread(self):
        """Thread for reading and deciphering incoming CAN messages"""
        class ReadThread(QThread):
            
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
            self.readThread = ReadThread()
            self.readThread.CAN = self.CAN
            self.readThread.BMS = self.BMS
            self.readThread.MCU = self.MCU
            self.readThread.start()
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
                    self.milesText.setText(str(0))
                    self.voltageText.setText(str(voltage))
                    self.batteryTemperatureText.setText(str(avgBatteryTemperature))

                    # MCU
                    self.speedometer.display(speed)

                except:
                    print(traceback.format_exc())
            
                
        try:
            self.updateGUI_Thread = UpdateGUI()
            self.updateGUI_Thread.BMS = self.BMS
            self.updateGUI_Thread.MCU = self.MCU

            # GUI widgets
            self.updateGUI_Thread.chargePercentageBar = self.chargePercentageBar
            self.updateGUI_Thread.milesText = self.milesText
            self.updateGUI_Thread.voltageText = self.voltageText
            self.updateGUI_Thread.batteryTemperatureText = self.batteryTemperatureText
            self.updateGUI_Thread.speedometer = self.speedometer

            self.updateGUI_Thread.start()
        except:
            print(traceback.format_exc())

    def shutdown(self):
        """Shutdown the rpi when shutdown button is pressed. Save the log prior to shut down"""
        try:
            self.appendLogDictTimer.stop()
            self.saveLogJsonTimer.stop()
            self.appendLogDict()
            self.appendLogDictThread.wait()
            self.saveLogJson()
            self.saveLogJsonThread.wait()
            self.endLogFile()
            self.readThread.terminate()
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
            self.saveLogJsonThread = SaveLogJson()
            self.saveLogJsonThread.logFilePath = self.logFilePath
            self.saveLogJsonThread.logDict = self.logDict
            self.saveLogJsonThread.start()
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
                    BMS = self.BMS
                    MCU = self.MCU
                    logDict = self.logDict
                    t = self.timestamp
                    logDict[t] = {}
                    logDict[t]['Voltage'] = '{} V'.format(BMS.getVoltage())
                    logDict[t]['AverageBatteryTemperature'] = '{} F'.format(BMS.getAvgBatteryTemp())
                    logDict[t]['StateOfCharge'] = '{} %'.format(BMS.getSOC())
                    logDict[t]['MilesRange'] = '{} mi'.format(0)
                    logDict[t]['Current'] = '{} A'.format(BMS.getCurrent())
                    logDict[t]['AveragePackCurrent'] = '{} A'.format(BMS.getAvgPackCurrent())
                    logDict[t]['HighestBatteryTemperature'] = '{} F'.format(BMS.getHighestTemp())
                    logDict[t]['ThermistorID'] = BMS.getHighetTempThermistorID()
                    logDict[t]['Speed'] = '{} mph'.format(MCU.getSpeed())
                except KeyError as err:
                    print(str(err))
                except:
                    print(traceback.format_exc())

        try:
            self.appendLogDictThread  = AppendLogDict()
            self.appendLogDictThread.BMS = self.BMS
            self.appendLogDictThread.MCU = self.MCU
            self.appendLogDictThread.timestamp = datetime.now().__str__()
            self.appendLogDictThread.logDict = self.logDict
            self.appendLogDictThread.start()

        except:
            print(traceback.format_exc())

def main():
    try:
        app = QApplication(sys.argv)
        form = Dashboard()
        form.show()
    except:
        print(traceback.format_exc())
    finally:
        app.exec_()

if __name__ == '__main__':
    main()

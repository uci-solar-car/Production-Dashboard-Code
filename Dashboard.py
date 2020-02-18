# Changelog
# 12/6/2019 Changlelog
# Added call for left, right, and hazard blinkers

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

"""
    Uncomment 'from CAN import *' and comment out 'from CAN_final import *' when testing with fake ECUs.
    Comment our 'from CAN import *' and uncomment 'from CAN_final import *' when testing with real ECUs. 
"""
##from CAN import *
from CAN_final import *

class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # initialize CAN_Control, BMS, MCU 
        self.CAN = CAN_Control()
        self.BMS = self.CAN.BMS
        self.MCU = self.CAN.MCU
        self.Lights = self.CAN.Lights

        # connect shutdown button
        self.shutdownButton.pressed.connect(self.shutdown)

        dt = datetime.now()
        self.startTime = dt.strftime('%d_%m_%Y_%H_%M')
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

        # update texts/labels on GUI display every 200 ms
        self.updateTextsGUI_Thread = None
        self.updateTextsGUI_Timer = QTimer()
        self.updateTextsGUI_Timer.setSingleShot(False)
        self.updateTextsGUI_Timer.timeout.connect(self.updateTextsGUI)
        self.updateTextsGUI_Timer.start(200)

        # update non-flashing images on GUI display every 500 ms
        self.prevStateHazards = 0
        self.prevStateWarning = 0
        self.prevStateCruiseControl = 0
        self.prevStateHeadlights = 0
##        self.warningChangedSignal = pyqtSignal()
##        self.hazardsChangedSignal = pyqtSignal()
##        self.cruiseControlChangedSignal = pyqtSignal()
##        self.headlightsChangedSignal = pyqtSignal()
##        self.warningChangedSignal.connect(self.warningChanged)
##        self.hazardsChangedSignal.connect(self.hazardsChanged)
##        self.cruiseControlChangedSignal.connect(self.hazardsChanged)
##        self.headlightsChangedSignal.connect(self.headlightsChanged)
        self.updateIconsGUI_Thread = None
        self.updateIconsGUI_Timer = QTimer()
        self.updateIconsGUI_Timer.setSingleShot(False)
        self.updateIconsGUI_Timer.timeout.connect(self.updateIconsGUI)
        self.updateIconsGUI_Timer.start(500)

        # update flashing turn signals images on GUI display
        self.updateTurnLightsGUI_Thread = None
        self.updateTurnLightsGUI()

    def startReadThread(self):
        """Thread for reading and deciphering incoming CAN messages."""
        class ReadThread(QThread):
            def __init__(self):
                QThread.__init__(self)

            def run(self):
                while True:
                    try:
                        ID, data = self.CAN.readMessage()
                        # if there is a CAN message, pass it to the correct ECU to be decoded
                        if ID is not None and data is not None:
                            if ID == 0x001:
                                self.BMS.decodeMessage1(data)
                            elif ID == 0x002:
                                self.BMS.decodeMessage2(data)
                            elif ID == 0x003:
                                self.MCU.decodeMessage(data)
                            elif ID == 0x004:
                                self.Lights.decodeMessage(data)
                                    
                    except:
                        print(traceback.format_exc())
                        
        try:
            self.readThread = ReadThread()
            self.readThread.CAN = self.CAN
            self.readThread.BMS = self.BMS
            self.readThread.MCU = self.MCU
            self.readThread.Lights = self.Lights
            self.readThread.start()
        except:
            print(traceback.format_exc())

    def updateTextsGUI(self):
        """Updates texts on GUI display every 250 ms.
            Texts include state of charge, gear position, speed, miles range."""
        class UpdateTextsGUI(QThread):

            def __init__(self):
                QThread.__init__(self)

            def run(self):
                try:
                    ##### get new signal variables #####
                    # BMS
                    BMS = self.BMS
                    stateOfCharge = BMS.getSOC()

                    # MCU
                    MCU = self.MCU
                    speed = MCU.getSpeed()
                    gearPosition = MCU.getGearPosition()

                    ###### update texts/numbers on GUI display based on new signal variables #####
                    # BMS
                    self.chargePercentageBar.setValue(int(stateOfCharge))
                    self.milesText.setText(str(0))

                    # MCU
                    self.speedometer.display(int(speed))
                    self.gearPositionLabel.setText(str(gearPosition))
                except:
                    print(traceback.format_exc())

        try:
            # ECUs to pass to the QThread
            self.updateTextsGUI_Thread = UpdateTextsGUI()
            self.updateTextsGUI_Thread.BMS = self.BMS
            self.updateTextsGUI_Thread.MCU = self.MCU

            # GUI widgets to pass to the QThread
            self.updateTextsGUI_Thread.chargePercentageBar = self.chargePercentageBar
            self.updateTextsGUI_Thread.milesText = self.milesText
            self.updateTextsGUI_Thread.speedometer = self.speedometer
            self.updateTextsGUI_Thread.gearPositionLabel = self.gearPositionLabel

            # run thread
            self.updateTextsGUI_Thread.start()
        except:
            print(traceback.format_exc())

    def updateTurnLightsGUI(self):
        """Updates turn indicators on the GUI display"""
        class UpdateTurnLightsGUI(QThread):
            def __init__(self):
                QThread.__init__(self)
            def run(self):
                try:
                    Lights = self.Lights
                    leftArrowStack = self.leftArrowStack
                    rightArrowStack = self.rightArrowStack
                    while True:
                        hazards = Lights.getHazards()
                        # flash both turn signals if hazards are on.
                        if hazards == 1:
                            leftArrowStack.setCurrentIndex(1)
                            rightArrowStack.setCurrentIndex(1)
                            self.msleep(500)
                            leftArrowStack.setCurrentIndex(0)
                            rightArrowStack.setCurrentIndex(0)
                            self.msleep(500)
                            # self.leftArrowIcon.setStyleSheet("border-image: url(:/img/leftArrowOn);")
                            # self.msleep(1)
                            # self.rightArrowIcon.setStyleSheet("border-image: url(:/img/rightArrowOn);")
                            # self.msleep(500)
                            # self.leftArrowIcon.setStyleSheet("border-image: url(:/img/leftArrow);")
                            # self.msleep(1)
                            # self.rightArrowIcon.setStyleSheet("border-image: url(:/img/rightArrow);")
                            # self.msleep(500)

                        else:
                            leftTurn = Lights.getLeftTurnIndicator()
                            rightTurn = Lights.getRightTurnIndicator()
                            # flash left signal if activated
                            if leftTurn == 1 and rightTurn == 0:
                                leftArrowStack.setCurrentIndex(1)
                                self.msleep(500)
                                leftArrowStack.setCurrentIndex(0)
                                self.msleep(500)
                                # self.leftArrowIcon.setStyleSheet("border-image: url(:/img/leftArrowOn);")
                                # self.msleep(500)
                                # self.leftArrowIcon.setStyleSheet("border-image: url(:/img/leftArrow);")
                                # self.msleep(500)
                            # flash right signal if activated.
                            elif rightTurn == 1 and leftTurn == 0:
                                rightArrowStack.setCurrentIndex(1)
                                self.msleep(500)
                                rightArrowStack.setCurrentIndex(0)
                                self.msleep(500)
                                # self.rightArrowIcon.setStyleSheet("border-image: url(:/img/rightArrowOn);")
                                # self.msleep(500)
                                # self.rightArrowIcon.setStyleSheet("border-image: url(:/img/rightArrow);")
                                # self.msleep(500)

                except:
                    print(traceback.format_exc())

        try:
            # ECUs to pass to the QThread
            self.updateTurnLightsGUI_Thread = UpdateTurnLightsGUI()
            self.updateTurnLightsGUI_Thread.Lights = self.Lights

            # GUI widgets to pass to the QThread
            self.updateTurnLightsGUI_Thread.hazardsIcon = self.hazardsIcon
            self.updateTurnLightsGUI_Thread.leftArrowStack = self.leftArrowStack
            self.updateTurnLightsGUI_Thread.rightArrowStack = self.rightArrowStack

            # run thread
            self.updateTurnLightsGUI_Thread.start()
        except:
            print(traceback.format_exc())

    def updateIconsGUI(self):
        """ Updates indicator icons on the GUI display. Icons include warning, hazard, headlights, cruise control. """
        class UpdateIconsGUI(QThread):
            # initialize signals
            warningChangedSignal = pyqtSignal(int)
            hazardsChangedSignal = pyqtSignal(int)
            headlightsChangedSignal = pyqtSignal(int)
            cruiseControlChangedSignal = pyqtSignal(int)

            def __init__(self):
                QThread.__init__(self)
            def run(self):
                try:
                    # new MCU signal variables
                    MCU = self.MCU
                    currStateCruiseControl = MCU.getCruiseControl()

                    # new Lights signal variables
                    Lights = self.Lights
                    currStateHazards = Lights.getHazards()
                    currStateHeadlights = Lights.getHeadlights()
                    currStateWarning = Lights.getWarning()

                    # compare previous signal values with new signal values to see if GUI icon needs to change
                    # if signal values are new, update GUI image and call slot functions
                    if self.prevStateHazards != currStateHazards:
                        if currStateHazards == 1:
                            self.hazardsIcon.show()
                            #self.hazardsIcon.setStyleSheet("background-image: url(:/img/hazards);")
                        else:
                            self.hazardsIcon.hide()
                            #self.hazardsIcon.setStyleSheet("")
                        self.hazardsChangedSignal.emit(currStateHazards)

                    if self.prevStateCruiseControl != currStateCruiseControl:
                        if currStateCruiseControl == 1:
                            self.cruiseControlIcon.show()
                            #self.cruiseControlIcon.setStyleSheet("background-image: url(:/img/cruiseControl);")
                        else:
                            self.cruiseControlIcon.hide()
                            #self.cruiseControlIcon.setStyleSheet("")
                        self.cruiseControlChangedSignal.emit(currStateCruiseControl)

                    if self.prevStateHeadlights != currStateHeadlights:
                        if currStateHeadlights == 1:
                            self.headlightsIcon.show()
                            #self.headlightsIcon.setStyleSheet("background-image: url(:/img/lowbeams);")
                        else:
                            self.headlightsIcon.hide()
                            #self.headlightsIcon.setStyleSheet("")
                        self.headlightsChangedSignal.emit(currStateHeadlights)

                    if self.prevStateWarning != currStateWarning:
                        if currStateWarning == 1:
                            self.warningIcon.show()
                            #self.warningIcon.setStyleSheet("background-image: url(:/img/warningYellow);")
                        else:
                            self.warningIcon.hide()
                            #self.warningIcon.setStyleSheet("")
                        self.warningChangedSignal.emit(currStateWarning)

                except:
                    print(traceback.format_exc())

        try:
            # ECUs to pass to the QThread
            self.updateIconsGUI_Thread = UpdateIconsGUI()
            self.updateIconsGUI_Thread.MCU = self.MCU
            self.updateIconsGUI_Thread.Lights = self.Lights

            # GUI widgets to pass to the QThread
            self.updateIconsGUI_Thread.warningIcon = self.warningIcon
            self.updateIconsGUI_Thread.cruiseControlIcon = self.cruiseControlIcon
            self.updateIconsGUI_Thread.hazardsIcon = self.hazardsIcon
            self.updateIconsGUI_Thread.headlightsIcon = self.headlightsIcon

            # previous state to pass to the QThread for comparison
            self.updateIconsGUI_Thread.prevStateWarning = self.prevStateWarning
            self.updateIconsGUI_Thread.prevStateHazards = self.prevStateHazards
            self.updateIconsGUI_Thread.prevStateCruiseControl = self.prevStateCruiseControl
            self.updateIconsGUI_Thread.prevStateHeadlights = self.prevStateHeadlights

            # connect signals and slots to pass QThread
            self.updateIconsGUI_Thread.warningChangedSignal.connect(self.warningChanged)
            self.updateIconsGUI_Thread.hazardsChangedSignal.connect(self.hazardsChanged)
            self.updateIconsGUI_Thread.headlightsChangedSignal.connect(self.headlightsChanged)
            self.updateIconsGUI_Thread.cruiseControlChangedSignal.connect(self.cruiseControlChanged)

            # run thread
            self.updateIconsGUI_Thread.start()
        except:
            print(traceback.format_exc())

    def warningChanged(self, newValue):
        """Update prevState of warning."""
        try:
            self.prevStateWarning = newValue
        except:
            print(traceback.format_exc())

    def hazardsChanged(self, newValue):
        """Update prevState of hazards."""
        try:
            self.prevStateHazards = newValue
        except:
            print(traceback.format_exc())

    def headlightsChanged(self, newValue):
        """Update prevState of headlights."""
        try:
            self.prevStateHeadlights = newValue
        except:
            print(traceback.format_exc())

    def cruiseControlChanged(self, newValue):
        """ Update prevState of cruise control."""
        try:
            self.prevStateCruiseControl = newValue
        except:
            print(traceback.format_exc())

    def resetGUIIcons(self):
        """ Set GUI icons to original states. """
        self.leftArrowStack.setCurrentIndex(0)
        self.rightArrowStack.setCurrentIndex(0)
        self.hazardsIcon.hide()
        self.cruiseControlIcon.hide()
        self.headlightsIcon.hide()
        self.warningIcon.hide()

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
            self.readThread.exit()
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
                dt = datetime.now()
                self.endTime = dt.strftime('%d_%m_%Y_%H_%M')
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
                    Lights = self.Lights
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
                    logDict[t]['GearPosition'] = MCU.getGearPosition()
                    logDict[t]['CruiseControl'] = MCU.getCruiseControl()
                    logDict[t]['LeftTurn'] = Lights.getLeftTurnIndicator()
                    logDict[t]['RightTurn'] = Lights.getRightTurnIndicator()
                    logDict[t]['Hazards'] = Lights.getHazards()
                    logDict[t]['Headlights'] = Lights.getHeadlights()
                except KeyError as err:
                    print(str(err))
                except:
                    print(traceback.format_exc())

        try:
            self.appendLogDictThread = AppendLogDict()
            self.appendLogDictThread.BMS = self.BMS
            self.appendLogDictThread.MCU = self.MCU
            self.appendLogDictThread.Lights = self.Lights
            self.appendLogDictThread.timestamp = datetime.now().__str__()
            self.appendLogDictThread.logDict = self.logDict
            self.appendLogDictThread.start()

        except:
            print(traceback.format_exc())

def main():
    try:
        app = QApplication(sys.argv)
        form = Dashboard()
        form.showFullScreen()
    except:
        print(traceback.format_exc())
    finally:
        app.exec_()

if __name__ == '__main__':
    main()

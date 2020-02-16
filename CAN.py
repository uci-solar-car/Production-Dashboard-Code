# 12/6/2019 Changelog
# Added class for Blinkers

# 11/29/2019 Changelog
# Added class for MCU and speed

# 11/28/2019 Changelog
# Added decoding of message for BMS statuses

""" To be used when testing with fake ECU. """
import can
import can.interfaces
import subprocess
import traceback
from can.interface import Bus
from can import Message
from subprocess import call

class CAN_Control():
    def __init__(self):
        self.bus = None
        self.bufferedReader = None
        self.notifier = None
        self.BMS = self.BMS_Control()
        self.MCU = self.MCU_Control()
        self.Blinkers = self.Blinkers_Control()
        self.initCAN()

    def initCAN(self):
        """Initialize the profile for the CAN controller."""
        try:
            # send out command to set up can0 from the shell to interface CAN controller hardware
            call('sudo ip link set can0 up type can bitrate 500000', shell=True)

            # initialize Bus object
            self.bus = Bus(channel='can0', bustype='socketcan_native')

            # initialize message buffer to store incoming CAN messages
            self.bufferedReader = can.BufferedReader()

            # notifier will notify when new message arrives on the bus and places it in the buffer 
            self.notifier = can.Notifier(self.bus, [self.bufferedReader])
        except:
            print(traceback.print_exc())
    
    def readMessage(self, timeout = 0.1):
        """Grabs a message from the buffered reader and returns the arbitration ID and data fields"""
        try:
            arbitrationID = None
            data = None
            msg = self.bufferedReader.get_message(timeout = timeout)
            if msg is not None:
                # arbitration id is the priority number of the CAN message. the lower the id, the higher the priority
                arbitrationID = msg.arbitration_id

                # data is a list of bytes. data[0] is byte 1 ..... all the way to data[7] is byte 8
                data = msg.data
            return arbitrationID, data
            
        except:
            print(traceback.print_exc())

    def sendMessage(self, msg, timeout = 0.1):
        """Sends a CAN message on the bus."""
        try:
            self.bus.send(msg, timeout = timeout)
        except:
            print(traceback.print_exc())

    class BMS_Control():
        def __init__(self):
            # BMS CAN message1
            self.msg1ID = 0x001
            self.failsafeStat = 0
            self.voltage = 0  # instantaneous voltage of battery pack
            self.current = 0  # instantaneous current battery pack
            self.highestTemperature = 0  # current highest temperature of pack
            self.highestTemperatureThermistorID = 0  # id of thermistor with highest temperature

            # BMS CAN message2
            self.msg2ID = 0x002
            self.avgPackCurrent = 0  # average temperature of pack
            self.avgBatteryTemperature = 0  # average temperature of pack
            self.stateOfCharge = 0      # state of charge

            # others
            self.milesRange = 0

        def getVoltage(self):
            return self.voltage

        def getCurrent(self):
            return self.current

        def getHighestTemp(self):
            return self.highestTemperature

        def getHighetTempThermistorID(self):
            return self.highestTemperatureThermistorID

        def getSOC(self):
            return self.stateOfCharge

        def getAvgBatteryTemp(self):
            return self.avgBatteryTemperature

        def getAvgPackCurrent(self):
            return self.avgPackCurrent

        def decodeMessage1(self, data):
            """Decode CAN message from BMS with ID# 0x001. Message includes Failsafe Statuses, Inst. Pack Voltage,
                Inst. Pack Current, Highest Temperature, Thermistor ID with Highest Temperature"""
            try:
                # failsafe statuses
                self.failsafeStat = (data[1] | data [0])
                self.voltageFailsafeActive = self.failsafeStat & 0x1
                self.currentFailsafeActive = (self.failsafeStat >> 1) & 0x1
                self.relayFailsafeActive = (self.failsafeStat >> 2) & 0x1
                self.cellBalancingActive = (self.failsafeStat >> 3) & 0x1
                self.chargeInterlockFailsafeActive = (self.failsafeStat >> 4) & 0x1
                self.thermistorBValueTableInvalid = (self.failsafeStat >> 5) & 0x1
                self.inputPowerSupplyFailsafeActive = (self.failsafeStat >> 6) & 0x1

                # pack instantaneous voltage
                self.voltage = (data[3] | data[2])

                # pack instantaneous current
                self.current = (data[5] | data[4])
                
                # highest temperature
                self.highestTemperature = data[6]

                # id of thermistor with highest temperature
                self.highestTemperatureThermistorID = data[7]
                
            except:
                print(traceback.format_exc())

        def decodeMessage2(self, data):
            """Decode CAN message from BMS with ID# 0x002. Message includes State of Charge, Average Temperature,
                Average Pack Current. """
            try:
                # state of charge
                self.stateOfCharge = (data[1] | data[0])

                # average battery temperature
                self.avgBatteryTemperature = (data[3] | data[2])

                # average pack current
                self.avgPackCurrent = (data[5] | data[4])
                
            except:
                print(traceback.format_exc())

    class MCU_Control():
        def __init__(self):
            self.msgID = 0x003
            self.speed = 0           #speed in mph
            self.gearPosition = 0    # 0 = Park, 1 = Reverse, 2 = Neutral, 3 = Drive
            self.cruiseControl = 0   # 0 = Cruise Control On, 1 = Cruise Control Off
            self.brake = 0           # 0 = Brake is not pressed, 1 = Brake is pressed

        def getSpeed(self):
            return self.speed

        def getGearPosition(self):
            if self.gearPosition == 0:
                return 'P'
            elif self.gearPosition == 1:
                return 'R'
            elif self.gearPosition == 2:
                return 'N'
            elif self.gearPosition == 3:
                return 'D'

        def getCruiseControl(self):
            return self.cruiseControl

        def getBrake(self):
            return self.brake

        def decodeMessage(self, data):
            """Decode CAN message from MCU. Message includes Speed, gearPosition, cruiseControl"""
            try:
                # speed
                self.speed = data[0]

                # gear position
                self.gearPosition = data[1] & 11

                # cruise control status
                self.gearPosition = (data[1] >> 2) & 1

                # brake status
                self.brake = (data[1] >> 3) & 1

            except:
                print(traceback.format_exc())

    class Lights_Control():
        def __init__(self):
            self.msgID = 0x004
            self.rightTurn = 0     # 0 = off, 1 = right turn on
            self.leftTurn = 0      # 0 = off, 1 = left turn on
            self.hazards = 0       # 0 = off, 1 = hazards on
            self.headlights = 0    # 0 = off, 1 = lowbeams
            self.warning = 0       # 0 = off, 1 = warning on

        def getRightTurnIndicator(self):
            return self.rightTurn

        def getLeftTurnIndicator(self):
            return self.leftTurn

        def getHazards(self):
            return self.hazards

        def getHeadlights(self):
            return self.headlights

        def getWarning(self):
            return self.warning

        def decodeMessage(self, data):
            """Decode CAN message from blinker. Message includes status of hazards, right, and left blinker"""
            try:
                # hazard
                self.hazards = data[0] & 0x1

                # right turn indicator
                self.rightTurn = (data[0] >> 1) & 0x1

                # left turn indicator
                self.leftTurn = (data[0] >> 2) & 0x1

                # headlights
                self.headlights = (data[0] >> 3) & 0x1

                # warning
                self.headlights = (data[0] >> 4) & 0x1
            except:
                print(traceback.format_exc())

##if __name__ == '__main__':
##    CAN = CAN_Control()
##    while True:
##        CAN.readMessage()

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
        self.initCAN()

    def initCAN(self):
        try:
            # send out command to set up can0 from the shell to interface CAN controller hardware
            call('sudo /sbin/ip link set can0 up type can bitrate 500000', shell=True)

            # initialize Bus object
            self.bus = Bus()

            # initialize message buffer to store incoming CAN messages
            self.bufferedReader = can.BufferedReader()

            # notifier will notify when new message arrives on the bus and places it in the buffer 
            self.notifier = can.Notifier(self.bus, [self.bufferedReader])
        except:
            print(traceback.print_exc())

    def readMessage(self, timeout = 0.1):
        """grabs a message from the buffered reader and returns the arbitration ID and data fields"""
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
        """sends a CAN message on the bus"""
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
            """Decode CAN message with ID# 0x001. Message includes Failsafe Statuses, Inst. Pack Voltage,
                Inst. Pack Current, Highest Temperature, Thermistor ID with Highest Temperature"""
            try:
                self.failsafeStat = data & 0xFFFF
                self.voltage = (data >> 16) & 0xFFFF
                self.current = (data >>32) & 0xFFFF
                self.highestTemperature = (data >> 48) & 0xFF
                self.highestTemperatureThermistorID = (data >> 56) & 0xFF
            except:
                print(traceback.format_exc())

        def decodeMessage2(self, data):
            """Decode CAN message with ID# 0x002. Message includes State of Charge, Average Temperature, Average Pack
                Current. """
            try:
                self.stateOfCharge = data & 0xFFFF
                self.avgBatteryTemperature = (data >> 16) & 0xFFFF
                self.avgPackCurrent = (data >> 32) & 0xFFFF
            except:
                print(traceback.format_exc())

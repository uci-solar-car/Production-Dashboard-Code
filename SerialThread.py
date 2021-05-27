# Thread for sending serial messages
# still only sends random messages

import threading

import serial
from random import seed
from random import random
import time

class SerialThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
      
        self.serial_port = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)
        
        seed(1)
        self.msg_log = {}
   
    def generateChecksum(self, msg): # string data
        return 1


    def validateMessage(self, msg, checksum):
        return checksum == self.generateChecksum(msg);

    # takes the list of ids that were successfully received/uploaded
    # to the server, and deletes them from the list of messages that
    # need sending
    def updateReceivedIds(self, msg):
        ids = msg.split(",")
        print("ids: " + str(ids))
        print("msg_log: " + str(self.msg_log))
        for i in ids: # note: in string form
            if (i != ""):
                self.msg_log.pop(int(i))
        

    # checks for messages in the serialport, and
    # parses through received data
    def receiveMessages(self):
        receivedMsgs = []
        
        while (self.serial_port.in_waiting > 0):
            serial_msg = self.serial_port.readline().decode('Ascii')
            receivedMsgs.append(serial_msg)
            
        while bool(receivedMsgs):
            msg = receivedMsgs[0].split(";")
            
            if len(msg) != 3:
                print("msg either incomplete or formatted incorrectly: " + msg);
            
            # check for corruption
            if (self.validateMessage(msg[0] + msg[1], int(msg[2]))):
                print("msg successfully received: " + receivedMsgs[0])
                self.updateReceivedIds(msg[1])
            else:
                print("Invalid Checksum: " + receivedMsgs[0])
            
            receivedMsgs.pop(0)

    def resendMessages(self):
    	for msg in self.msg_log:
    		self.serial_port.write(self.msg_log[msg].encode())
    		write("msg " + str(msg) + " resent: " + self.msg_log[msg])
    			
            
    def generateRandomNumberMsg(self, msg_id, n):
        msg = str(msg_id) + ";"    
        while (n > 2):
            msg += str(int(random() * 100)) + ","
            n -= 1
        msg += str(44) + ","# driveNum = 44
        msg += str(int(random() * 100))
        msg += ";" + str(self.generateChecksum(msg))
        return msg
    
    # send random list of numbers to sql server and ensure correct data is received
    def testMsgValidation(self):
        nnums = 5
        msg_id = 60 # keeps track of msg ids
        while True:
            msg_to_send = self.generateRandomNumberMsg(msg_id, nnums)
            self.msg_log[msg_id] = msg_to_send
            self.serial_port.write(msg_to_send.encode())
            print("\nmessage sent: " + msg_to_send)
            
            msg_id += 1
            time.sleep(5)
            
            self.receiveMessages()
   
    def run(self):
        if(self.serial_port.isOpen() is False):
            self.serial_port.open()
        self.testMsgValidation()
          

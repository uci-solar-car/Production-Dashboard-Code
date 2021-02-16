#!/usr/bin/python

import serial
from random import seed
from random import random
import time
#from xbee import XBee

serial_port = serial.Serial(port="/dev/ttyUSB0",
                            baudrate=9600)

seed(1)
msg_log = {}

def generateChecksum(msg): # string data
    return 1


def validateMessage(msg, checksum):
    return checksum == generateChecksum(msg);

# takes the list of ids that were successfully received/uploaded
# to the server, and deletes them from the list of messages that
# need sending
def updateReceivedIds(msg):
    ids = msg.split(",")
    print("ids: " + str(ids))
    print("msg_log: " + str(msg_log))
    for i in ids: # note: in string form
        if (i != ""):
            msg_log.pop(int(i))
    

# checks for messages in the serialport, and
# parses through received data
def receiveMessages():
    receivedMsgs = []
    
    while (serial_port.in_waiting > 0):
        serial_msg = serial_port.readline().decode('Ascii')
        receivedMsgs.append(serial_msg)
        
    while bool(receivedMsgs):
        msg = receivedMsgs[0].split(";")
        
        if len(msg) != 3:
            print("msg either incomplete or formatted incorrectly: " + msg);
        
        # check for corruption
        if (validateMessage(msg[0] + msg[1], int(msg[2]))):
            print("msg successfully received: " + receivedMsgs[0])
            updateReceivedIds(msg[1])
        else:
            print("Invalid Checksum: " + receivedMsgs[0])
        
        receivedMsgs.pop(0)
    
    
    

# n = # of numbers to generate
def generateRandomNumberMsg(msg_id, n):
    msg = str(msg_id) + ";"    
    while (n > 2):
        msg += str(int(random() * 100)) + ","
        n -= 1
    msg += str(44) + ","# driveNum = 44
    msg += str(int(random() * 100))
    msg += ";" + str(generateChecksum(msg))
    return msg
        

if(serial_port.isOpen() is False):
    serial_port.open()

# simple test to check if receiver xbee is receiving messages
def testhello():
    while True:
        msgToSend = "hello xbee"
        serial_port.write(msgToSend.encode())
        #destination_ addy = XBee64BitAddress.from_hex_string("13A20041488079")
        #xbee.tx(dest_addr='\x00\x29', data='hello')


# send random list of numbers to sql server and ensure correct data is received
def testMsgValidation():
    nnums = 5
    msg_id = 60 # keeps track of msg ids
    while True:
        msg_to_send = generateRandomNumberMsg(msg_id, nnums)
        msg_log[msg_id] = msg_to_send
        serial_port.write(msg_to_send.encode())
        print("\nmessage sent: " + msg_to_send)
        
        msg_id += 1
        time.sleep(5)
        
        receiveMessages()
    

testMsgValidation()

#xbee.halt()
#serial_port.close()
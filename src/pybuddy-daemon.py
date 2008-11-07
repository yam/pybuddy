#!/usr/bin/python
#
# pybuddy
# python ibuddy daemon - http://code.google.com/p/pybuddy
#
# Jose.Carlos.Luna@gmail.com
# luis.peralta@gmail.com
#
# Most of the code comes from http://cuntography.com/blog/?p=17
# Which is based on http://scott.weston.id.au/software/pymissile/

import usb
import time
import sys
import socket
import os
import pwd
from ConfigParser import RawConfigParser


################
#Configuration
################
tsleep = 0.1


################
# IBUDDY class
################

class BuddyDevice:
  SETUP   = (0x22, 0x09, 0x00, 0x02, 0x01, 0x00, 0x00, 0x00)
  MESS    = (0x55, 0x53, 0x42, 0x43, 0x00, 0x40, 0x02)
  
  LEFT = 0
  RIGHT = 1

  UP = 0
  DOWN = 1

  finalMess = 0xFF

  def __init__(self, battery, buddy_product):
    try:
      self.dev=UsbDevice(0x1130, buddy_product, battery)
      self.dev.open()
      self.dev.handle.reset()
      self.resetMessage()
      self.pumpMessage()
    except NoBuddyException, e:
      raise NoBuddyException()
      
# Commands are sent as disabled bits
  def setReverseBitValue(self,num,value):
     if(value!=0):
         value=0
     else:
         value=1

     if (value==0):
         temp = 0xFF - 2**num
         self.finalMess = self.finalMess & temp
     else:
         temp = value << num
         self.finalMess = self.finalMess | temp

  def getReverseBitValue(self,num):
     temp = self.finalMess
     temp = temp >> num
     res = not(temp&1)
     return res

  def setHeadColor(self, red, green, blue):
    self.setReverseBitValue(4,red)
    self.setReverseBitValue(5,green)
    self.setReverseBitValue(6,blue)

  def setHeart(self, status):
    self.setReverseBitValue(7,status)

  def pumpMessage(self):
     self.send(self.finalMess)

  def resetMessage(self):
     self.finalMess = 0xFF

  def flick(self, direction):
     if (direction == self.RIGHT):
        self.setReverseBitValue(1,1)
        self.setReverseBitValue(0,0)
     elif(direction == self.LEFT):
        self.setReverseBitValue(1,0)
        self.setReverseBitValue(0,1)

  def wing(self, direction):
     if (direction == self.UP):
        self.setReverseBitValue(3,1)
        self.setReverseBitValue(2,0)
     elif(direction == self.DOWN):
        self.setReverseBitValue(3,0)
        self.setReverseBitValue(2,1)

  def getColors (self):
     return self.getReverseBitValue(4), self.getReverseBitValue(5), self.getReverseBitValue(6)

  def getHeart(self):
     return self.getReverseBitValue(7)

  def getWing(self):
     return self.getReverseBitValue(2)

  def getDirection(self):
     return self.getReverseBitValue(1)

  def send(self, inp):
    self.dev.handle.controlMsg(0x21, 0x09, self.SETUP, 0x02, 0x01)
    self.dev.handle.controlMsg(0x21, 0x09, self.MESS+(inp,), 0x02, 0x01)

#####################
# USB class
######################

class UsbDevice:
  def __init__(self, vendor_id, product_id, skip):
    busses = usb.busses()
    self.handle = None
    count = 0
    for bus in busses:
      devices = bus.devices
      for dev in devices:

        if dev.idVendor==vendor_id and dev.idProduct==product_id:
          if count==skip:
            sys.stderr.write("vend :%s   prod: %s\n" % (dev.idVendor, dev.idProduct))
            self.dev = dev
            
            self.conf = self.dev.configurations[0]
            self.intf = self.conf.interfaces[0][0]
            self.endpoints = []
            for endpoint in self.intf.endpoints:
              self.endpoints.append(endpoint)
              sys.stderr.write("endpoint\n")
            return
          else:
            count=count+1
    raise NoBuddyException()

  def open(self):
    if self.handle:
      self.handle = None
    self.handle = self.dev.open()
    #We need to detach HID interface
    try:
        self.handle.detachKernelDriver(0)
        self.handle.detachKernelDriver(1)
    except:
        pass

    self.handle.setConfiguration(self.conf)
    self.handle.claimInterface(self.intf)
    self.handle.setAltInterface(self.intf)

class NoBuddyException(Exception): pass


#########################################
# Decoding macros
##########################################

def macro_color (buddy,red,green,blue):
    buddy.setHeadColor(red,green,blue)
    buddy.pumpMessage()
    time.sleep(tsleep)
    buddy.resetMessage()
    buddy.pumpMessage()
    buddy.pumpMessage()

def macro_heart (buddy,heart):
    buddy.setHeart(1)
    buddy.pumpMessage()
    time.sleep(tsleep)
    buddy.resetMessage()
    buddy.pumpMessage()
    buddy.pumpMessage()

def macro_move_flap(buddy):
    buddy.flick(buddy.LEFT)
    buddy.pumpMessage()
    time.sleep(0.2)
    buddy.flick(buddy.RIGHT)
    buddy.pumpMessage()
    time.sleep(0.2)
    buddy.flick(buddy.LEFT)
    buddy.pumpMessage()
    time.sleep(0.2)
    macro_flap(buddy)

def macro_flap (buddy,heart=0):
    for i in range(2):
        buddy.resetMessage()
        buddy.wing(buddy.UP)
        if heart:
            buddy.setHeart(1)
        buddy.pumpMessage()
        time.sleep(0.1)
        buddy.resetMessage()
        buddy.wing(buddy.DOWN)
        buddy.pumpMessage()
        time.sleep(0.1)

def macro_heart (buddy):
    buddy.setHeart(1)
    buddy.pumpMessage()
    time.sleep(tsleep)
    buddy.resetMessage()
    buddy.pumpMessage()
    time.sleep(tsleep)

def macro_heart2(buddy):
    buddy.setHeart(1)
    buddy.pumpMessage()
    time.sleep(tsleep)
    buddy.resetMessage()
    buddy.pumpMessage()
    time.sleep(tsleep)
    buddy.setHeart(1)
    buddy.pumpMessage()
    time.sleep(tsleep)
    buddy.resetMessage()
    buddy.pumpMessage()
    time.sleep(tsleep)

def do_color(buddy,red,green,blue):
    r,g,b = buddy.getColors()
    try:
         param1=int(red)
         param2=int(green)
         param3=int(blue)
    except:
         param1=0
         param2=0
         param3=0

    if(param1==-1):
        param1=r

    if(param2==-1):
        param2=g

    if(param3==-1):
        param3=b

    buddy.setHeadColor(param1,param2,param3)

def decode_buddy (buddy,msg):
    orders = msg.split("\n") 
    for str in (orders): 
        cod = str.split(":")
        param=0
        if cod[0] == 'RED':
            try: do_color(buddy,cod[1],-1,-1)
            except: pass
        if cod[0] == 'GREEN':
            try: do_color(buddy,-1,cod[1],-1)
            except: pass
        if cod[0] == 'BLUE':
            try: do_color(buddy,-1,-1,cod[1])
            except: pass
        if cod[0] == 'YELLOW':
            try: do_color(buddy,cod[1],cod[1],-1)
            except: pass
        if cod[0] == 'SAPHIRE':
            try: do_color(buddy,-1,cod[1],cod[1])
            except: pass
        if cod[0] == 'VIOLET':
            try: do_color(buddy,cod[1],-1,cod[1])
            except: pass
        if cod[0] == 'HEART':
            try:
                param=int(cod[1])
            except:
                param=0
            buddy.setHeart(param)
        if cod[0] == 'C':
            try: do_color(buddy,cod[1],cod[2],cod[3])
            except: pass
        if cod[0] == 'MR':
            buddy.flick(buddy.RIGHT)
        if cod[0] == 'ML':
            buddy.flick(buddy.LEFT)
        if cod[0] == 'SLEEP':
            time.sleep(0.1)
        if cod[0] == 'WU':
            buddy.wing(buddy.UP)
        if cod[0]== 'WD':
            buddy.wing(buddy.DOWN)
        if cod[0]== 'EXEC':
            buddy.pumpMessage()
        if cod[0] == 'CLEAR':
            buddy.resetMessage()
        if cod[0]== 'RESET':
            buddy.resetMessage()
            buddy.pumpMessage()
        if cod[0] == 'MACRO_FLAP':
            macro_move_flap(buddy)
        if cod[0] == 'MACRO_FLAP2':
            macro_flap(buddy)
        if cod[0] == 'MACRO_RED':
            macro_color(buddy,1,0,0)
        if cod[0] == 'MACRO_GREEN':
            macro_color(buddy,0,1,0)
        if cod[0] == 'MACRO_BLUE':
            macro_color(buddy,0,0,1)
        if cod[0] == 'MACRO_YELLOW':
            macro_color(buddy,1,1,0)
        if cod[0] == 'MACRO_VIOLET':
            macro_color(buddy,1,0,1)
        if cod[0] == 'MACRO_SAPHIRE':
            macro_color(buddy,0,1,1)
        if cod[0] == 'MACRO_LBLUE':
            macro_color(buddy,1,1,1)
        if cod[0] == 'MACRO_HEART':
            macro_heart(buddy)
        if cod[0] == 'MACRO_HEART2':
            macro_heart2(buddy)

#######################################
# MAIN program
#######################################

config = RawConfigParser({'port': 8888,
                          'address': '127.0.0.1',
                          'user': 'nobody',
                          'usbproduct': 0001,
                          })
config._sections = {'network':{}, 'system':{}}

config_files = ["~/.pybuddy.cfg", "/etc/pybuddy/pybuddy.cfg", "/usr/local/etc/pybuddy.cfg"]
if len(sys.argv) > 1:
    config_files.append(sys.argv[1])
    
config_read = config.read(config_files)

if config_read:
    sys.stderr.write("Read config file: " + config_read[0] + "\n")
    
sys.stderr.write("Starting search...")
try:
    buddy=BuddyDevice(0, int(config.get("system", "usbproduct")))
except NoBuddyException, e:
    sys.stderr.write("Not found!")


sys.stderr.write("Starting daemon...\n")
if os.fork()==0:
    os.setsid()
else:
    sys.exit(0)
#    sys.stdout=open("/dev/null", 'w')
#    sys.stdin=open("/dev/null", 'r')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((config.get("network", "address"), int(config.get("network", "port"))))

try:
    uid = pwd.getpwnam(config.get("system", "user"))[2]
except KeyError:
    sys.stderr.write("Username ", config.get("system", "user") + " not found\n")
os.setuid(uid)


while 1:
    try:
        message, address = s.recvfrom(8192)
        print "Got data from", address
        decode_buddy(buddy, message)

    except (KeyboardInterrupt, SystemExit):
        raise

      

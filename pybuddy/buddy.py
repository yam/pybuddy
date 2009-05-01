import usb
import logging

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
    battery = 0
    product = 0


    def __init__(self, battery, buddy_product):
        try:
            self.dev=UsbDevice(0x1130, buddy_product, battery)
            self.dev.open()
            self.dev.handle.reset()
            self.resetMessage()
            self.pumpMessage()
            self.battery=battery
            self.product=buddy_product
        except NoBuddyException, e:
            raise NoBuddyException()

    # Commands are sent as disabled bits
    def setReverseBitValue(self,num,value):
        if (value==1):
            temp = 0xFF - (1<<num)
            self.finalMess = self.finalMess & temp
        elif (value==0):
            temp = 1 << num
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
        try:
            self.dev.handle.controlMsg(0x21, 0x09, self.SETUP, 0x02, 0x01)
            self.dev.handle.controlMsg(0x21, 0x09, self.MESS+(inp,), 0x02, 0x01)
        except usb.USBError:
            self.__init__(self.battery,self.product)

#####################
# USB class
######################

class UsbDevice:
    def __init__(self, vendor_id, product_id, skip):
        busses = usb.busses()
        self._log = logging.getLogger(self.__class__.__name__)
        self.handle = None
        count = 0
        for bus in busses:
            devices = bus.devices
            for dev in devices:

                if dev.idVendor==vendor_id and dev.idProduct==product_id:
                    if count==skip:
                        self._log.info("ibuddy found! vend: %s   prod: %s",dev.idVendor, dev.idProduct)
                        self.dev = dev

                        self.conf = self.dev.configurations[0]
                        self.intf = self.conf.interfaces[0][0]
                        self.endpoints = []
                        for endpoint in self.intf.endpoints:
                            self.endpoints.append(endpoint)
                            self._log.info("endpoint")
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
            self._log.info("Could not connect to Device")

        self.handle.setConfiguration(self.conf)
        self.handle.claimInterface(self.intf)
        self.handle.setAltInterface(self.intf)

class NoBuddyException(Exception): pass

if __name__ == "__main__":
    # Running Test
    import macro
    buddy = BuddyDevice(0,5)
    macro.decode_buddy(buddy, macro.macro_demo())

#!/usr/bin/python
import threading
import time
import sys
import usb.core
import usb.util
import pyautogui
import math

from ctypes import *
#windll, Structure, c_long, byref

class point(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]
    def __init__(self, x = -1, y = -1):
        self.x = x
        self.y = y
    def __add__(self,other):
        x = self.x + other.x
        y = self.y + other.y
        return point(x,y)
    def __sub__(self,other):
        x = self.x - other.x
        y = self.y - other.y
        return point(x,y)
    def __mul__(self,other):
        x = self.x * other.x
        y = self.y * other.y
        return point(x,y)
    def __truediv__(self,value):
        x = self.x / value
        y = self.y / value
        if x == 0:
            x = 1
        if y == 0:
            y = 1
        return point(math.ceil(x),math.ceil(y))
    def __floordiv__(self,value):
        x = self.x // value
        y = self.y // value
        return point(x,y)
    def __abs__(self):
        print(self.x)
        x = abs(self.x)
        y = abs(self.y)
        print(x)
        print("----------")
        return point(x,y)
    def __ceil__(self):
        x = math.ceil(self.x)
        y = math.ceil(self.y)
        print(x)
        print(y)
        return point(x,y)

    def __str__(self):
        return "({0},{1})".format(self.x,self.y)

class touch:
    def __init__(self):
        self.state = [True,False,False]
        self.allowReset = False
        self.lastLeft = time.time()
        self.touchStart = [-1,0,0]
        self.touchEnd = [-1,100,100]
        self.pressAndHold = False
        self.lastPosition = point()
        self.moved = False
        
    def checkState(self,other):
        count = 0
        for elem in self.state:
            if elem is not other[count]:
                return False
            count += 1
        return True
    
    def setState(self,state):
        if self.checkState(state):
            return False
        else:
            fingers = [1,2]
            for finger in fingers:
                if self.state[finger] is True and state[finger] is False:
                    self.touchEnd[finger] = time.time()
                if self.state[finger] is False and state[finger] is True:
                    self.touchStart[finger] = time.time()
            self.state = state
            return True

    def isLeftClick(self):
        if self.state[0] is True and self.state[1] is False and self.state[2] is False and not self.pressAndHold:
            if self.touchStart[1] > self.touchStart[2] and (self.touchEnd[1] - self.touchStart[1] < .3):
                windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0,0)
                windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0,0)
                self.lastLeft = time.time()
                self.pressAndHold = False
                print("left click")
        if self.pressAndHold:
            print("release press and hold")
            self.pressAndHold = False
            windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0,0)

    def isPressAndHold(self):
        if time.time() - self.lastLeft < .3:
            windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0,0)
            self.pressAndHold = True
            print("start press and hold")
    
    def isRightClick(self):
        if self.state[0] is True and self.state[1] is False and self.state[2] is False:
            if abs(self.touchStart[1] - self.touchStart[2]) < .1 and (self.touchEnd[1] - self.touchStart[1] < .3) and (self.touchEnd[2] - self.touchStart[2] < .3):
                windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0,0)
                windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0,0)
                print("rightClick")

    def extractTouchPosition(self,data):
        return point(data[4] +(255 *(data[5])), data[6] +(255 *(data[7])))

    def __str__(self):
        fingers = [1,2]
        touchDiff = [0,0,0]
        for finger in fingers:
            touchDiff[finger] = self.touchEnd[finger] - self.touchStart[finger]
        return str(str(self.state)+" "+(str(touchDiff)))

MOUSEEVENTF_LEFTDOWN = 0x0002 # left button down 
MOUSEEVENTF_LEFTUP = 0x0004 # left button up 
MOUSEEVENTF_RIGHTDOWN = 0x0008 # right button down 
MOUSEEVENTF_RIGHTUP = 0x0010 # right button up
MOUSEEVENTF_WHEEL = 0x0800
INITIAL_TOUCH = 0
MOVEMENT = 1

cursor = point()
screen = touch()

    
def getPos(num):
    num = math.ceil(abs(num) * (num/2))
    if num > 100:
        num = 100
    return num

def mouseMove(diff):
    windll.user32.GetCursorPos(byref(cursor))
    windll.user32.SetCursorPos((cursor.x+diff.x),cursor.y+diff.y)
    screen.moved = True

def mouseScroll(diff):
    windll.user32.GetCursorPos(byref(cursor))
    windll.user32.mouse_event(MOUSEEVENTF_WHEEL, cursor.x, cursor.y, diff.y,0)
    screen.moved = True

               
def doEverything():
    # decimal vendor and product values
    dev = usb.core.find(idVendor=1659, idProduct=8963)
    interface = 0
    endpoint = dev[0][(0,0)][0]
    try:
        if dev.is_kernel_driver_active(interface):
            print('Detaching kernel driver for interface %d '
                         'of %r on ports %r' % (interface, self._device, self._ports))
            dev._device.detach_kernel_driver(interface)
    except NotImplementedError:
        pass
    
    lastPoint = point()
    curPoint = point()

    touchEnd = time.time()
    touchStart = time.time()
    clickRegistered = False
    moved = False
    
    sencondIsLast = False


    #only supports 2 fingers right now

    while True :
        try:
            data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
            #this determines the number of fingers touching the screen... only supports up to 2 fingers for now
            if data[1] == INITIAL_TOUCH:
                if data[2] == 0 and (data[10] == 0 or data[10] == 1 or data[10] == 2):
                    if screen.setState([True,False,False]):
                        if screen.moved == False:
                            screen.isLeftClick()
                            screen.isRightClick()
                        screen.lastPosition = point()
                        screen.allowReset = False
                        screen.moved = False
                    continue
                if data[2] == 0 and data[10] == 3:
                    if screen.allowReset == True:
                        screen.allowReset = False
                        continue
                    if screen.setState([False,False,True]):
                        screen.allowReset = False
                    continue
                if data[2] == 1 and data[3] !=  0:
                    screen.isPressAndHold()
                    screen.setState([False,True,False])
                    continue
                if data[2] == 2:
                    if screen.checkState([False,False,True]) and screen.allowReset is False:
                        screen.allowReset = True
                        continue
                    if screen.setState([False,True,True]):
                        screen.allowReset = False
                    continue
            if data[1] is MOVEMENT:
                ##single touch
                if screen.checkState([False,True,False]):
                    print("one fingers")
                    if screen.lastPosition.x == -1:
                        screen.lastPosition = screen.extractTouchPosition(data)
                    else:
                        current = screen.extractTouchPosition(data)
                        diff = current - screen.lastPosition
                        diff = point(getPos(diff.x),getPos(diff.y))
                        if diff.x == 0 and diff.y == 0:
                            continue
                        #print(diff)
                        thread = threading.Thread(target = mouseMove, args=(diff,))
                        thread.start()
                        screen.lastPosition = current
                if screen.checkState([False,True,True]):
                    print("two fingers")
                    if screen.lastPosition.x == -1:
                        screen.lastPosition = screen.extractTouchPosition(data)
                    else:
                        current = screen.extractTouchPosition(data)
                        diff = current - screen.lastPosition
                        diff = point(getPos(diff.x),getPos(diff.y))
                        if diff.x == 0 and diff.y == 0:
                            continue                        
                        thread = threading.Thread(target = mouseScroll, args=(diff,))
                        thread.start()
                        screen.lastPosition = current
                        
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                continue
                # release the device
                usb.util.release_interface(dev, interface)
                # reattach the device to the OS kernel


thread2 = threading.Thread(target = doEverything)
thread2.start()
#thread1 = threading.Thread(target = idleScreen)
#thread1.start()

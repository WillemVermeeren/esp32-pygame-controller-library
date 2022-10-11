

import bluetooth
import pygame
from pygame.locals import *     
import sys
import socket
import threading
import json
import math
import random

pygame.init()

FPS = 30
SCALE = 4


BLACK = (15, 15, 15)
WHITE = (255, 255, 255)
GREEN = (10, 125, 10)
BLUE = (63, 127, 188)

keys = {}
kickedList = []

def chechForTerminate():   # checks if the program has been terminatated by either pressing space or X
    for event in pygame.event.get():  #
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

def terminate():  # terminats the game
    disconnectBluetooth()
    pygame.quit()
    sys.exit()

def scaleImageTimes(image, times):  # properli scales the image and if you want to tweak things (in terms of scaling the image) you van do it here
    width = image.get_width()*times
    height = image.get_height()*times
    return pygame.transform.scale(image, (width, height))


def startupAnimation(): # does the shitty startup animation
    BLsurface.fill(BLACK)
    tickSound = pygame.mixer.Sound("BLcontrollerAssets\\sound\\KeyboardPress.wav")

    string1 = "built with BLconnect"

    string2 = "> Made by Willem Vermeeren"

    font = pygame.font.Font('BLcontrollerAssets\\fonts\\Modeseven-L3n5.ttf', 70)

    for i, letter in enumerate(string1):
        pygame.mixer.Sound.play(tickSound)
        chechForTerminate()
        text = font.render(string1[0:i+1]+"_", True, GREEN, BLACK)
        textRect = text.get_rect()
        textRect.x = WIDTH/2-textRect.width/2
        textRect.y = HEIGHT/2-textRect.height/2
        BLsurface.blit(text, textRect)
        fpsClock.tick(FPS/4)
        pygame.display.update()
    

    font = pygame.font.Font('BLcontrollerAssets\\fonts\\Modeseven-L3n5.ttf', 50)

    for i, letter in enumerate(string2):

        chechForTerminate()

        text = font.render(string2[0:i+1], True, GREEN, BLACK)
        textRect = text.get_rect()
        textRect.left
        textRect.y=HEIGHT-textRect.height-10

        BLsurface.blit(text, textRect)
        fpsClock.tick(FPS)
        pygame.display.update()

    for i in range(0, FPS*2):
        chechForTerminate()
        fpsClock.tick(FPS)
    

def updateKeysLoop():  # a loop that runs in the barground collecting the keyinput of the controllers
    global connectedDevices, connectedControllerAmount, bluetoothActivated, keys, terminateBluetooth

    terminateBluetooth = False
    while not terminateBluetooth:
        for i in range(0, connectedControllerAmount):
            if i<len(connectedDevices):
                try:
                    connectedDevices[i]["socket"].send("keys".encode())
                    connectedDevices[i]["socket"].settimeout(0.5)
                    data = connectedDevices[i]["socket"].recv(2048)
                    if data!=0:
                        keys["controller"+str(i+1)] = json.loads(data)
                except:
                    pass

            else:
                keys["controller"+str(i+1)] = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}

def connectControllerLoop():
    global connectedDevices, connectedControllerAmount, connectDevices, terminateBluetooth, kickedList
    terminateBluetooth = False
    connectDevices = True
    connectedDevices = []

    for i in range(1, connectedControllerAmount):
        keys["controller"+str(i)] = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}

    

    while not terminateBluetooth and connectDevices:
        nearby_devices = bluetooth.discover_devices(duration=2, lookup_names=True, flush_cache=True) # discovers devices
        for adress, name in nearby_devices:
            if "controller" in name:
                newDevice = True
                for device in connectedDevices:
                    try:
                        deviceAdress, port = device["socket"].getpeername()
                    except:
                        newDevice = False

                    if adress==deviceAdress:
                        newDevice = False

                for kickedDevice in kickedList:
                    if kickedDevice["adressName"]==adress:
                        newDevice = False
                        break


                if not newDevice:
                    continue

                for i in range(1, 60):
                    try:

                        connectedDevices.append({"socket":socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM), "name": name})    
                        connectedDevices[len(connectedDevices)-1]["socket"].connect((adress, i))

                        break
                    except:
                        print("port "+str(i)+" is occupied")

        for i, sock in enumerate(connectedDevices):
            try:
                sock["socket"].send("ping".encode())
            except:
                print("closing "+str(i))
                sock["socket"].close()
                connectedDevices.pop(i)

        for i, kickedDevice in enumerate(kickedList):
            kickedDevice["blCyclesKicked"]+=1
            if kickedDevice["blCyclesKicked"]>10:
                kickedList.pop(i)


def selectionScreenKeyUpdate():
    global connectDevices, menuKeysPressed
    while not terminateBluetooth and connectDevices:
        if len(connectedDevices)>0:
            try:
                connectedDevices[0]["socket"].send("keys".encode())
                connectedDevices[0]["socket"].settimeout(0.5)
                data = connectedDevices[0]["socket"].recv(1024)

                if data==0:
                    menuKeysPressed = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}
                else:
                    menuKeysPressed = json.loads(data)
            except:
                pass


BACKGROUNDELEMENTS = [
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud1.png"), SCALE),
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud2.png"), SCALE),
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud3.png"), SCALE),
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud4.png"), SCALE),
]

class backroundElement:
    def __init__(self, surface):
        self.surface = surface

        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

        self.image = BACKGROUNDELEMENTS[random.randint(0, len(BACKGROUNDELEMENTS)-1)]

    def moveAndDraw(self):
        self.x-=0.25

        if self.x <= -self.image.get_width():
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT)

        self.surface.blit(self.image, (math.floor(self.x), self.y))


        
        

# ------- user functions -------------------


def connectBluetooth(on, surface, controllerAmount):
    print("connecting")
    global WIDTH, HEIGHT, BLsurface, fpsClock, connectedControllerAmount, bluetoothActivated, keys, connectedDevices, connectDevices, menuKeysPressed, kickedList, SCALE
    connectedControllerAmount = controllerAmount
    BLsurface = surface
    bluetoothActivated = on
    for i in range(0, controllerAmount): 
        keys["controller"+str(i+1)] = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}

    if not bluetoothActivated:
        return

    fpsClock = pygame.time.Clock()
    WIDTH, HEIGHT = surface.get_size() # inits all important stuff

    controllerListWidth = controllerAmount*108*SCALE
    while controllerListWidth>WIDTH-20:
        SCALE-=1
        controllerListWidth = controllerAmount*108*SCALE

    if SCALE<=0:
        	
        print("\033[31m Not enough screen space for your specified controller amount  \n")     
        print("\033[0m allow less controllers or get a wider screen\n")   
        pygame.quit()
        sys.exit()

    startupAnimation() #startup animtion


    CONTROLLERIMAGE = scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\controller.png"), SCALE)
    NOCONTROLLERIMAGE = scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\noController.png"), SCALE)
    
    font = pygame.font.Font('BLcontrollerAssets\\fonts\\Modeseven-L3n5.ttf',7*SCALE)

    menuKeysPressed = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}
    previousMenuKeysPressed = menuKeysPressed
    controllerSelected = 0


    beginX = math.floor(WIDTH/2- (NOCONTROLLERIMAGE.get_width()*1.2*connectedControllerAmount)/2)
    BLsurface.fill(BLUE)
    for i in range(0, controllerAmount):
        BLsurface.blit(NOCONTROLLERIMAGE, (beginX+NOCONTROLLERIMAGE.get_width()*1.2*i, HEIGHT/2))

    pygame.display.update()

    connectBluetoothDeviceThread = threading.Thread(target=connectControllerLoop)
    connectBluetoothDeviceThread.start()

    getKeysThread = threading.Thread(target=selectionScreenKeyUpdate)
    getKeysThread.start()

    activeBackgroundElements = []
    for i in range(0, 10):
        activeBackgroundElements.append(backroundElement(BLsurface))


    while True:
        currentLoopCycleConnected = len(connectedDevices) # i do it this way to prevent the variable changin mid loop cycle and breaking stuff
        chechForTerminate() # makes the programm terminatable

        previousMenuKeysPressed = menuKeysPressed
        
        

        BLsurface.fill(BLUE)
        
        for backgroundElement in activeBackgroundElements:
            backgroundElement.moveAndDraw()

        for i in range(0, controllerAmount):
            if i<currentLoopCycleConnected:
                
                BLsurface.blit(CONTROLLERIMAGE, (math.floor(beginX+CONTROLLERIMAGE.get_width()*1.2*i), HEIGHT/2))

                if i == controllerSelected:
                    controllerName = font.render(connectedDevices[i]["name"], True, BLUE, WHITE)
                else:
                    controllerName = font.render(connectedDevices[i]["name"], True, WHITE, BLUE)

                controllerNameRect = controllerName.get_rect()
                controllerNameRect.x = math.floor(beginX+CONTROLLERIMAGE.get_width()*1.2*i  + CONTROLLERIMAGE.get_width()/2-controllerNameRect.width/2)
                controllerNameRect.y = HEIGHT/2+CONTROLLERIMAGE.get_height()+20
                BLsurface.blit(controllerName, controllerNameRect)
            else:
                BLsurface.blit(NOCONTROLLERIMAGE, (beginX+NOCONTROLLERIMAGE.get_width()*1.2*i, HEIGHT/2))

        
            
        pygame.display.update()

        if (not menuKeysPressed["b"]) and previousMenuKeysPressed["b"]:
            connectDevices = False
            GetBluetoothKeysThread = threading.Thread(target=updateKeysLoop)
            GetBluetoothKeysThread.start()
            return

        if (not menuKeysPressed["left"]) and previousMenuKeysPressed["left"]:
            controllerSelected-=1

        if (not menuKeysPressed["right"]) and previousMenuKeysPressed["right"]:
            controllerSelected+=1

        if controllerSelected < 0:
            controllerSelected = currentLoopCycleConnected-1

        if controllerSelected > currentLoopCycleConnected-1:
            controllerSelected = 0

        if (not menuKeysPressed["a"]) and previousMenuKeysPressed["a"]:
            adressName, socket = connectedDevices[controllerSelected]["socket"].getpeername()
            kickedList.append({"adressName":adressName, "blCyclesKicked":0})
            try:
                connectedDevices[controllerSelected]["socket"].close()
            except:
                pass 
            connectedDevices.pop(controllerSelected)

def getBluetoothKeys():
    global keys
    return keys

def disconnectBluetooth():

    global terminateBluetooth
    terminateBluetooth = True

    for device in connectedDevices:
        try:
            device["socket"].close()
        except:
            pass
    


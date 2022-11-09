# to the person having to read this mess
#
# i am sorry


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


BLACK = (15, 15, 15) # colors constants
WHITE = (255, 255, 255)
GREEN = (10, 125, 10)
BLUE = (63, 127, 188)

keys = {} # the keys currently pressed by the controllers
kickedList = [] #list of devices in rejoin cooldown because of kick

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

def scaleImageTimes(image, times):  # properly scales the image and if you want to tweak things (in terms of scaling the image) you van do it here
    width = image.get_width()*times
    height = image.get_height()*times
    return pygame.transform.scale(image, (width, height))


def startupAnimation(): # animation screen DO NOT CHANGE OR REMOVE TILL 31/june/2023 
    BLsurface.fill(BLACK)
    tickSound = pygame.mixer.Sound("BLcontrollerAssets\\sound\\KeyboardPress.wav") # keys keyboard sound

    string1 = "built with BLconnect" # main title

    string2 = "> Made by Willem Vermeeren" # subtitle

    font = pygame.font.Font('BLcontrollerAssets\\fonts\\Modeseven-L3n5.ttf', 70) #main font

    for i, letter in enumerate(string1): # prints the main title letter for letter and centers the text
        pygame.mixer.Sound.play(tickSound) # plays sound
        
        chechForTerminate() # checks for terminate request
        
        text = font.render(string1[0:i+1]+"_", True, GREEN, BLACK) # generates the title surface and dimensions
        textRect = text.get_rect()
        textRect.x = WIDTH/2-textRect.width/2
        textRect.y = HEIGHT/2-textRect.height/2
        
        BLsurface.blit(text, textRect) # blist the title surface and updates
        fpsClock.tick(FPS/4)
        pygame.display.update()
    

    font = pygame.font.Font('BLcontrollerAssets\\fonts\\Modeseven-L3n5.ttf', 50) #subtitle font

    for i, letter in enumerate(string2): # prints subtitle letter by letter

        chechForTerminate() # checks for terminate request

        text = font.render(string2[0:i+1], True, GREEN, BLACK) # generates subtitle surface and dimensions
        textRect = text.get_rect()
        textRect.left
        textRect.y=HEIGHT-textRect.height-10

        BLsurface.blit(text, textRect) # blits surface and updates
        fpsClock.tick(FPS)
        pygame.display.update()

    for i in range(0, FPS*2): # lets the title screen stay for 2 secondes before exiting function
        chechForTerminate()
        fpsClock.tick(FPS)
    

def updateKeysLoop():  # a loop that runs in the barground collecting the keyinput of the controllers
    global connectedDevices, connectedControllerAmount, bluetoothActivated, keys, terminateBluetooth

    terminateBluetooth = False # says if the bluetooth library should terminate
    while not terminateBluetooth:
        
        for i in range(0, connectedControllerAmount): # goes through all the controller indexes
            if i<len(connectedDevices): #checks if a device is connected for that index
                try:
                    connectedDevices[i]["socket"].send("keys".encode()) # if connected it asks for the keys currently pressed
                    connectedDevices[i]["socket"].settimeout(0.5)
                    data = connectedDevices[i]["socket"].recv(2048)
                    if data!=0:
                        keys["controller"+str(i+1)] = json.loads(data) # if something is received it updates the controller keys in the dictionary
                except:
                    pass

            else:
                keys["controller"+str(i+1)] = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False} # if there is no controller connected on this index it just returns everything false

def connectControllerLoop(): # loop that checks for controllers tries to connect to them and if one doesn't respond anymore disconencts it
    global connectedDevices, connectedControllerAmount, connectDevices, terminateBluetooth, kickedList
    terminateBluetooth = False
    connectDevices = True
    connectedDevices = []

    for i in range(1, connectedControllerAmount): # creates the dictionary fo all the controllers with their key state
        keys["controller"+str(i)] = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}

    

    while not terminateBluetooth and connectDevices:
        nearby_devices = bluetooth.discover_devices(duration=2, lookup_names=True, flush_cache=True) # discovers devices
        for adress, name in nearby_devices:
            if "controller" in name: # if the name contrains "controller" it tries to connect
                newDevice = True
                for device in connectedDevices: # checks if the device is already connected
                    try:
                        deviceAdress, port = device["socket"].getpeername()
                    except:
                        newDevice = False

                    if adress==deviceAdress:
                        newDevice = False

                for kickedDevice in kickedList: #checks if the device is on a kick cooldown
                    if kickedDevice["adressName"]==adress:
                        newDevice = False
                        break


                if not newDevice:
                    continue

                for i in range(1, 60): # tries the first 60 ports on the computer so if one is already in use it will skip to the next
                    try:

                        connectedDevices.append({"socket":socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM), "name": name})    
                        connectedDevices[len(connectedDevices)-1]["socket"].connect((adress, i))

                        break
                    except:
                        print("port "+str(i)+" is occupied")

        for i, sock in enumerate(connectedDevices): #checks if devices still connected
            try:
                sock["socket"].send("ping".encode())
            except:
                print("closing "+str(i))
                sock["socket"].close()
                connectedDevices.pop(i)

        for i, kickedDevice in enumerate(kickedList): # updates kick cooldown
            kickedDevice["blCyclesKicked"]+=1
            if kickedDevice["blCyclesKicked"]>10:
                kickedList.pop(i)


def selectionScreenKeyUpdate(): # a loop that updates the keys from the "party leader" in the selection screen
    global connectDevices, menuKeysPressed
    while not terminateBluetooth and connectDevices:
        if len(connectedDevices)>0: # checks if a device is connected
            try:
                connectedDevices[0]["socket"].send("keys".encode()) #gets the keys
                connectedDevices[0]["socket"].settimeout(0.5)
                data = connectedDevices[0]["socket"].recv(1024)

                if data==0:
                    menuKeysPressed = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}
                else:
                    menuKeysPressed = json.loads(data)
            except:
                pass 


BACKGROUNDELEMENTS = [ # clouds images in selection screen
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud1.png"), SCALE),
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud2.png"), SCALE),
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud3.png"), SCALE),
    scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\backroundStuff\\cloud4.png"), SCALE),
]

class backroundElement: # class for background elements
    def __init__(self, surface):
        self.surface = surface

        self.x = random.randint(0, WIDTH) #their position
        self.y = random.randint(0, HEIGHT)

        self.image = BACKGROUNDELEMENTS[random.randint(0, len(BACKGROUNDELEMENTS)-1)] # set image as random cloud

    def moveAndDraw(self): # moves the cloud by a distance and draws itself
        self.x-=0.25

        if self.x <= -self.image.get_width():
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT)

        self.surface.blit(self.image, (math.floor(self.x), self.y))


        
        

# ------- user functions ------------------- (the only functions the user should be concerned about)


def connectBluetooth(on, surface, controllerAmount): # function for connecting bluetooth devices
    print("connecting")
    global WIDTH, HEIGHT, BLsurface, fpsClock, connectedControllerAmount, bluetoothActivated, keys, connectedDevices, connectDevices, menuKeysPressed, kickedList, SCALE
    
    connectedControllerAmount = controllerAmount # max amount of controllers
    BLsurface = surface #the surface 
    bluetoothActivated = on # if the library should be active or not
    
    for i in range(0, controllerAmount): # creates the keys variable if for some reason it's not defined yet
        keys["controller"+str(i+1)] = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}

    if not bluetoothActivated: # ends if bluetooth is deactivated
        return

    fpsClock = pygame.time.Clock() # gets pygame stuff
    WIDTH, HEIGHT = surface.get_size() # inits all important stuff

    controllerListWidth = controllerAmount*108*SCALE #scalesdown the images so the will fit on screen
    while controllerListWidth>WIDTH-20:
        SCALE-=1
        controllerListWidth = controllerAmount*108*SCALE

    if SCALE<=0: #if the scale is to small things can't be rendered so i made it exit here (unless you will play with more than 10 players this shouldn't be a problem
        	
        print("\033[31m Not enough screen space for your specified controller amount  \n")     
        print("\033[0m allow less controllers or get a wider screen\n")   
        pygame.quit()
        sys.exit()

    startupAnimation() #startup animtion


    CONTROLLERIMAGE = scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\controller.png"), SCALE) # image for the controller
    NOCONTROLLERIMAGE = scaleImageTimes(pygame.image.load("BLcontrollerAssets\\graphics\\noController.png"), SCALE) # image for the indexes where no controller is connected
    
    font = pygame.font.Font('BLcontrollerAssets\\fonts\\Modeseven-L3n5.ttf',7*SCALE)

    menuKeysPressed = {'up': False, 'down': False, 'left': False, 'right': False, "a":False, "b":False}
    previousMenuKeysPressed = menuKeysPressed # sets the menuKeysPressed en previusMenuKeysPressed variables
    controllerSelected = 0 # what controller is selected


    beginX = math.floor(WIDTH/2- (NOCONTROLLERIMAGE.get_width()*1.2*connectedControllerAmount)/2) #the begin x for the images
    BLsurface.fill(BLUE) # draws sky
    for i in range(0, controllerAmount): # draws controller slots
        BLsurface.blit(NOCONTROLLERIMAGE, (beginX+NOCONTROLLERIMAGE.get_width()*1.2*i, HEIGHT/2))

    pygame.display.update() # updates screen

    connectBluetoothDeviceThread = threading.Thread(target=connectControllerLoop)
    connectBluetoothDeviceThread.start() # starts conenctionloop in seperet thread

    getKeysThread = threading.Thread(target=selectionScreenKeyUpdate)
    getKeysThread.start() # starts the thread

    activeBackgroundElements = [] # draws the clouds
    for i in range(0, 10):
        activeBackgroundElements.append(backroundElement(BLsurface))


    while True:
        currentLoopCycleConnected = len(connectedDevices) # i do it this way to prevent the variable changin mid loop cycle and breaking stuff
        chechForTerminate() # makes the programm terminatable

        previousMenuKeysPressed = menuKeysPressed # 
        
        

        BLsurface.fill(BLUE) #resets sky
        
        for backgroundElement in activeBackgroundElements:
            backgroundElement.moveAndDraw() #moves the clouds

        for i in range(0, controllerAmount):
            if i<currentLoopCycleConnected: # draws the controller image and draws the name
                
                BLsurface.blit(CONTROLLERIMAGE, (math.floor(beginX+CONTROLLERIMAGE.get_width()*1.2*i), HEIGHT/2))

                if i == controllerSelected:
                    controllerName = font.render(connectedDevices[i]["name"], True, BLUE, WHITE) # if the controller is selected it gets a white background
                else:
                    controllerName = font.render(connectedDevices[i]["name"], True, WHITE, BLUE)

                controllerNameRect = controllerName.get_rect()
                controllerNameRect.x = math.floor(beginX+CONTROLLERIMAGE.get_width()*1.2*i  + CONTROLLERIMAGE.get_width()/2-controllerNameRect.width/2)
                controllerNameRect.y = HEIGHT/2+CONTROLLERIMAGE.get_height()+20
                BLsurface.blit(controllerName, controllerNameRect)
            else:
                BLsurface.blit(NOCONTROLLERIMAGE, (beginX+NOCONTROLLERIMAGE.get_width()*1.2*i, HEIGHT/2))

        
            
        pygame.display.update() #updates the display

        if (not menuKeysPressed["b"]) and previousMenuKeysPressed["b"]:
            connectDevices = False
            GetBluetoothKeysThread = threading.Thread(target=updateKeysLoop) #starts the game
            GetBluetoothKeysThread.start()
            return

        if (not menuKeysPressed["left"]) and previousMenuKeysPressed["left"]: # moves selector to left
            controllerSelected-=1

        if (not menuKeysPressed["right"]) and previousMenuKeysPressed["right"]: # moves elector to right
            controllerSelected+=1

        if controllerSelected < 0:
            controllerSelected = currentLoopCycleConnected-1 # makes selector go over edge

        if controllerSelected > currentLoopCycleConnected-1: # makes selector go over edge
            controllerSelected = 0

        if (not menuKeysPressed["a"]) and previousMenuKeysPressed["a"]: # kicks the controller and closes socket
            adressName, socket = connectedDevices[controllerSelected]["socket"].getpeername()
            kickedList.append({"adressName":adressName, "blCyclesKicked":0})
            try:
                connectedDevices[controllerSelected]["socket"].close()
            except:
                pass 
            connectedDevices.pop(controllerSelected)

def getBluetoothKeys(): # returns the keys variable
    global keys
    return keys

def disconnectBluetooth(): # a function to safly end the bluetooth library

    global terminateBluetooth
    terminateBluetooth = True

    for device in connectedDevices:
        try:
            device["socket"].close()
        except:
            pass
    


###################################################################################
###################################################################################
#!/usr/bin/python

# etch-a-sketch controller using 28BYJ-48 stepper motors
# written by Noah Carpenter

import smbus
import time
import matplotlib.pyplot as plt
import numpy as np
import math

#bus = smbus.SMBus(0) # old versions of Raspberry Pi use I2C bus 0
bus = smbus.SMBus(1) # new versions of Raspberry Pi use I2C bus 1

# Add motor number to base address to get the motor's I2C address
BASE_ADDR = 0x20 # I2C base address for PCF8574

#I2CDELAY is the delay (2) between I2C commands
I2CDELAY = 0.002

# mstate stores the states of all the motors
mstate=[0 for x in range(8)]

# coil[n] describes which coils are energized in state[n]
coil = [0 for x in range(8)]
coil[0] = 0b0001 # coil 1 is energized in state 0
coil[1] = 0b0011 # coils 1 and 2 are energized in state 1
coil[2] = 0b0010 # coil 2 is energized in state 2
coil[3] = 0b0110 # coils 2 and 3 are energized in state 3
coil[4] = 0b0100 # coil 3 is energized in state 4
coil[5] = 0b1100 # coils 3 and 4 are energized in state 5
coil[6] = 0b1000 # coil 4 is energized in state 6
coil[7] = 0b1001 # coils 1 and 4 are energized in state 7

# motor(mnum, change) changes the state of motor <mnum> by <change>
# Note that the change may be fractional, but only the integer value is returned
# <change> must be between -1 and +1 (inclusive)

#################################################################################
#################################################################################

#Trey's & Noah's Stuff:

#################################################################################
#Global positional variables
posX = 0
posY = 0
currentAngle = 0
hitchX=190
hitchY=200
xDir = 0
yDir = 0
prevxDir = 0
prevyDir = 0
#################################################################################

#More Derin Stuff:
#################################################################################
#################################################################################

def motor(mnum,change):
    mnum = int(mnum)
    if mnum<0: # motor number is outside normal range
        return 0
    if mnum>=8: # motor number is outside normal range
        return 0
    if change < -1: # change can't be less than -1
        change = -1
    if change > 1: # change can't be greater than 1
        change = 1
    mstate[mnum] += change
    if mstate[mnum] >=8: # wrap state back down to range [0,8)
        mstate[mnum]-=8
    if mstate[mnum] <0: # wrap state back up to range [0,8)
        mstate[mnum]+=8
    return int(mstate[mnum])
################################################################################
################################################################################


#Originally Derin, But we edited the crap out of this:
#################################################################################
# draw(deltax,deltay) draws a line from the current point to (dx,dy)
def draw(deltax, deltay):
    
    deltax = int(deltax)
    deltay = int(deltay)
    adeltax = abs(deltax)
    adeltay = abs(deltay)
    delta = adeltax
#################################################################################



    global posX
    global posY
    global prevxDir
    global prevyDir
    #print("Original Position: ",posX,", ",posY) #Debug
    #print("Drawing...")




   
    if (adeltay >delta): # delta is the largest, absolute change
        delta = adeltay
    delta=int(delta)

    if delta==0: #Leave the method if there's no change
        return
    
    dx = deltax/delta
    dy = deltay/delta

    
    for i in range(int(hitchX*100/delta)):
        if dx > 0:
            hx = 1
        elif dx < 0:
            hx = -1
        else:
            hx = 0

            
        oldstate = motor(0,0) # get current state of x-motor
        newstate = motor(0,hx) 
        if oldstate != newstate: # increment the x-motor
            bus.write_byte(BASE_ADDR+0, coil[newstate])
            time.sleep(I2CDELAY)
        time.sleep(I2CDELAY)
        

    for i in range(int(hitchY*200/delta)):
        if dy > 0:
            hy = 1
        elif dy < 0:
            hy = -1
        else:
            hy = 0
            
        oldstate = motor(1,0) # get current state of y-motor
        newstate = motor(1,hy)
        if oldstate != newstate: # increment the y-motor
            bus.write_byte(BASE_ADDR+1, coil[newstate])
            time.sleep(I2CDELAY)

    for i in range(delta):
        oldstate = motor(0,0) # get current state of x-motor
        newstate = motor(0,dx) 
        if oldstate != newstate: # increment the x-motor
            bus.write_byte(BASE_ADDR+0, coil[newstate])
            time.sleep(I2CDELAY)
        oldstate = motor(1,0) # get current state of y-motor
        newstate = motor(1,dy)
        if oldstate != newstate: # increment the y-motor
            bus.write_byte(BASE_ADDR+1, coil[newstate])
            time.sleep(I2CDELAY)

    posX = posX+deltax #Update position variables. Note: This needs to be changed depending
    posY = posY+deltay #on how the draw function is calibrated
    #print("Complete.")
    #print("New Positon: ",posX,", ",posY)

def drawPolar(angDeg,radius):
    angRad = (angDeg)*(np.pi/180)
    x = radius*np.cos(angRad)
    y = radius*np.sin(angRad)
    draw(x,y)

#Positional functions

#Calibrate current position to be 0,0
def calibrateXY():
    global posX #init global position variables
    global posY
    posX = 0
    posY = 0

#Sends cursor to specified point
def gotoXY(gotoX,gotoY):
    global posX
    global posY
    deltax = gotoX-posX
    deltay = gotoY-posY
    draw(deltax,deltay)

def polygon(n, side):
    
    print("Current hitchX:",hitchX)
    print("Current hitchY:",hitchY)

    for i in range(n):
        angle =   np.pi *2*i/n
        draw(side*np.cos(angle),side*np.sin(angle))

######################################################################


def circle(a,b,arcDegrees,startingDegree):
    startDegreeRad = startingDegree*(math.pi/180) 
    for i in range(arcDegrees):
        if i%5==0:
            arcDegreesRad= i*(math.pi/180)
            changeX = a*math.sin(arcDegreesRad+startDegreeRad)
            changeY = b*math.cos(arcDegreesRad+startDegreeRad)
            draw(changeX,changeY)

def spiro(r2,r3):
    r1=500
    t=np.arange(0,np.pi*2*r2/math.gcd(r1,r2),0.001)
    t2=t*r1/r2
    x = (r1-r2)*np.cos(t)+r3*np.cos(t2)
    y = (r1-r2)*np.sin(t)-r3*np.sin(t2)

    plt.plot(x,y)
    plt.show()

    for i in range(len(t)):
        if i%10==0: #reduce resolution
            gotoXY(x[i],y[i])

def testHitch(x,y):
    global hitchX
    global hitchY
    for i in range(x):
        for j in range(y):
            hitchX = hitchX-10
            print("Current hitchX:",hitchX)
            print("Current hitchY",hitchY)
            polygon(7,1500)
            draw(4000,0)
        hitchY = hitchY-10


def changeAngle(ang):
    global currentAngle
    currentAngle = ang
    print('currentAngle',currentAngle)

def hilbert2(step,rule,angle,depth):
    global currentAngle
    if depth > 0:
        a = lambda: hilbert2(step,"a",angle,depth-1)
        b = lambda: hilbert2(step, "b", angle, depth-1)
        left = lambda: changeAngle(currentAngle+angle)
        right = lambda: changeAngle(currentAngle-angle)
        forward = lambda: drawPolar(currentAngle,step)
        if rule == "a":
            left(); b(); forward(); right(); a(); forward(); a(); right(); forward(); b(); left();
        if rule == "b":
            right(); a(); forward(); left(); b(); forward(); b(); left(); forward(); a(); right();
            
    
 

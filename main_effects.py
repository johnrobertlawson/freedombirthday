# The tech-geek alternative to Christmas lights!
# Choose a random effect from a list, and then play it for a while, before switching
# Created by Matt Dyson (mattdyson.org)
# Version 1.0 (20/12/13)

from __future__ import division
import serial
import time
import math
import random
import os
import colorsys
import pdb

from BlinkyTapeV2 import BlinkyTape

tickLength = 0.05 # Time per 'tick'
minLength = 15# Minimum length of particular display
maxLength = 25 # Max length of particular display

color_map = {
    -10: (255, 0, 255),
    0: (158, 0, 255),
    10: (0, 0, 255),
    20: (0, 126, 255),
    30: (0, 204, 255),
    40: (5, 247, 247),
    50: (127, 255, 0),
    60: (247, 247, 5),
    70: (255, 204, 0),
    80: (255, 153, 0),
    90: (255, 79, 0),
    100: (204, 0, 0),
    110: (169, 3, 3),
    120: (186, 50, 50)
}

def getRunLength():
   length = minLength + (random.random() * (maxLength - minLength))
   print("Running effect for %s seconds" % (length))
   ticksPerSec = (1 / tickLength)
   return int(length * ticksPerSec)

# Scrolling colours with smooth transition
def effect_scroll(blink):
   phase = 0
   for i in range(getRunLength()):
      for i in range(0, blink.getSize()):
         pos = math.radians(i*3) + phase
         redVal = 255 - (math.fabs(math.cos(pos) * 255))
         greenVal = 255 - (math.fabs(math.sin(pos) * 255))
         
         blink.setPixel(i,int(redVal),int(greenVal),0)
      blink.sendUpdate()
      phase += .1
      if phase==1:
         phase = 0   
      time.sleep(tickLength)

# Fade in one colour, then out, then switch colour
def effect_fade(blink):
   level = 5
   direction = 5
   color=1
   #for i in range(getRunLength()):
   while True:
      if color%6 == 0:
         blink.displayColor(level,0,0)
      elif color%6 == 1:
         blink.displayColor(0,level,0)
      elif color%6 == 2:
         blink.displayColor(0,0,level)
      elif color%6 == 3:
         blink.displayColor(level,0,level)
      elif color%6 == 4:
         blink.displayColor(0,level,level)
      elif color%6 == 5:
         blink.displayColor(level,level,0)
      
      level+=direction
      if level>250 or level<6:
         direction=-direction
      if level<6:
         color += 1
      time.sleep(tickLength)


def getTailLength(barLength):
   return 1.5 * barLength

def getBarLength():
   return 3 + int(random.random() * 8)

# Scroll a bars of a certain colour through the other colour
def effect_bars(blink):
   position = 0
   length = getBarLength()
   for x in range(getRunLength()):
      for i in range(0,blink.getSize()):
         setBarIntensity(i,position,length,blink,[250,0,0],[0,250,0])
      blink.sendUpdate()
      position+=1
      time.sleep(tickLength)
      if (position - getTailLength(length))>blink.getSize():
         position=-(length+getTailLength(length))

# Similar to the bars effect, however bounce off either end, and invert the colours
def effect_bounce(blink):
   cardinal = [209,4,4]
   gold = [255,234,0]
   position = 0
   length = getBarLength()
   direction = 1
   for x in range(getRunLength()):
      for i in range(0,blink.getSize()):
         setBarIntensity(i,position,length,blink,cardinal,gold)
      blink.sendUpdate()
      position+=direction
      time.sleep(tickLength)
      if position+length>blink.getSize() or position<0:
         direction=-direction

def setBarIntensity(led, position, length, blink, colourOn, colourOff):
   tailLength=getTailLength(length)
   if led >= position and led <= (position+length):
      blink.setPixel(led,colourOn[0],colourOn[1],colourOn[2])
   elif led < position and led > position-tailLength:
      # Trailing tail
      intensity = position-led
      colour=[]
      colour.append(int(colourOn[0] * (1/intensity)))
      colour.append(int(colourOn[1] * (1/intensity)))
      colour.append(int(colourOn[2] * (1/intensity)))
      blink.setPixel(led,colour[0],colour[1],colour[2])
   elif led < position+length+tailLength and led > position:
      # Leading tail
      intensity = led-(position+length)
      colour=[]
      colour.append(int(colourOn[0] * (1/intensity)))
      colour.append(int(colourOn[1] * (1/intensity)))
      colour.append(int(colourOn[2] * (1/intensity)))
      blink.setPixel(led,colour[0],colour[1],colour[2])
   else:
      blink.setPixel(led,colourOff[0],colourOff[1],colourOff[2])

def weather_forecast(blink,stid='KAMW'):
    print("Showing NAM forecast for "+stid)
    url = 'http://www.nws.noaa.gov/cgi-bin/mos/getmet.pl?sta='+stid
    cmd1 = 'wget {0} -O forecast.txt'.format(url)
    # pdb.set_trace()
    os.system(cmd1)
    data = open('forecast.txt','r').readlines() 
    MOS = data[9]
    # pdb.set_trace()
    # Get 90 h forecast with interpolated values
    temps = temps_from_MOS(MOS)

    # We have one pixel too many
    temps.pop(-1)
    for h in range(60):
        r,g,b = color_for_temp(temps[h])
        bt.setPixel(h,r,g,b)

    for x in range(getRunLength()):
    #while True:
        blink.sendUpdate()
        time.sleep(tickLength)

def color_for_temp(temp):
    """Returns an RGB color triplet for the given (Fahrenheit scale) temp.

    Temps colors taken from the Weather Channel mapping found at:
    http://wattsupwiththat.com/2008/06/26/color-and-temperature-perception-is-everything/
    """
    color = None
    for temp_ceil in sorted(color_map.iterkeys()):
        color = color_map[temp_ceil]
        if temp < temp_ceil:
            break
    return adjust_color(color)

def adjust_color(color, dim_factor=0.10):
    r, g, b = color
    h, s, v = colorsys.rgb_to_hsv(r / 256.0, g / 256.0, b / 256.0)
    r, g, b = colorsys.hsv_to_rgb(h, s, v * dim_factor)
    return int(r * 256), int(g * 256), int(b * 256)

def temps_from_MOS(data,fcsthr=60):
    # Initialise the list of zeros
    temp_all = [-999,] * (fcsthr+1)

    # List the forecast-time hours
    MOS_h = range(0,63,3)
    MOS_h.pop(-2) # Remove hour 57
    temp_MOS = [int(data[5+(3*n):8+(3*n)]) for n in range(len(MOS_h))]

    for h in range(fcsthr+1):
        if h in MOS_h:
            MOS_n = MOS_h.index(h)
            temp_all[h] = temp_MOS[MOS_n]

    temp_all[57] = int((temp_all[54] + temp_all[60])/2)

    for h in range(fcsthr+1):
        rem = h%3
        if rem==0:
            pass
        elif rem==1:
            temp_all[h] = int(((2*temp_all[h-1]) + temp_all[h+2])/3)  
        elif rem==2:
            temp_all[h] = int((temp_all[h-2] + (2*temp_all[h+1]))/3)  

    return temp_all

if __name__ == "__main__":

  import glob
  import optparse 

  parser = optparse.OptionParser()
  parser.add_option("-p", "--port", dest="portname",
                    help="serial port (ex: /dev/ttyUSB0)", default=None)
  (options, args) = parser.parse_args()

  if options.portname != None:
    port = options.portname
  else:
    serialPorts = glob.glob("/dev/ttyACM*")
    port = serialPorts[0]

  bt = BlinkyTape(port)

  effect_bounce(bt) 
  effect_fade(bt)

  stids = ['KMEH','KPHX','KAMW']
  for stid in stids:
    weather_forecast(bt,stid) 
  # effects = [ effect_scroll, effect_fade, effect_bars, effect_bounce ]
  # while True:
    # chosen = random.choice(effects)
    # print("Changing effect to %s" % (chosen.__name__))
    # chosen(bt)    

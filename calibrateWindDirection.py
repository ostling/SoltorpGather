import os
import glob
import sys
import re
import time
import subprocess 
import datetime
import RPi.GPIO as GPIO

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

GPIO.setmode(GPIO.BCM)

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

# "default" setup for wind direction
WIND_DIRECTION_MAP={
        1:290,
        2:248,
        3:632,
        4:601,
        5:943,
        6:828,
        7:887,
        8:704,
        9:787,
        10:409,
        11:464,
        12:85,
        13:95,
        14:67,
        15:187,
        16:129
}

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def readWindDirection():
	trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
	return trim_pot

def getIndexForValue(measuredValue):
        smallestLargerOrEqualValue = 999999999999999
        smallestLargerOrEqualIndex = 99
        largestSmallerValue = 0
        largestSmallerIndex = 0

        for index, value in WIND_DIRECTION_MAP.iteritems():
                if value < measuredValue and value > largestSmallerValue:
                        largestSmallerValue = value
                        largestSmallerIndex = index

                if value >= measuredValue and value < smallestLargerOrEqualValue:
                        smallestLargerOrEqualValue = value
                        smallestLargerOrEqualIndex = index

        #print "Largest smaller value=%s index=%s, Smallest larger value=%s index=%s" % (largestSmallerValue, largestSmallerIndex, smallestLargerOrEqualValue, smallestLargerOrEqualIndex)
        if (measuredValue - largestSmallerValue) < (smallestLargerOrEqualValue - measuredValue):
                return largestSmallerIndex
        else:
                return smallestLargerOrEqualIndex

raw_input("Point wind direction indicator to NORTH and press enter...")

measuredValue = readWindDirection()
measuredValueIndex = getIndexForValue(measuredValue)

print "Got index %s for value=%s" % (measuredValueIndex, measuredValue)

windDirectionStringPrefix = 'WIND_DIRECTION_MAP={' + '\n'
windDirectionStringPre = ''
windDirectionStringPost = ''
windDirectionStringSuffix = '}'

for index, value in WIND_DIRECTION_MAP.iteritems():
        if index < measuredValueIndex:
                windDirectionStringPre = windDirectionStringPre + '\t' + str(measuredValueIndex + index) + ':' + str(value) + '\n'
        else:
                windDirectionStringPost = windDirectionStringPost + '\t' + str(index - measuredValueIndex + 1) + ':' + str(value) + '\n'

print "Printing new varible config"
print
print windDirectionStringPrefix + windDirectionStringPost + windDirectionStringPre + windDirectionStringSuffix
print
print "Copy this into script"

GPIO.cleanup()           # clean up GPIO on normal exit
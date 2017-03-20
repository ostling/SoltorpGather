import os
import glob
import sys
import re
import time
import subprocess
import MySQLdb as mdb 
import datetime
import RPi.GPIO as GPIO
 

databaseUsername="pi" #YOUR MYSQL USERNAME, USUALLY ROOT
databasePassword="raspberry" #YOUR MYSQL PASSWORD 
databaseName="ODB" #do not change unless you named the Wordpress database with some other name

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


def saveToDatabase(wind_direction):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()

        #now=datetime.datetime.now()
        #midnight=datetime.datetime.combine(now.date(),datetime.time())
        #minutes=((now-midnight).seconds)/60 #minutes after midnight, use datead$


        with con:
                cur=con.cursor()

                cur.execute("INSERT INTO wind_direction (wind_direction, dateMeasured, timeMeasured) VALUES (%s,%s,%s)",
                			(wind_direction,currentDate, datetime.datetime.now()))

		print "Saved wind direction"
		return "true"

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

def read_wind_direction():
	trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
	return trim_pot

print "Printing wind direction:"
running = True
while running:
        try:
                print read_wind_direction()
                time.sleep(0.1)

        except KeyboardInterrupt:
                GPIO.cleanup()       # clean up GPIO on CTRL+C exit
                running = False

GPIO.cleanup()           # clean up GPIO on normal exit
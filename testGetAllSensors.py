import os
import glob
import sys
import re
import time
import subprocess
import MySQLdb as mdb
import datetime
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO


databaseUsername="pi" #YOUR MYSQL USERNAME, USUALLY ROOT
databasePassword="raspberry" #YOUR MYSQL PASSWORD
databaseName="ODB" #do not change unless you named the Wordpress database with some other name

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
except:
    print "Failed to init DS180"

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

try:
    GPIO.setmode(GPIO.BCM)

    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
except:
    print "Failed to init GPIO"

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

def read_temp_raw():
	catdata = subprocess.Popen(['cat',device_file],
	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
#        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c#, temp_f

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

def read_A1():
	trim_pot = readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS)
	return trim_pot

print "Printing A0 value:"
try:
    print read_wind_direction()
except:
    print "Failed to get wind direction"

print "Printing A1 value:"
try:
    print read_A1()
except:
    print "Failed to get A1 value"

print "Current temp BMP180:"
try:
    sensor = BMP085.BMP085()
    print sensor.read_temperature()
except:
    print "Failed to get temp BMP180 value"

print "Current pressure BMP180: "
try:
    print sensor.read_pressure()
except:
    print "Failed to get pressure BMP180 value"

print "Current temp DS180:"
try:
    print read_temp()
except:
    print "Failed to get temp DS180 value"

GPIO.cleanup()

import os
import glob
import sys
import re
import time
import subprocess
import MySQLdb as mdb 
import datetime
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# FOR DB
databaseUsername="pi" #YOUR MYSQL USERNAME, USUALLY ROOT
databasePassword="raspberry" #YOUR MYSQL PASSWORD 
databaseName="ODB" #do not change unless you named the Wordpress database with some other name

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# FOR APPLICATION
SECS_CALC_WIND_SPEED = 5
TIMEOUT_CALC_WIND_SPEED = 10
WIND_CONF_FACTOR = 1

def windMeterTick(channel):
    print "Callback"
    global ticks
    global lastRunTime
    global nextCalcTime
    global windSaved

    ticks = ticks + 1
    if (datetime.datetime.now() > nextCalcTime):
        # Convert ticks / x seconds to m/s
        runTimeInSeconds = (datetime.datetime.now() - lastRunTime).total_seconds()

        print "runTimeInSeconds=%s, ticks=%s" % (runTimeInSeconds, ticks)
        windSpeed = ( ticks / runTimeInSeconds ) * WIND_CONF_FACTOR
	windSpeed = round(windSpeed, 1)
        windSaved = saveToDatabase(windSpeed)

        nextCalcTime = datetime.datetime.now() + datetime.timedelta(0, SECS_CALC_WIND_SPEED)
        lastRunTime = datetime.datetime.now()
        ticks = 0;

# GPIO 21 -> INPUT.
# 21 will go to GND when button pressed
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(21, GPIO.FALLING, callback=windMeterTick)

def saveToDatabase(windSpeed):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        midnight=datetime.datetime.combine(now.date(),datetime.time())
        minutes=((now-midnight).seconds)/60 #minutes after midnight, use datead$


        with con:
                cur=con.cursor()
                cur.execute("INSERT INTO wind_speed (wind_speed, dateMeasured, timeMeasured) VALUES (%s,%s,%s)",(windSpeed,currentDate, datetime.datetime.now()))

		print "Saved wind speed=%s m/s" % windSpeed
		return True

print "Initiating wind measurement."

# Init global vars.
global lastRunTime
global ticks
global nextCalcTime
global windSaved

lastRunTime = datetime.datetime.now()
ticks = 0
nextCalcTime = datetime.datetime.now() + datetime.timedelta(0, SECS_CALC_WIND_SPEED)
windSaved = False

# Listen for interrupts during TIMEOUT_CALC_WIND_SPEED seconds. If nothing has happend -> assume there is no wind.
time.sleep(TIMEOUT_CALC_WIND_SPEED)

if not windSaved :
    saveToDatabase(0)
    print "Timeout after %s seconds! No wind today mate." % TIMEOUT_CALC_WIND_SPEED

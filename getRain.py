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

# The rain gauge is a self-emptying bucket-type rain gauge which activates a momentary button closure for each 0.011" of rain that are collected.
# 0.011" = 0.2794 millimeters

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
MILIMETER_PER_TICK = 0.2794

def rainMeterTick(channel):
    saveToDatabase();

# GPIO 20 -> INPUT.
# 20 will go to GND
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(20, GPIO.FALLING, callback=rainMeterTick)

def saveToDatabase():

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        cur=con.cursor()
        currentDate=datetime.datetime.now().date()

        currentRow = getCurrentRow()
        currentId = currentRow[0]
        currentNumberOfTicks = currentRow[1]

        if (currentNumberOfTicks == 0):
            cur.execute("INSERT INTO rain (ticks, mmAccumulated, dateMeasured, timeMeasured) VALUES (%s,%s,%s,%s)", (1, MILIMETER_PER_TICK, currentDate, datetime.datetime.now()))
        else:
            acc = (currentNumberOfTicks + 1) * MILIMETER_PER_TICK
            str = "ticks=%s, acc=%d", (currentNumberOfTicks+1, acc)
 
            cur.execute("UPDATE rain set ticks = %s, mmAccumulated = %s, dateMeasured = %s, timeMeasured = %s WHERE id = %s ", (currentNumberOfTicks+1, acc, currentDate, datetime.datetime.now(), currentId))

        cur.execute('COMMIT')


	return True

def getCurrentRow():
    con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
    currentDate=datetime.datetime.now().date()

    with con:
            cur=con.cursor()
            cur.execute("SELECT id, ticks FROM rain where dateMeasured = %s AND HOUR(timeMeasured) = %s", (currentDate, datetime.datetime.now().hour))
    if (cur.rowcount == 0):
        result = [0,0]
        return result
    else:
        results = cur.fetchall()
        for row in results:
            result=[row[0], row[1]]
            return row

print "Initiating rain measurement."

running = True
while running:
    try:
        time.sleep(10)

    except KeyboardInterrupt:
        running = False

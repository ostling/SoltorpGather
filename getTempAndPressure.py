import os
import glob
import sys
import re
import time
import subprocess
import MySQLdb as mdb 
import datetime
import Adafruit_BMP.BMP085 as BMP085

databaseUsername="pi" #YOUR MYSQL USERNAME, USUALLY ROOT
databasePassword="raspberry" #YOUR MYSQL PASSWORD 
databaseName="ODB" #do not change unless you named the Wordpress database with some other name

def saveTempToDatabase(temperature, pressure):
    con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
    currentDate=datetime.datetime.now().date()

    with con:
            cur=con.cursor()
            cur.execute("INSERT INTO temperatures (temperature, dateMeasured, timeMeasured, device) VALUES (%s,%s,%s,%s)",
                        (temperature,currentDate, datetime.datetime.now(), 'BMP180'))
    print "Saved temperature"

    with con:
            cur=con.cursor()
            cur.execute("INSERT INTO pressure (pressure, dateMeasured, timeMeasured, device) VALUES (%s,%s,%s,%s)",
                        (pressure,currentDate, datetime.datetime.now(), 'BMP180'))
    print "Saved pressure"
    return "true"
 
def read_temp():
    return sensor.read_temperature();

def read_pressure():
    return sensor.read_pressure();


sensor = BMP085.BMP085()
saveTempToDatabase(read_temp(), read_pressure()/100)

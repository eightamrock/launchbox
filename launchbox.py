#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import urllib2
import pytz
import datetime
import json
import socket
import fcntl
import struct
from libs import requests
import ConfigParser
from libs.matrix_keypad.rpi_keypad import keypad
from libs.Adafruit.Adafruit_CharLCD import Adafruit_CharLCD
from libs.Adafruit.Adafruit_MCP230xx import MCP230XX_GPIO

# Get github stuffz
config = ConfigParser.ConfigParser()
config.read('config.cfg')

owner = config.get('github', 'owner')
repo = config.get('github', 'repository')
token = config.get('github', 'token')
try:
  target_branch = config.get('github', 'target_branch')
except ConfigParser.NoOptionError:
  target_branch = None
headers = {
  'Authorization': "token "+token,
  'User-Agent': 'LaunchBox'
}
time_fmt = '%b %d, %Y %H:%M:%S %Z'

# IO Configs
bus = 1         # Note you need to change the bus number to 0 if running on a revision 1 Raspberry Pi.
address = 0x20  # I2C address of the MCP230xx chip.
gpio_count = 8  # Number of GPIOs exposed by the MCP230xx chip, should be 8 or 16 depending on chip.
brb_led = 8
brb_switch = 7

#Setup GPIOs for Big Red Button
GPIO.setmode(GPIO.BCM)
GPIO.setup(brb_led, GPIO.OUT)
GPIO.setup(brb_switch, GPIO.IN)
GPIO.output(brb_led, GPIO.HIGH)

# Initialize keypad
kp = keypad()

# Create MCP230xx GPIO adapter.
mcp = MCP230XX_GPIO(bus, address, gpio_count)

# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=1, pin_e=2, pins_db=[3,4,5,6], GPIO=mcp, pin_b=7)

# Clear out the LCD and turn on the backlight
lcd.clear()
lcd.backlight(True)

# Send IP to screen for 10 seconds
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
my_ip = get_ip_address("wlan0")
lcd.message("My IP is:\n" + str(my_ip))
time.sleep(10)

# Boot up
lcd.clear()
lcd.message("LaunchBox: \nTeam Kraken")
# arbitrary sleep
time.sleep(3)

def digit():
    digitPressed = None
    while digitPressed == None:
	   digitPressed = kp.getKey()
    return digitPressed

def getCode(stopChar):
    char = str(digit())    
    if char == "#":
	   return False
    else:
	   return char

def is_target(data):
  return target_branch == None or data['base']['ref'] == target_branch

def is_mergable(data):
  return data['mergeable'] is True and data['state'] == 'open'

def can_deploy(pr):

  while not can_deploy:
    url = "https://api.github.com/repos/%s/%s/pulls/%s" % (owner, repo, pr)
    req = requests.get(url, headers=headers)
    results = req.json()
    can_deploy = req.status_code == 200 and is_mergable(results) and is_target(results)
    if not can_deploy:
        return False
    else:
        return True

def merge_pr(pr):
  timestamp = datetime.datetime.now(pytz.timezone("America/New_York"))
  payload = {
    'commit_message': "LaunchBox Release - " + timestamp.strftime(time_fmt)
  }
  url = "https://api.github.com/repos/%s/%s/pulls/%s/merge" % (owner, repo, num)
  res = requests.put(url, data=json.dumps(payload), headers=headers)
  if res.json()['merged']:
    return True
  else :
    return False

def launchbox():
    
    # Boot Complete
    lcd.clear()
    lcd.message("Enter PR: \n")
    lcd.cursor()

    # Listen for PR, use # to complete * to clear
    code = ""
    char = getCode("#")
    while char != False:
        if char == "*":
            if code != "" :
            	lcd.write4bits(lcd.LCD_CURSORSHIFT)
            	lcd.message(" ")
            	lcd.write4bits(lcd.LCD_CURSORSHIFT)
                code = code[:-1]
            time.sleep(.25)
            char = getCode("#")
        else:
            lcd.message(char)
            code = code + char
            time.sleep(.25)
            char = getCode("#")

    # We now have the PR number lets check it
    lcd.noCursor()
    lcd.clear()
    lcd.message("Verifying PR \nPlease Wait")
    is_deployable = can_deploy(code)
    time.sleep(2)

    if is_deployable == True:
        lcd.clear()
        lcd.message("PR: " + code + "\nInitialized")
        time.sleep(3)

        # its deployable, lets get the part started
        # light up LED on big red button
        GPIO.output(brb_led, GPIO.LOW)
        lcd.clear()
        lcd.message("Ready to Deploy")

        # Listen for big red button press
        while GPIO.input(brb_switch) == GPIO.LOW:
            time.sleep(0.01)

        merged = merge_pr(code)
        if merged == True:
            # Successful deploy
            lcd.clear()
            lcd.message("Deploy Complete")
            GPIO.output(brb_led, GPIO.HIGH)
            time.sleep(5)
            launchbox()
        else:
            # Fail oh noessss.
            lcd.clear()
            lcd.message("Deploy Failed")
            time.sleep(5)
            launchbox()
    else:
        launchBox()
     
launchbox()

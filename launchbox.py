#!/usr/bin/python

import RPi.GPIO as GPIO
from libs.matrix_keypad.rpi_keypad import keypad
from libs.Adafruit.Adafruit_CharLCD import Adafruit_CharLCD
from libs.Adafruit.Adafruit_MCP230xx import MCP230XX_GPIO

bus = 1         # Note you need to change the bus number to 0 if running on a revision 1 Raspberry Pi.
address = 0x20  # I2C address of the MCP230xx chip.
gpio_count = 8  # Number of GPIOs exposed by the MCP230xx chip, should be 8 or 16 depending on chip.
brb_led = 9
brb_switch = 10

#Setup GPIOs for Big Red Button
GPIO.setup(brb_led, GPIO.OUT)
GPIO.setup(brb_switch, GPIO.IN)

GPIO.output(brb_led, GPIO.LOW)

# Initialize keypad
kp = keypad()

# Create MCP230xx GPIO adapter.
mcp = MCP230XX_GPIO(bus, address, gpio_count)

# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=1, pin_e=2, pins_db=[3,4,5,6], GPIO=mcp, pin_b=7)
lcd.clear()
lcd.backlight(True)

# Boot up
lcd.message("LaunchBox: \nTeam Kraken")
sleep(10)

def launchbox():
    
    # Boot Complete
    lcd.clear()
    lcd.message("Enter PR: \n")

    # Listen for PR, use # to complete * to clear

    # initialize PR 
    # successfully created PR
    # PR Complete light up LED on big red button
    GPIO.output(brb_led, GPIO.HIGH)

    # Listen for big red button press
    while GPIO.input(brb_switch) == GPIO.LOW:
        sleep(0.01)

    # Deploy/Merge PR 
    # Success
    lcd.clear()
    lcd.message("Deployment\n Complete")
    GPIO.output(brb_led, GPIO.LOW)
    launchbox()

    # Fail
    lcd.clear()
    lcd.message("Deployment\n Failed")
    launchbox()

launchbox()
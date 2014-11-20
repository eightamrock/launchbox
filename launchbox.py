#!/usr/bin/python
# Example script to show usage of MCP230xx GPIO extender to drive character LCD.

from libs.Adafruit.Adafruit_CharLCD import Adafruit_CharLCD
from libs.Adafruit.Adafruit_MCP230xx import MCP230XX_GPIO

bus = 1         # Note you need to change the bus number to 0 if running on a revision 1 Raspberry Pi.
address = 0x20  # I2C address of the MCP230xx chip.
gpio_count = 8  # Number of GPIOs exposed by the MCP230xx chip, should be 8 or 16 depending on chip.

# Create MCP230xx GPIO adapter.
mcp = MCP230XX_GPIO(bus, address, gpio_count)

# Create LCD, passing in MCP GPIO adapter.

lcd = Adafruit_CharLCD(pin_rs=1, pin_e=2, pins_db=[3,4,5,6], GPIO=mcp, pin_b=7)

lcd.clear()
lcd.backlight(True)
lcd.message("LaunchBox: \nTeam Kraken")


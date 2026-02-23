# SPDX-FileCopyrightText: 2018 Dave Astels for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Dice roller for the NeoTrellisM4

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2018 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
"""

"""
No serious, you should give Adafruit your money. Lady Ada rocks!
Copyright (c) 2026 Zach Metcalf
Licensed under the MIT license.
All text above must be included in any redistribution.
"""

# pylint: disable=global-statement

import math
import time
import random
import board
import adafruit_trellism4
import adafruit_adxl34x
import busio

# Set up the trellis and accelerometer

trellis = adafruit_trellism4.TrellisM4Express()
trellis.pixels.brightness = 0.1

i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)


number_patterns = [
    ["*  ", " * ", "  *", "   "],  # 0 # Just for animation
    ["   ", " * ", "   ", "   "],  # 1
    ["*  ", "   ", "  *", "   "],  # 2
    ["*  ", " * ", "  *", "   "],  # 3
    ["* *", "   ", "* *", "   "],  # 4
    ["* *", " * ", "* *", "   "],  # 5
    ["***", "   ", "***", "   "],  # 6
]


def display_digit(number, offset, color):
    """Display a digit.
    number     -- the number (0-9) to display
    offset     -- the left-most column of the displayed digit
    color      -- the RGB color to use to display the digit
    force_zero -- whether to leave a 0 blank (False) or display it
    """
    print("displaying", number, "at offset", offset, "with color", color)
    time.sleep(0.1)
    bits = number_patterns[number]
    for row in range(4):
        for col in range(3):
            if bits[row][col] == " " or number == 0:
                trellis.pixels[col + offset, row] = (0, 0, 0)
            else:
                trellis.pixels[col + offset, row] = color


def display_number(numbers, color, position=0):
    """Display a multi-digit number.
    If the number is > 99, the hundreds digit (1-4) is indicated on the far left column:
        100 is the top pixel, 400 is the bottom.
    number      -- the number to display
    color       -- the RGB color to use to display the digit
    force_zeros -- whether to leave a 0 in the tens place blank (False) or display it
    """
    display_digit(numbers[0], 5, color)
    display_digit(numbers[1], 1, color)
    for h in range(4):
        trellis.pixels[0, h] = (0, 0, 0)


def animate_to(numbers, color=(255, 0, 0)):
    """Perform an animation (displaying random numbers) before displaying the requested number.
    numbers -- the numbers to eventually display
    color  -- the color to use (indicates the type of dice used)
    """
    for _ in range(6):
        trellis.pixels.fill((0, 0, 0))
        display_number([random.randint(1, 6), random.randint(1, 6)], color, 0)
        time.sleep(0.1)
    trellis.pixels.fill((0, 0, 0))
    display_number(numbers, color)


def roll(sides):
    """Generate a random dice roll.
    Returns the total of the roll.
    number -- the number of dice to roll
    sides  -- the number of side on dice to roll (4, 6, 8, 10, 12, 20)
    """
    return [random.randint(1, sides), random.randint(1, sides)]


previous_reading = [None, None, None]
bound = 4.0


def shaken():
    """Detect when the Trellis is shaken.
    See http://www.profoundlogic.com/docs/display/PUI/Accelerometer+Test+for+Shaking
    TL;DR one or more axis experiences a significant (set by bound) change very quickly
    Returns whether a shake was detected.
    """
    global previous_reading
    result = False
    x, y, z = accelerometer.acceleration
    if previous_reading[0] is not None:
        result = (
            math.fabs(previous_reading[0] - x) > bound
            and math.fabs(previous_reading[1] - y) > bound
            and math.fabs(previous_reading[2] - z) > bound
        )
    previous_reading = (x, y, z)
    return result


d6 = 6

while True:
    trellis.pixels.fill((0, 0, 0))
    previous_reading = accelerometer.acceleration

    animate_to(roll(d6))
    timeout = time.monotonic() + 5.0
    while len(trellis.pressed_keys) == 0 and time.monotonic() < timeout:
        pass

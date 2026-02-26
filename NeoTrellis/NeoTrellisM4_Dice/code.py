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
No seriously, you should give Adafruit your money. Lady Ada rocks!
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
trellis.pixels.brightness = 0.05
trellis.pixels.fill((0, 0, 0))

i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)


class Player:
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.in_turn = False


class Game:
    def __init__(self):
        self.players = [
            Player("LEFT", (0, 3)),
            Player("RIGHT", (7, 3)),
        ]
        self.active_player = 0
        self.stage = "START"

    @property
    def current_player(self):
        return self.players[self.active_player]

    @property
    def non_active_player(self):
        return self.players[(self.active_player + 1) % len(self.players)]

    def switch_player(self):
        self.active_player = (self.active_player + 1) % len(self.players)
        return self.players[self.active_player]

    def next_stage(self):
        if self.stage == "START":
            self.stage = "ROLLING"
        elif self.stage == "ROLLING":
            self.stage = "MOVING"
        elif self.stage == "MOVING":
            self.switch_player()
            self.stage = "END"
        elif self.stage == "END":
            self.stage = "ROLLING"
        self.set_buttons()

    def set_buttons(self):
        if self.stage == "START":
            for player in self.players:
                trellis.pixels[player.location] = (0, 255, 0)
        elif self.stage == "ROLLING":
            for player in self.players:
                trellis.pixels[player.location] = (0, 0, 0)
        elif self.stage == "MOVING":
            trellis.pixels[self.current_player.location] = (255, 0, 0)
        elif self.stage == "END":
            trellis.pixels[self.non_active_player.location] = (0, 0, 0)
            trellis.pixels[self.current_player.location] = (0, 255, 0)


number_patterns = [
    ["*  ", " * ", "  *"],  # 0
    ["   ", " * ", "   "],  # 1
    ["*  ", "   ", "  *"],  # 2
    ["*  ", " * ", "  *"],  # 3
    ["* *", "   ", "* *"],  # 4
    ["* *", " * ", "* *"],  # 5
    ["***", "   ", "***"],  # 6
]


def display_digit(number, offset, color):
    time.sleep(0.1)
    bits = number_patterns[number]
    for row in range(3):
        for col in range(3):
            if bits[row][col] == " " or number == 0:
                trellis.pixels[col + offset, row] = (255, 255, 255)
            else:
                trellis.pixels[col + offset, row] = color


def display_number(numbers, color):
    display_digit(numbers[0], 0, color)
    display_digit(numbers[1], 5, color)


def animate_to(numbers, color=(255, 0, 0)):
    for _ in range(6):
        trellis.pixels.fill((0, 0, 0))
        display_number([random.randint(1, 6), random.randint(1, 6)], color)
        time.sleep(0.1)
    trellis.pixels.fill((0, 0, 0))
    display_number(numbers, color)


def roll(sides):
    return [random.randint(1, sides), random.randint(1, sides)]


previous_reading = [None, None, None]
bound = 4.0


d6 = 6
game = Game()
game.set_buttons()

while True:
    previous_reading = accelerometer.acceleration

    pressed = trellis.pressed_keys
    is_pressed = len(pressed) > 0 and pressed[0] == game.current_player.location

    if game.stage == "START" and (
        is_pressed or game.non_active_player.location in pressed
    ):
        game.active_player = 0 if pressed[0] == game.players[0].location else 1

    if is_pressed:
        game.next_stage()

    if is_pressed and game.stage == "ROLLING":
        animate_to(roll(d6))
        game.next_stage()

import time
from collections import namedtuple
import serial
import json
import subprocess
import sys

PORT_RIGHT = '/dev/tty.usbserial-SR0GK1A'
PORT_LEFT = '/dev/tty.usbserial-SR0UK1L'

Forward = namedtuple('Forward', 'speed')
Reverse = namedtuple('Reverse', 'speed')
Freewheel = object()
Brake = object()

def invert(channel):
    def new_channel(x):
        if isinstance(x, Forward):
            channel(Reverse(speed=x.speed))
        elif isinstance(x, Reverse):
            channel(Forward(speed=x.speed))
        else:
            channel(x)
    return new_channel

class MotorBoard:
    def __init__(self, port):
        self._connection = serial.Serial(port, baudrate=115200)
        # FIXME: ugliest hack of all time
        time.sleep(2)
        self.channels = (self._channel(0), self._channel(1))

    def __getitem__(self, index):
        return self.channels[index]

    def _channel(self, channel):
        def drive(value):
            self._connection.write((channel + 2,))
            if isinstance(value, Forward):
                self._connection.write((128 + int(value.speed),))
            if isinstance(value, Reverse):
                self._connection.write((128 - int(value.speed),))
            if value is Freewheel:
                self._connection.write((128,))
            if value is Brake:
                self._connection.write((2,))
        return drive

BOARD_LEFT = MotorBoard(PORT_LEFT)
BOARD_RIGHT = MotorBoard(PORT_RIGHT)

print('GOING')

proc = subprocess.Popen('./joystick',
                        stdout=subprocess.PIPE,
                        stderr=sys.stderr)

def set(channel, level):
    if level < -1:
        level = -1
    if level > 1:
        level = 1
    if level < 0:
        channel(Reverse(-level * 80))
    elif level > 0:
        channel(Forward(level * 80))
    else:
        channel(Freewheel)

BACK = invert(BOARD_LEFT[0])
FRONT_LEFT = invert(BOARD_RIGHT[1])
FRONT_RIGHT = BOARD_RIGHT[0]

for line in proc.stdout:
    (x, y, kill) = json.loads(line.decode('utf-8'))
    if kill:
        FRONT_LEFT(Brake)
        FRONT_RIGHT(Brake)
        BACK(Brake)
    else:
        xs = x / 32768
        ys = y / 32768
        print(xs, ys)
        set(FRONT_LEFT, ys)
        set(FRONT_RIGHT, ys)
        set(BACK, xs)

FRONT_LEFT(Brake)
FRONT_RIGHT(Brake)
BACK(Brake)


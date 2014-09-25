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
        print("Opening connection to {}".format(port))
        self._connection = serial.Serial(port, baudrate=115200, timeout=0.2)
        self._wait_for_connection()
        self.channels = (self._channel(0), self._channel(1))

    def _wait_for_connection(self):
        time.sleep(0.8)
        return # FIXME: horrible hax
        for i in range(20):
            print("    Reading firmware version...")
            if self._try_vers():
                return
        raise Exception("Cannot communicate with motor board on {}".format(self._connection.port))

    def _try_vers(self):
        self._connection.write(b'\x01')
        time.sleep(0.2)
        data = self._connection.readline()
        if data:
            print("Got FW vers: {}".format(data.strip()))
            return True
        else:
            return False

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

def map_joystick(value):
    # dead zone
    if -400 < value < 400:
        dead_value = 0
    else:
        dead_value = value
    mapped_value = dead_value / 32768
    return mapped_value * 0.4

for line in proc.stdout:
    (x, y, kill) = json.loads(line.decode('utf-8'))
    if kill:
        FRONT_LEFT(Brake)
        FRONT_RIGHT(Brake)
        BACK(Brake)
    else:
        xs = map_joystick(x)
        ys = map_joystick(-y)
        print(xs, ys)
        set(FRONT_LEFT, ys + xs)
        set(FRONT_RIGHT, ys - xs)
        set(BACK, -xs)

FRONT_LEFT(Brake)
FRONT_RIGHT(Brake)
BACK(Brake)


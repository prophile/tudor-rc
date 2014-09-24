import time
from collections import namedtuple
import serial

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
                self._connection.write((128 + value.speed,))
            if isinstance(value, Reverse):
                self._connection.write((128 - value.speed,))
            if value is Freewheel:
                self._connection.write((128,))
            if value is Brake:
                self._connection.write((2,))
        return drive

BOARD_LEFT = MotorBoard(PORT_LEFT)
BOARD_RIGHT = MotorBoard(PORT_RIGHT)

print('GOING')

BACK = invert(BOARD_LEFT[0])
FRONT_LEFT = invert(BOARD_RIGHT[1])
FRONT_RIGHT = BOARD_RIGHT[0]

FRONT_LEFT(Forward(30))
FRONT_RIGHT(Forward(30))
BACK(Brake)

time.sleep(3)

FRONT_LEFT(Brake)
FRONT_RIGHT(Brake)
BACK(Forward(30))

time.sleep(2)

BACK(Brake)


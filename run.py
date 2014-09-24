import time
from collections import namedtuple
import serial

PORT_LEFT = '/dev/tty.usbserial-SR0GK1A'
PORT_RIGHT = '/dev/tty.usbserial-SR0UK1L'

Forward = namedtuple('Forward', 'speed')
Reverse = namedtuple('Reverse', 'speed')
Freewheel = object()
Brake = object()

class MotorBoard:
    def __init__(self, port):
        self._connection = serial.Serial(port, baudrate=1000000)
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

BOARD_LEFT[0](Forward(100))
time.sleep(10)


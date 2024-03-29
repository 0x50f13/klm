# This file is part of pyklm project.
#
#  Copyright 2022-2023 by Polar <toddot@protonmail.com>
#
#  Licensed under GNU General Public License 3.0 or later.
#  Some rights reserved. See COPYING, AUTHORS.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

import socket
import os
from enum import Enum

from pyklm.rgb import RGB
from pyklm.util import byteargs
from pyklm.mode import KeyboardMode


class KLMError(Exception):
    pass


class KLMResultStatus(Enum):
    RESULT_OK = 0x0
    RESULT_ERROR = 0x1
    RESULT_BAD_REQUEST = 0x2
    RESULT_DATA = 0x3

    @staticmethod
    @byteargs
    def from_byte(byte: int):
        if byte == 0x0:
            return KLMResultStatus.RESULT_OK
        elif byte == 0x1:
            return KLMResultStatus.RESULT_ERROR
        elif byte == 0x2:
            return KLMResultStatus.RESULT_BAD_REQUEST
        elif byte == 0x3:
            return KLMResultStatus.RESULT_DATA
        else:
            raise ValueError(f"Bad status code: {byte}")


class KLMResult:
    """
     Stores result and associated data if needed
    """

    def __init__(self):
        self.status = KLMResultStatus.RESULT_ERROR
        self.data = list()

    def __repr__(self):
        return f"<KLMResult: {self.status}, {len(self.data)} bytes of data>"

    @classmethod
    def receive_from(cls, sock):
        status_byte = sock.recv(1)[0]
        status = KLMResultStatus.from_byte(status_byte)
        if status != KLMResultStatus.RESULT_DATA:
            result = cls()
            result.status = status
            return result
        size_byte = sock.recv(1)[0]
        if size_byte == 0:
            raise ValueError(f"Unexpected response size: {size_byte}")
        data = sock.recv(size_byte)
        result = cls()
        result.status = KLMResultStatus.RESULT_DATA
        result.data = data
        return result


class KLMConnection:
    """
     Stores data required to interact with klmd
    """

    def __init__(self):
        self.staged = bytearray()
        self.size = 0

    def set_color(self, color: RGB):
        """
         Stages set color command.

         :param color: RGB: color to set
        """
        self.staged += bytearray([0x01])
        self.staged += color.to_bytearray()
        self.size += 4

    @byteargs
    def set_brightness(self, brightness: int):
        """
         Stages set brightness command.

         :param brightness: int: brightness level(0-255)
        """
        self.staged += bytearray([0x03])
        self.staged += bytearray([brightness])
        self.size += 2

    def set_mode(self, mode: KeyboardMode):
        """
         Stages command to setting mode

         :param mode: KeyboardMode: mode to use
        """
        self.staged += bytearray([0x05])
        self.staged += bytearray([mode.value])
        self.size += 2

    def add_color(self, color: RGB):
        """
         Stages add color command.

         :param color: RGB: color to add
        """
        self.staged += bytearray([0x02])
        self.staged += color.to_bytearray()
        self.size += 4

    @byteargs
    def set_speed(self, speed: int):
        """
         Sets speed of color shift or keyboard breathe.

         :param: speed: int: speed in a byte range(0-255)
        """
        self.staged += bytearray([0x04])
        self.staged += bytearray([speed])
        self.size += 2

    def set_power(self, power: bool):
        self.staged += bytearray([0x07])
        if power:
            self.staged += bytearray([0x01])
        else:
            self.staged += bytearray([0x00])
        self.size += 2

    def get_modes(self):
        self.staged += bytearray([0x09])
        self.size += 1

    def toggle(self):
        """
         Toggles power of keyboard.
        """
        self.staged += bytearray([0x08])
        self.size += 1

    def commit(self) -> KLMResult:
        """
         Commits staged changes to daemon.

         :return: KLMResult: result of communication.
        """
        if not os.path.exists("/var/run/klmd.sock"):
            raise KLMError("No sock found. Is daemon running?")
        if self.size == 0:
            raise KLMError("No commands staged. If you have stage commands before this may be a bug.")
        if self.size > 255:
            raise KLMError(f"Size of requst {self.size} is too big. Try reducing amount of commands.")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/var/run/klmd.sock")
        sock.send(bytearray([self.size]))
        sock.send(self.staged)
        result = KLMResult.receive_from(sock)
        sock.close()
        return result

    def reset(self):
        """
         Removes staged commands from connection.
        """
        self.staged = bytearray([])
        self.size = 0

"""
MIT License

Copyright (c) 2019 UCSF Hu Lab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import sys
from pathlib import Path
import datetime
from array import array
import struct
from typing import List
from typing import Any
from . import constant


class VITALBINARY:
    Label = ""                          # 16 char
    Uom = ""                            # 8 char
    Unit = ""                           # 8 char
    Bed = ""                            # 4 char
    Year = 0                            # 32-bit int
    Month = 0                           # 32-bit int
    Day = 0                             # 32-bit int
    Hour = 0                            # 32-bit int
    Minute = 0                          # 32-bit int
    Second = 0.0                        # double 8-byte

    def __init__(self, Label: str = "", Uom: str = "", Unit: str = "", Bed: str = "",
                 Year: int = 0, Month: int = 0, Day: int = 0,
                 Hour: int = 0, Minute: int = 0, Second: float = 0.0):
        self.Label = Label
        self.Uom = Uom
        self.Unit = Unit
        self.Bed = Bed
        self.Year = Year
        self.Month = Month
        self.Day = Day
        self.Hour = Hour
        self.Minute = Minute
        self.Second = Second

    def setValue(self, Label: str = "", Uom: str = "", Unit: str = "", Bed: str = "",
                 Year: int = 0, Month: int = 0, Day: int = 0,
                 Hour: int = 0, Minute: int = 0, Second: float = 0.0):
        self.Label = Label
        self.Uom = Uom
        self.Unit = Unit
        self.Bed = Bed
        self.Year = Year
        self.Month = Month
        self.Day = Day
        self.Hour = Hour
        self.Minute = Minute
        self.Second = Second


class VitalFileError(BaseException):
    def __init__(self, message):
        self.message = message


class VitalFile:
    f = None
    filename = ""
    header = None
    numSamplesInFile = 0    # filesize in byte

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.header = None
        self.numSamplesInFile = 0

    def open(self):
        if self.mode == "r":
            try:
                fileSize = os.path.getsize(self.filename)
                self.numSamplesInFile = int((fileSize - constant.VITALHEADER_SIZE) / (constant.DOUBLE_SIZE * 4))
                self.f = open(self.filename, "rb")
            except:
                self.f = None
                raise VitalFileError("File not found!")
        elif self.mode == "r+":
            try:
                fileSize = os.path.getsize(self.filename)
                self.numSamplesInFile = int((fileSize - constant.VITALHEADER_SIZE) / (constant.DOUBLE_SIZE * 4))
                self.f = open(self.filename, "rb+")
            except:
                self.f = None
                raise VitalFileError("File not found!")
        elif self.mode == "w":
            try:
                outfile = Path(self.filename)
                if not outfile.exists():
                    self.numSamplesInFile = 0
                    self.f = open(self.filename, "wb")
                else:
                    self.f = None
                    raise VitalFileError("File exist already!")
            except:
                self.f = None
                raise VitalFileError("Cannot open file!")

    def setHeader(self, header: VITALBINARY):
        self.header = header

    def _readStr(self, size: int):
        buf = self.f.read(size)
        # remove the padded '\0'
        s = buf.decode("utf-8").rstrip('\0')
        return s

    def _writeStr(self, s: str, size: int):
        format_str = "{0}s".format(size)
        self.f.write(struct.pack(format_str, s.encode('utf-8')))

    def readHeader(self):
        # set to beginning of file
        self.f.seek(0, 0)
        self.header = VITALBINARY()
        self.header.Label = self._readStr(16)
        self.header.Uom = self._readStr(8)
        self.header.Unit = self._readStr(8)
        self.header.Bed = self._readStr(4)
        self.header.Year, self.header.Month, self.header.Day, self.header.Hour, self.header.Minute = struct.unpack("iiiii", self.f.read(constant.INT32_SIZE * 5))
        self.header.Second = struct.unpack("d", self.f.read(constant.DOUBLE_SIZE))[0]

    def writeHeader(self):
        # set to beginning of file
        self.f.seek(0, 0)
        self._writeStr(self.header.Label, 16)
        self._writeStr(self.header.Uom, 8)
        self._writeStr(self.header.Unit, 8)
        self._writeStr(self.header.Bed, 4)
        self.f.write(struct.pack("i", self.header.Year))
        self.f.write(struct.pack("i", self.header.Month))
        self.f.write(struct.pack("i", self.header.Day))
        self.f.write(struct.pack("i", self.header.Hour))
        self.f.write(struct.pack("i", self.header.Minute))
        self.f.write(struct.pack("d", self.header.Second))

    def getNumSamples(self):
        (self.fileSize - constant.VITALHEADER_SIZE) / (constant.DOUBLE_SIZE * 4)

    # return value, offset, low, high
    def readVitalData(self):
        value, offset, low, high = struct.unpack("dddd", self.f.read(constant.DOUBLE_SIZE * 4))
        return value, offset, low, high

    # return array of tuples of (value, offset, low, high)
    def readVitalDataBuf(self, numSamples):
        buf = self.f.read(constant.DOUBLE_SIZE * 4 * numSamples)
        trunkSize = constant.DOUBLE_SIZE * 4
        curr = 0
        arr = []
        while curr < len(buf):
            mv = memoryview(buf[curr:curr + trunkSize])
            t = struct.unpack("dddd", mv)
            arr.append(t)
            curr += trunkSize
        return arr

    def writeVitalData(self, value: float, offset: float, low: float, high: float):
        # set to end of file
        self.f.seek(0, 2)
        self.f.write(struct.pack("d", value))
        self.f.write(struct.pack("d", offset))
        self.f.write(struct.pack("d", low))
        self.f.write(struct.pack("d", high))
        self.numSamplesInFile += 1

    def close(self):
        # print("Close")
        if self.f is not None:
            self.f.flush()
            self.f.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

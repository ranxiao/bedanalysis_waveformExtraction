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
from .fixsampling import fixsamplingarr


class CFWBINARY:
    magic = [b'C', b'F', b'W', b'B']    # 4 characters "CFWB"
    Version = constant.CFWB_VERSION     # 32-bit int
    secsPerTick = 0.0                   # double 8-byte
    Year = 0                            # 32-bit int
    Month = 0                           # 32-bit int
    Day = 0                             # 32-bit int
    Hour = 0                            # 32-bit int
    Minute = 0                          # 32-bit int
    Second = 0.0                        # double 8-byte
    trigger = 0.0                       # double 8-byte
    NChannels = 0                       # 32-bit int
    SamplesPerChannel = 0               # 32-bit int
    TimeChannel = 0                     # 32-bit int
    DataFormat = 0                      # 32-bit int

    def __init__(self, secsPerTick: float = 0.0, Year: int = 0, Month: int = 0, Day: int = 0,
                 Hour: int = 0, Minute: int = 0, Second: float = 0.0, trigger: float = 0.0,
                 NChannels: int = 0, SamplesPerChannel: int = 0, TimeChannel: int = 0,
                 DataFormat: int = constant.FORMAT_SHORT):
        self.secsPerTick = secsPerTick
        self.Year = Year
        self.Month = Month
        self.Day = Day
        self.Hour = Hour
        self.Minute = Minute
        self.Second = Second
        self.trigger = trigger
        self.NChannels = NChannels
        self.SamplesPerChannel = SamplesPerChannel
        self.TimeChannel = TimeChannel
        self.DataFormat = DataFormat

    def setValue(self, secsPerTick: float = 0.0, Year: int = 0, Month: int = 0, Day: int = 0,
                 Hour: int = 0, Minute: int = 0, Second: float = 0.0, trigger: float = 0.0,
                 NChannels: int = 0, SamplesPerChannel: int = 0, TimeChannel: int = 0,
                 DataFormat: int = constant.FORMAT_SHORT):
        self.secsPerTick = secsPerTick
        self.Year = Year
        self.Month = Month
        self.Day = Day
        self.Hour = Hour
        self.Minute = Minute
        self.Second = Second
        self.trigger = trigger
        self.NChannels = NChannels
        self.SamplesPerChannel = SamplesPerChannel
        self.TimeChannel = TimeChannel
        self.DataFormat = DataFormat


class CFWBCHANNEL:
    Title = ""              # 32 characters long
    Units = ""              # 32 characters long
    scale = 0.0             # double 8-byte
    offset = 0.0            # double 8-byte
    RangeHigh = 0.0         # double 8-byte
    RangeLow = 0.0          # double 8-byte

    def __init__(self, Title: str = "", Units: str = "", scale: float = 0.0, offset: offset = 0.0,
                 RangeHigh: float = 0.0, RangeLow: float = 0.0):
        self.Title = Title
        self.Units = Units
        self.scale = scale
        self.offset = offset
        self.RangeHigh = RangeHigh
        self.RangeLow = RangeLow

    def setValue(self, Title: str = "", Units: str = "", scale: float = 0.0, offset: offset = 0.0,
                 RangeHigh: float = 0.0, RangeLow: float = 0.0):
        self.Title = Title
        self.Units = Units
        self.scale = scale
        self.offset = offset
        self.RangeHigh = RangeHigh
        self.RangeLow = RangeLow


class BinFileError(BaseException):
    def __init__(self, message):
        self.message = message


class BinFile:
    f = None
    filename = ""
    header = None
    channels = []

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.header = None
        self.channels = []

    def open(self):
        if self.mode == "r":
            try:
                self.f = open(self.filename, "rb")
            except:
                self.f = None
                raise BinFileError("File not found!")
        elif self.mode == "r+":
            try:
                self.f = open(self.filename, "rb+")
            except:
                self.f = None
                raise BinFileError("File not found!")
        elif self.mode == "w":
            try:
                outfile = Path(self.filename)
                if not outfile.exists():
                    self.f = open(self.filename, "wb")
                else:
                    self.f = None
                    raise BinFileError("File exist already!")
            except:
                self.f = None
                raise BinFileError("Cannot open file!")

    def setHeader(self, header: CFWBINARY):
        self.header = header

    def addChannel(self, channelDef: CFWBCHANNEL):
        self.channels.append(channelDef)

    def readHeader(self):
        self.header = CFWBINARY()
        self.header.magic[0], self.header.magic[1], self.header.magic[2], self.header.magic[3] = struct.unpack("cccc", self.f.read(4))
        self.header.Version = struct.unpack("i", self.f.read(constant.INT32_SIZE))[0]
        self.header.secsPerTick = struct.unpack("d", self.f.read(constant.DOUBLE_SIZE))[0]
        self.header.Year, self.header.Month, self.header.Day, self.header.Hour, self.header.Minute = struct.unpack("iiiii", self.f.read(constant.INT32_SIZE * 5))
        self.header.Second, self.header.trigger = struct.unpack("dd", self.f.read(constant.DOUBLE_SIZE * 2))
        self.header.NChannels, self.header.SamplesPerChannel, self.header.TimeChannel, self.header.DataFormat = struct.unpack("iiii", self.f.read(constant.INT32_SIZE * 4))
        self.channels = []
        for i in range(self.header.NChannels):
            buf = self.f.read(32)
            label = buf.decode("utf-8").rstrip('\0')
            buf = self.f.read(32)
            uom = buf.decode("utf-8").rstrip('\0')
            scale, offset, rangeHigh, rangeLow = struct.unpack("dddd", self.f.read(constant.DOUBLE_SIZE * 4))
            channel = CFWBCHANNEL(label, uom, scale, offset, rangeHigh, rangeLow)
            self.channels.append(channel)

    def writeHeader(self):
        # set to beginning of file
        self.f.seek(0, 0)
        self.f.write(struct.pack("cccc", self.header.magic[0], self.header.magic[1], self.header.magic[2], self.header.magic[3]))
        self.f.write(struct.pack("i", self.header.Version))
        self.f.write(struct.pack("d", self.header.secsPerTick))
        self.f.write(struct.pack("i", self.header.Year))
        self.f.write(struct.pack("i", self.header.Month))
        self.f.write(struct.pack("i", self.header.Day))
        self.f.write(struct.pack("i", self.header.Hour))
        self.f.write(struct.pack("i", self.header.Minute))
        self.f.write(struct.pack("d", self.header.Second))
        self.f.write(struct.pack("d", self.header.trigger))
        self.f.write(struct.pack("i", self.header.NChannels))
        self.f.write(struct.pack("i", self.header.SamplesPerChannel))
        self.f.write(struct.pack("i", self.header.TimeChannel))
        self.f.write(struct.pack("i", self.header.DataFormat))
        # Write out 'NChannels' of channel headers
        if (self.channels is not None) and (len(self.channels) > 0):
            for i in range(len(self.channels)):
                channel = self.channels[i]
                self.f.write(struct.pack("32s", channel.Title.encode('utf-8')))
                self.f.write(struct.pack("32s", channel.Units.encode('utf-8')))
                self.f.write(struct.pack("d", channel.scale))
                self.f.write(struct.pack("d", channel.offset))
                self.f.write(struct.pack("d", channel.RangeHigh))
                self.f.write(struct.pack("d", channel.RangeLow))


    def readChannelData(self, offset: float, length: float, useSecForOffset: bool, useSecForLength: bool, downSamplingRatio: float = 1.0, *, noDataScaling: bool = False):
        offsetSampleNum = int(offset / self.header.secsPerTick) if useSecForOffset else int(offset)
        lengthSampleNum = int(length / self.header.secsPerTick) if useSecForLength else int(length)
        if (self.header.DataFormat == constant.FORMAT_DOUBLE):
            sampleSize = constant.DOUBLE_SIZE
        elif (self.header.DataFormat == constant.FORMAT_FLOAT):
            sampleSize = constant.FLOAT_SIZE
        elif (self.header.DataFormat == constant.FORMAT_SHORT):
            sampleSize = constant.SHORT_SIZE
        # offset and lenght are 0, then read entire file
        if (offsetSampleNum == 0) and (lengthSampleNum == 0):
            lengthSampleNum = self.header.SamplesPerChannel
        # do not read over the end of file
        elif (lengthSampleNum + offsetSampleNum) > self.header.SamplesPerChannel:
            lengthSampleNum = self.header.SamplesPerChannel - offsetSampleNum
        # do not read anything if offset is bigger then total sample number
        elif offsetSampleNum > self.header.SamplesPerChannel:
            lengthSampleNum = 0
        self.f.seek(constant.CFWB_SIZE + constant.CHANNEL_SIZE * self.header.NChannels + offsetSampleNum * sampleSize * self.header.NChannels, 0)
        channelArr = []

        if noDataScaling:
            for i in range(0, self.header.NChannels):
                if self.header.DataFormat == constant.FORMAT_DOUBLE:
                    channelArr.append(array("d", (0,) * lengthSampleNum))
                elif self.header.DataFormat == constant.FORMAT_FLOAT:
                    channelArr.append(array("f", (0,) * lengthSampleNum))
                elif self.header.DataFormat == constant.FORMAT_SHORT:
                    channelArr.append(array("h", (0,) * lengthSampleNum))
            for x in range(0, lengthSampleNum):
                i = 0
                for c in channelArr:
                    if self.header.DataFormat == constant.FORMAT_DOUBLE:
                        c[x] = struct.unpack("d", self.f.read(constant.DOUBLE_SIZE))[0]
                    elif self.header.DataFormat == constant.FORMAT_FLOAT:
                        c[x] = struct.unpack("f", self.f.read(constant.FLOAT_SIZE))[0]
                    elif self.header.DataFormat == constant.FORMAT_SHORT:
                        c[x] = struct.unpack("h", self.f.read(constant.SHORT_SIZE))[0]
        else:
            for i in range(0, self.header.NChannels):
                channelArr.append(array("d", (0,) * lengthSampleNum))

            for x in range(0, lengthSampleNum):
                i = 0
                for c in channelArr:
                    if self.header.DataFormat == constant.FORMAT_DOUBLE:
                        c[x] = struct.unpack("d", self.f.read(constant.DOUBLE_SIZE))[0]
                    elif self.header.DataFormat == constant.FORMAT_FLOAT:
                        c[x] = struct.unpack("f", self.f.read(constant.FLOAT_SIZE))[0]
                    elif self.header.DataFormat == constant.FORMAT_SHORT:
                        v = struct.unpack("h", self.f.read(constant.SHORT_SIZE))[0]
                        if v in constant.GAP_SHORT_VALUES:
                            c[x] = constant.MIN_DOUBLE_VALUE
                        else:
                            c[x] = self.channels[i].scale * (v + self.channels[i].offset)
                    i += 1
            if downSamplingRatio != 1.0:
                channelArr = fixsamplingarr(channelArr, downSamplingRatio)
        
        return channelArr

    def writeChannelData(self, chanData: List[List[Any]], fs: int = 0, gapInSecs: int = 0):
        # 2 means the end of file
        self.f.seek(0, 2)
        numSamplesWritten = 0
        numChannels = len(chanData)
        if gapInSecs > 0:
            numSamples = gapInSecs * fs
            numSamplesWritten += numSamples
            for j in range(numSamples):
                for i in range(numChannels):
                    if self.header.DataFormat == constant.FORMAT_SHORT:
                        d = constant.MIN_SHORT_VALUE
                        self.f.write(struct.pack("h", d))
                    elif self.header.DataFormat == constant.FORMAT_DOUBLE:
                        d = constant.MIN_DOUBLE_VALUE
                        self.f.write(struct.pack("d", d))
                    elif self.header.DataFormat == constant.FORMAT_FLOAT:
                        d = constant.MIN_FLOAT_VALUE
                        self.f.write(struct.pack("f", d))
        overlappedSamples = (-1 * gapInSecs * fs) if gapInSecs < 0 else 0
        len_chanData = 0
        if len(chanData) > 0:
            len_chanData = len(chanData[0])
        numSamplesWritten += max(len_chanData - overlappedSamples, 0)
        for j in range(len_chanData):
            if j < overlappedSamples:
                continue
            for i in range(len(chanData)):
                # bug fix, prevent idx out of range
                out_of_range = j > (len(chanData[i]) - 1)
                if self.header.DataFormat == constant.FORMAT_SHORT:
                    d = chanData[i][j] if not out_of_range else constant.MIN_SHORT_VALUE
                    self.f.write(struct.pack("h", d))
                elif self.header.DataFormat == constant.FORMAT_DOUBLE:
                    d = chanData[i][j] if not out_of_range else constant.MIN_DOUBLE_VALUE
                    self.f.write(struct.pack("d", d))
                elif self.header.DataFormat == constant.FORMAT_FLOAT:
                    d = chanData[i][j] if not out_of_range else constant.MIN_FLOAT_VALUE
                    self.f.write(struct.pack("f", d))
                else:
                    # raise exception
                    raise BinFileError("Unsupported array type!")
        return numSamplesWritten

    def updateSamplesPerChannel(self, numSamples: int, writeToFile: bool):
        self.header.SamplesPerChannel = numSamples
        if writeToFile:
            if self.mode == "w" or self.mode == "r+":
                self.f.seek(constant.N_SAMPLE_POSITION)
                self.f.write(struct.pack("i", numSamples))
                self.f.flush()

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

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
from vitalfilepy import VitalFile
from vitalfilepy import VITALBINARY


def test_vitalfilewriter():
    filename = "tmp_test_vitalfilewriter.vital"
    valueList = [80, 90, 85, 130, 135]
    offsetList = [0, 60, 12, 180, 360]
    lowList = [0, 0, 0, 0, 0]
    highList = [1000, 1000, 1000, 150, 150]
    # remove test file if exist
    try:
        outfile = Path(filename)
        if outfile.exists():
            outfile.unlink()
    except:
        # ignore error
        pass
    # dummy test for now
    assert(len(filename) > 0)
    with VitalFile(filename, "w") as f:
        header = VITALBINARY("HR", "Bpm", "T1ICU", "101", 2019, 3, 31, 8, 15, 30.0)
        f.setHeader(header)
        f.writeHeader()
        for i in range(0, 5):
            f.writeVitalData(valueList[i], offsetList[i], lowList[i], highList[i])
    with VitalFile(filename, "r") as f:
        f.readHeader()
        print("Start Date/Time: {0}/{1}/{2} {3}:{4}:{5:.0f}".format(f.header.Month, f.header.Day, f.header.Year, f.header.Hour, f.header.Minute, f.header.Second))
        assert(f.header.Label == "HR")
        assert(f.header.Uom == "Bpm")
        assert(f.header.Unit == "T1ICU")
        assert(f.header.Bed == "101")
        assert(f.header.Year == 2019)
        assert(f.header.Month == 3)
        assert(f.header.Day == 31)
        assert(f.header.Hour == 8)
        assert(f.header.Minute == 15)
        assert(f.header.Second == 30.0)
        for i in range(0, 5):
            value, offset, low, high = f.readVitalData()
            print("value, offset, low, high: {0}, {1}, {2}, {3}".format(value, offset, low, high))
            assert(value == valueList[i])
            assert(offset == offsetList[i])
            assert(low == lowList[i])
            assert(high == highList[i])
    # remove temporary file created
    try:
        outfile = Path(filename)
        if outfile.exists():
            outfile.unlink()
    except:
        # ignore error
        pass
    return

if __name__ == "__main__":
    # execute only if run as a script
    test_vitalfilewriter()

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


CFWB_VERSION = 1
CHANNEL_TITLE_LEN = 32
UNITS_LEN = 32
MAGIC_LEN = 4
SHORT_SIZE = 2
INT32_SIZE = 4
FLOAT_SIZE = 4
DOUBLE_SIZE = 8
FORMAT_DOUBLE = 1
FORMAT_FLOAT = 2
FORMAT_SHORT = 3
N_SAMPLE_POSITION = MAGIC_LEN + INT32_SIZE + DOUBLE_SIZE + 5 * INT32_SIZE + DOUBLE_SIZE + DOUBLE_SIZE + INT32_SIZE
CFWB_SIZE = MAGIC_LEN + INT32_SIZE + DOUBLE_SIZE + 5 * INT32_SIZE + DOUBLE_SIZE + DOUBLE_SIZE + 4 * INT32_SIZE
CHANNEL_SIZE = CHANNEL_TITLE_LEN + UNITS_LEN + 4 * DOUBLE_SIZE
GAP_SHORT_VALUES = [-32767, -32768]
MIN_SHORT_VALUE = -32767
MAX_SHORT_VALUE = 32767
MIN_DOUBLE_VALUE = -1.7e+308
MAX_DOUBLE_VALUE = 1.7e+308
MIN_FLOAT_VALUE = -3.4e+38
MAX_FLOAT_VALUE = 3.4e+38

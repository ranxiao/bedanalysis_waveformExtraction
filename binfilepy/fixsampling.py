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

import numpy as np
# to fix error in pyinstaller, we need to import additional types for numpy
import numpy.core._dtype_ctypes
from array import array
from typing import List


def fixsamplingarr(arr: array, downSamplingRatio: float):
    x = np.array(list(range(0, len(arr))))
    y = np.array(arr)
    step = 1.0 / downSamplingRatio      # samplesPerSec / targetSamplesPerSec
    new_x = []
    for u in np.arange(0, len(arr), step):
        new_x.append(u)
    '''
    fill_value = (y[0], y[len(y) - 1])
    f = interpolate.interp1d(x, y, bounds_error=False, fill_value=fill_value)
    new_y = f(new_x)
    '''
    new_y = np.interp(new_x, x, y)
    return array('h', new_y.astype(int).tolist())

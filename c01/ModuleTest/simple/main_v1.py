#!/usr/bin/env python

import sys
# this is default setting
sys.path.append(".")

from utils.class_utils import *

encoder = Encoder()
decoder = Decoder()

print(encoder.encode('abcde'))
print(decoder.decode('edcba'))

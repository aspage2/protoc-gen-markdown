#!/usr/bin/env python

import sys

data = sys.stdin.buffer.read()
with open("raw/data", "wb") as f:
    f.write(data)

#!/usr/bin/env python

import sys

i = 0
while True:
    line = sys.stdin.readline().rstrip("\n")
    if not line: break
    sys.stdout.write("N")
    sys.stdout.write(str(i))
    sys.stdout.write(": ")
    sys.stdout.write(line)
    sys.stdout.write("\n")
    sys.stdout.flush()
    i += 1

#!/usr/bin/env python

import imp
import sys

for pkg in sys.argv[1:]:
    try:
        pkginfo = imp.find_package(pkg)
        pkgpath = pkginfo[1]
    except ImportError:
        pkginfo = None




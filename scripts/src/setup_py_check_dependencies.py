#!/usr/bin/env python

import imp
import pkgutil
import sys

from os.path import dirname

"""
Usage: set_py_check_dependencies [MODULENAME]...

For each MODULENAME, print a line indicating whether the respective
module is found and loadable.
"""

all_ok = True
install = []
damaged = []

for pkg in sys.argv[1:]:
        package = pkgutil.get_loader(pkg)
        print(pkg, end=" ")
        sys.stdout.flush()
        if not package:
            print("NOT FOUND.")
            all_ok = False
            install.append(pkg)
        else:
            f = dirname(package.get_filename())
            print("FOUND and ", end="")
            sys.stdout.flush()
            try:
                __import__(pkg) 
                print("LOADABLE ", end="")
            except ImportError:
                print("NOT LOADABLE ", end="")
                all_ok = False
                damaged.append(pkg)

            print("({})".format(f))

if install:
    print("#>## Install the following python packages: {}".format(", ".join(reinstall)))
    print("#> ")

if damaged:
    print("#>## The following python packages threw an ERROR DURING LOADING:")
    print("#>## ")
    print("#>##     {}",', '.join(damaged))
    print("#>## ")
    print("#>## This may be due to the package itself or one of its dependencies")
    print("#>## Load them using `import ` in an interactive python session")
    print("#>## and check the error messages.")
    print("#> ")

if all_ok: sys.exit(0)
if not all_ok: sys.exit(1)


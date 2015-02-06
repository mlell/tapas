#!/usr/bin/env python

from docopt import docopt
import sys
import re

help=\
"""Usage: parse-configuration.py CONFIG_FILE

Reads in CONFIG_FILE and outputs code sourceable by bash. The config
file must be of following format:

variable1 = Values for variable 1
variable2 = etc...
"""

def main(argv):
    args = docopt(doc=help, argv=argv[1:])
    filename = args["CONFIG_FILE"]

    with open(filename, "rt") as ifd:
        content = [line.split("=",1) for line in ifd]

    content = [(a.strip(), b.strip()) for a,b in content]

    content = [(e,x[0],x[1]) for e,x in enumerate(content)]
    print(content)
    content = [(sanitize_lhs(a,e), sanitize_rhs(b)) 
                for e,a,b in content]
    for l in content:
        print("{}={}".format(*l))

def sanitize_lhs(string,line):
    illegal_character = re.search("[^a-zA-Z0-9_]", string)
    if illegal_character:
        raise ValueError("Illegal variable name in input line {}: {}"
            .format(line,string))
    return string


#    return re.sub("[^a-zA-Z0-9_]","_",string)

def sanitize_rhs(string):
    s = string.replace("'", "'\"'\"'")
    return "'"+s+"'"


a = re.search("[a-z]","0000000000")
print(a)

if __name__ == "__main__":
    main(sys.argv)


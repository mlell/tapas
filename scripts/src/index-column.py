#!/usr/bin/env python

import sys
from docopt import docopt
from tempfile import TemporaryFile

help="""
    Usage: index-column.py [options] 
    
Adds an index column to the input file. If --inplace is not specified,
standard input is read and the result is written to standard output.
If --inplace is specified, the given file will be modified.

Options:
    --colname NAME, -c NAME  [default: index]
                             Which column name the added column will have
                             
    --no-colname             Suppresses the printing of a column name

    --inplace FILE, -i FILE  The specified file will be modified in place
                             (using a temporary file) instead of reading
                             from standard input and printing to standard 
                             output

    --start I                [default: 0] 
                             first index to be printed.

    --sep S                  [default: \\t] Character to split columns

    --skip N                 [default: 0] Prints the first N lines as-is

    --prefix X               Prepend a string to the index

"""
def main(argv):
    # Assign command line arguments to variables
    args=docopt(help, argv[1:])

    colname = args["--colname"]
    if args["--no-colname"]: 
        colname = None
    start = int(args["--start"])
    sep = args["--sep"]
    skip = int(args["--skip"])
    inplace = args["--inplace"]
    prefix = args["--prefix"]
    if not prefix:
        prefix = ""

    if sep == "\\t" : sep = "\t"

    # If in-place file replacement is requested
    if inplace:
        with TemporaryFile("w+t") as tmp:
            with open(inplace,"rt") as ifd:
                for l in ifd:
                    tmp.write(l)

            tmp.seek(0)
            with open(inplace,"wt") as ofd:
                add_index(tmp, ofd, start, skip, sep, colname, prefix)

    # If normal standard input to standard output piping is requested
    else:
        add_index(sys.stdin, sys.stdout,start,skip,sep,colname, prefix)


    
def add_index(it_in, ofd, start, skip , sep, colname, prefix):
    i = start - skip
    if colname: 
        i -= 1
    try:
        while True:
            line = next(it_in)
            if i == start - 1 and colname:
                line = sep.join([colname,line])
            elif i >= start:
                line = sep.join([prefix+str(i), line])

            i += 1
            print(line, end="", file=ofd)
            ofd.flush()
    except StopIteration:
        pass


if __name__ == "__main__": main(sys.argv)


# vim: tw=80


#!/usr/bin/env python

from __future__ import print_function
import sys
from docopt import docopt
from itertools import product

helpText=r"""
Usage: cross_tab.py [options] FILES...

Print all combinations of the input tables' rows. Empty lines or lines
containing only whitespace are ignored, unless explicitly allowed 
(see parameters.)

Options:
    --skip INT  [default: 0] 
                Skip this number of lines from the top of each 
                specified file.
    --head INT  [default: 0] 
                The specified files contain the specified number 
                of lines as header; don't print combinations of these but 
                print them only once at the beginning
    --sep CHAR  [Default: \t] 
                A character which separates the contents
                of the input files in the output columns
    --respect-empty
                Do not remove empty lines or lines containing only whitespace
                in the input files

Example:

    ── tab1 ──
    a   b
    1   3
    2   4
    ──────────

    ── tab2 ──
    X   
    a   
    b   

    ──────────
    
    Call: cross_tab --head 1 

    yields: 

    ──────────
    a   b   X
    1   3   a
    1   3   b
    2   4   a
    2   4   b
    ──────────

    Note how the empty lines in tab2 was ignored. Use --respect-empty to 
    change this behaviour.

"""


def main(argv):
    args = docopt(helpText)
    skip = int(args["--skip"])
    header= int(args["--head"])
    sep = "\t" if args["--sep"] == r"\t" else args["--sep"]
    respect = args["--respect-empty"]

    # Read in every file. input_lines will be of the following
    # format: [[file1_line1, file1_line2, ... ],
    #          [file2_line1, file2_line2, ... ], ... ]
    input_lines = []
    for file in args["FILES"]: 
        with open(file,"rt") as fd:
            lines = [l.rstrip("\n") for l in fd]
            if not respect:
                # Ignore empty lines
                lines = [l for l in lines if l.strip() != ""]
            input_lines.append(lines[skip:])
    
    if header > 0:
        for i in range(0,header):
            h = []
            for f in input_lines:
                h.append(f.pop(0))

            print(sep.join(h))

    for combination in product(*input_lines):
        print(sep.join(combination))


if __name__ == "__main__":main(sys.argv)




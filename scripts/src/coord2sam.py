#!/usr/bin/env python3

"""
Converts a set of artificial reads where the read mapping coordinates to
the reference are known to a SAM file which simulates successful mapping
of all the reads. This can be used to check the correct working of the 
mutation machinery via mapDamage. 
"""

import sys
import argparse
from textwrap import dedent
import pandas as pd

def main(argv):
    args = parseArgs(argv)

    # Print the SAM header
    with open(args.REFERENCE_FAI, 'r') as fd_fai:
        for l in fd_fai:
            l = l.split("\t")
            print("@SQ\tSN:{}\tLN:{}".format(l[0],l[1]))

    coords = pd.read_table(args.READ_COORDS, delim_whitespace=True)
    coords.set_index("name", inplace = True)

    # Additional SAM fields (see SAM Specification)
    flag  = 0 
    mapq  = 40  
    rnext = "*" 
    pnext = 0
    tlen  = 0

    with open(args.READ_FASTQ,'r') as fd_fastq:
        for qname, seq, qual in read_fastq_fields(l.rstrip() for l in fd_fastq):
            pos   = coords.loc[qname, 'start']
            rname = coords.loc[qname, 'record']
            cigar = str(len(seq))+"M"
            print("\t".join(str(s) for s in  
                [ qname , flag  , rname , pos , mapq , cigar
                , rnext , pnext , tlen  , seq , qual ])) 

    
def read_fastq_fields(iterable):
    """ Print out a list of triples (read name, nucleotide seq., quality string),
    given a list of text lines.
    >>> list(read_fastq_fields(
    ...          ["@read1","AAAA","+read1","FFFF","@read2","CCC","+","FFF"]))
    [('read1', 'AAAA', 'FFFF'), ('read2', 'CCC', 'FFF')]
    >>> list(read_fastq_fields(
    ...          ['@read1','AAAA','FFFF']))
    Traceback (most recent call last):
    ...
    ValueError: FASTQ line 3: File has not a number of lines divisible by 4
    >>> list(read_fastq_fields(
    ...          ['read1','AAAA','+', 'FFFF']))
    Traceback (most recent call last):
    ...
    ValueError: FASTQ line 1: Read name without leading '@'
    """
    stream = enumerate(iterable, start=1)

    while True:
        try:
            lineno, name = next(stream)
        except StopIteration: 
            break

        if not name.startswith("@"): 
            raise ValueError("FASTQ line {}: Read name without leading '@'"
                             .format(lineno))
        name = name[1:]

        try:
            lineno, seq  = next(stream)
            lineno, _    = next(stream)
            lineno, qual = next(stream)
            b = False
        except StopIteration:
            b = True # don't list StopIteration exception in traceback
        if b:
            raise ValueError(
                "FASTQ line {}: File has not a number of lines divisible by 4"
                .format(lineno)) 

        yield (name, seq, qual)

def parseArgs(argv):
    ap = argparse.ArgumentParser( description = __doc__ 
                                , formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("READ_COORDS", help=dedent(
    """A text table containing the true read positions. It must contain
       columns with the following names:
        * name:   the read name
        * record: the FASTA record of the reference the read is mapped to
        * start:  the 1-based base index of the reference where the first
                  base of the read is mapped to
    """))
    ap.add_argument("READ_FASTQ", help=dedent(
    """A FASTQ file which contains the nucleotide sequences and quality score 
    lines for each read"""))
    ap.add_argument("REFERENCE_FAI", help=dedent(
    """The .fai file of the reference genome. This usually has the same file 
    name as the reference genome's FASTA file, plus a .fai extension."""))


    return ap.parse_args(argv)


if __name__ == "__main__":
    main(sys.argv[1:])


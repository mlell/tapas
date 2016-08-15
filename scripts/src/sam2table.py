#!/usr/bin/env python

"""
Convert the most used SAM fields to a text table.

Prints the text table to standard output.

Examples: 
  Simple usage:        sam2table run23.sam > run23.tab
  Compressed input:    sam2table --gz run88.sam.gz > run23.tab
  Compress output:     sam2table run23.sam | gzip > run23.tab.gz

Output columns:
    qname:  Read name.
    flag:   Read flags.
    rname:  FASTA record name of reference where read was mapped onto.
    pos:    Base number on reference where read was mapped (1-based).
    mapq:   Mapping quality. -10×log10(Probability that mapping is wrong).
    cigar:  CIGAR string which indicates positions of base mismatches, 
            insertions, deletions in the read compared to its mapped
            reference region.

    See the SAM specification (http://samtools.github.io/hts-specs/SAMv1.pdf)
    for details.
"""

import sys
import argparse
import gzip

def main(argv):
    args = parseArgs(argv[1:])
    printSAMTable(args.SAMFILE, sys.stdout, isGzipped=args.gz)

def parseArgs(argv):
    p = argparse.ArgumentParser( description = __doc__ 
                               , formatter_class = argparse.RawTextHelpFormatter);
    p.add_argument('SAMFILE', help='Input SAM file')
    p.add_argument("--gz", action='store_true', help="The input is gzip'ed")
    return p.parse_args(args = argv)

def printSAMTable(filename, stream, isGzipped):
    samfields = [ 'qname','flag','rname'
                , 'pos','mapq','cigar' 
                ,'rnext','pnext','tlen'
                ]
    nSamfields = len(samfields)
    print("\t".join(samfields))
    if isGzipped:
        samfd = gzip.open(filename, 'rt')
    else:
        samfd = open(filename, 'r')
    try:

        for line in samfd:
            if line[0] == '@': 
                continue
            print("\t".join(line.split()[1:nSamfields]));

    finally:
        samfd.close()
        




if __name__ == "__main__":
    main(sys.argv)

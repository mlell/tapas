#!/usr/bin/env python

# @autor Moritz Lell
# @date 2015-Aug-25

import sys
import os.path
from docopt import docopt
from fasta_substring import FastaIndex, slice
import random as rnd
import tempfile as tmpf
import contextlib
import io
import subprocess as sp

help="""
Usage: uniform.py [options] MFASTA N L S [SEED]

Purpose
-------

Samples reads from the specified (multi-FASTA) file MFASTA. 
Read positions will be from random FASTA records of the file and 
will be uniformly distributed. 

Read lengths will be folded normally distributed. 
(i.e. length ~ abs(X), X being a normally distributed random 
variable)

If the randomly generated read length exceeds the length of the
input sequence, the whole input sequence is printed.

The MFASTA file needs to be indexed using samtools: 
`samtools faidx MFASTA`

Mandatory parameters
--------------------

MFASTA  A (multi-)FASTA file
N       Number of reads to generate
L       Minimum read length
S       Decay length: half of the generated reads are S bases longer
        than L
SEED    Seed to initialize the random number generator;
        same seed leads to same read mapping positions

Optional parameters
-------------------

--index FILE  Specify an alternative location for the FASTA index.

--quiet       Don't print a status line.

--only-coords  Only output read coordinates, do not extract
               corresponding nucleotide strings
"""

# Files in this list will be deleted at the program end
TMP_FILES=[]

def main(argv): 
    args = docopt(help, argv[1:])
     
    filename = args["MFASTA"]
    nreads = int(args["N"])
    rlen_min = int(args["L"])
    rlen_decay = int(args["S"])
    seed = args["SEED"]

    index_name = args["--index"]
    if not index_name: index_name = args["MFASTA"]+".fai"

    if not os.path.isfile(index_name):
        raise Exception("Index file not found. Execute "+
        "'samtools faidx' on FASTA file first.")

    only_coords = args['--only-coords']

    try:
        with open(index_name,"rt") as index_fd:
            index = FastaIndex(index_fd)

        # Rough validity check of input MFASTA
        with open(filename,"rt") as fd:
            while True:
                l = fd.readline()
                if not l: break

                l = l.strip()
                if l and not l.startswith(">"):
                    print("The input file is not a valid FASTA"+
                            "file!",file=sys.stderr)
                    sys.exit(1)
                else: 
                    # Line starts with >: Check ok, continue program
                    break 

        # Set seed of random number generator
        if seed:
            rnd.seed(seed)


        # Print header
        print("record\tstart\tend"+
                ("\tread" if not only_coords else ""))
        n_done = 0
        statusLine(80,n_done,nreads)
        with open(filename,"rt") as fd:

            # Get list of record names
            recordnames = list(index.entries.keys())

            # Extract sequences out of the MFASTA file at random
            for i in range(0,nreads):

                # Randomly choose record
                record = rnd.choice(recordnames)
                indexEntry = index.entries[record]
                len_record = indexEntry.length_char

                # Randomly choose sequence length 
                # But never generate 0
                rlen = int(rnd.expovariate(1/rlen_decay))+rlen_min
                if rlen > len_record:
                    rlen = len_record
                # Random beginning position ~ 
                #    [1 .. (record length - read length)]
                # the value of the argument is never reached
                # i.e randrange(1) returns values of range {0}
                #     randrange(2) returns values of range {0,1}
                start = rnd.randrange(1,len_record-rlen+2)
                # Calculate end of region to extract, length is inclusive
                # start = 1, len = 1 => end base = 1
                # start = 1, len = 2 => end base = 2 ...
                end = start + rlen - 1

                if not only_coords:
                    # Get the nucleotides for the chosen coordinates
                    # Note that slice expects 0-based indices, whereas the
                    # output will be 1-based, according to SAM
                    # specification.
                    read = slice(fd, index, record, start-1, rlen)
                    print("\t".join([str(s) for s in [record,start,end,read]]))

                else:
                    print("\t".join([str(s) for s in [record,start,end]]))

                n_done += 1

                if n_done % 100 == 0: 
                    statusLine(80,n_done,nreads)
            print("",file=sys.stderr)
    finally:
        # Delete the temporary files
        for f in TMP_FILES:
            os.unlink(f)


def statusMsg(msg,**kwargs):
    print(msg,file=sys.stderr,**kwargs)

def statusLine(width, now, end=100):
    msg = "{}/{}".format(now,end)
    barwidth = width - len(msg) - 3 # 2: [ and ], 1 space
    ratio = now / end
    nfull = round(ratio * barwidth)
    nempty = barwidth - nfull
    sys.stderr.write("["+("="*nfull)+(" "*nempty)+"] "+msg)
    sys.stderr.write("\r"*width)
    sys.stderr.flush()



if __name__ == "__main__": main(sys.argv)



# vim: tw=70
#hum=/raid6/mlell/pub/genome/homo
#./uniform.py --index ${hum}.fa.idx --linearized ${hum}.lin.fa 100 40 2 > test_old

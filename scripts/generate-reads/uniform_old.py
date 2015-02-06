#!/usr/bin/env python

# @autor Moritz Lell
# @date 2015-Aug-25

import sys
import os.path
from docopt import docopt
from fastareader import FASTA
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

Dependencies
------------

If the `index` switch is not used, this script needs to execute 
the `fasta_record_index` tool which should be available in the same
directory as this script. 


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

--index FILE
        The MFASTA index is not created but shall be read in from 
        the file FILE. It must be of the following format:

        head 0
        data 10
        len 18
        ...
        end 340

        The integer values denotes offsets in the MFASTA file in
        bytes as returned by the C `ftell` function. 'head' denotes
        an offset of a ">" character (FASTA record head). 'data'
        denotes an offset of the first nucleotide after a FASTA
        head. 'len' is the character count of the current data section
        and 'end' is followed by the offset of the file end.

--linearized
        The input MFASTA file is already linearized, so don't perform
        this step again. A FASTA file is linearized if it is of the 
        following form:

        >head section 1
        BASES_WITHOUT_LINEBREAK_OR_WHITESPACE
        >possibly another head section
        BASES_WITHOUT_LINEBREAK_OR_WHITESPACE
        ...

--temp-dir DIRECTORY  [Default: .]
        Specify the directory which is to be used for the output of
        the linearizing and indexing step. Default is the current
        directory. 

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

    index = args["--index"]
    linearized = args["--linearized"]
    temp_dir = args["--temp-dir"]

    try:
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

        # Linearize the source MFASTA file, if nessecary
        if not linearized:
            statusMsg("Linearizing input file...")
            lin_file = os.path.join(temp_dir,filename+".lin.tmp")
            TMP_FILES.append(lin_file)
            call_linearizer(filename,lin_file)
            filename = lin_file

        if not index: 
            statusMsg("Indexing input file...")
            # Do not load index from file, but invoke indexer.
            indexText = call_indexer(filename).decode()
            index_fd = io.StringIO(indexText)
        else:
            # Load FASTA index from file
            index_fd = open(index,"rt")


        # Print header
        print("record\tstart\tend\tread")

        with open(filename,"rt") as fd:
            fasta = FASTA(fd)
            with index_fd:
                fasta.readIndex(index_fd)

            # Get list of record names
            recordnames = fasta.FASTARecordNames()

            # Extract sequences out of the MFASTA file at random
            for i in range(0,nreads):
                # Randomly choose record
                no_records = len(fasta.pos_head)
                record = rnd.randrange(no_records)
                len_record = fasta.len_data[record]

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

                # Get the nucleotides for the chosen coordinates
                # Note that the positions in the SAM standard are 1-based
                # i.e. first base has index 1
                read = fasta.slice(record, start, rlen)

                rn = recordnames[record]

                print("\t".join([str(s) for s in [rn,start,end,read]]))
    finally:
        # Delete the temporary files
        for f in TMP_FILES:
            os.unlink(f)


def call_indexer(fasta_filename):
    scd = get_script_directory()
    index = sp.check_output(
            [os.path.join(scd,"fasta_record_index"), fasta_filename])
    return index

def call_linearizer(input_file, output_file):
    """ Call linearize_fasta on input_file and write the result
    to output_file. Error if the output file exists already."""
    scd = get_script_directory()
    with open(output_file,"xt") as ofd:
        sp.check_call([os.path.join(scd,"linearize_fasta"),
            input_file], stdout = ofd)

def get_script_directory():
    return os.path.dirname(os.path.realpath(__file__))

def statusMsg(msg,**kwargs):
    print(msg,file=sys.stderr,**kwargs)





if __name__ == "__main__": main(sys.argv)



# vim: tw=70


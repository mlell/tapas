#!/usr/bin/env python3
# Intersperse a file with nucleotide sequences and a file with
# Quality scores to form a FASTQ-File
# Input files must have raw format: Just lines of Text are 
# interspersed, NO FASTA-PARSING IS DONE
#
# Author: Moritz Lell 2015-Feb-13

from argparse import ArgumentParser
import sys

parser= ArgumentParser(description="Generate FASTQ File from Nucleotide Sequence and Quality Sequence lines")

parser.add_argument("nucleotide_file", metavar="NUCL-FILE",
help= """File containing lines of nucleotide data. Just lines \
are interspersed. NO FASTA PARSING IS DONE. 
One FASTQ record is formed for each line.""")

parser.add_argument("quality_file", metavar="QUALITY-FILE",
help= """File containing lines of text which are inserted \
as quality score lines into the output. Same \
format as NUCL-FILE.""")

parser.add_argument("index_file", metavar="INDEX-FILE",
                     nargs="?", 
help= """File containing indices the new FASTQ \
records should have, one per line. If absent, sequential \
integers are used.""")

def main():
    args= parser.parse_args()
    nclfile=args.nucleotide_file
    quafile=args.quality_file
    idxfile=args.index_file

    idxfh=None
    if(idxfile != None):
        idxfh=open(idxfile,"rt")

    if(idxfh == None):
        idxgen = seq_generator(1)
    else:
        idxgen = idx_file_generator(idxfh)
            
    try:
        with open(nclfile,"rt") as nclfd, open(quafile,"rt") as quafd:
            print_fastq_lines(nclfd,quafd,idxgen)
    
    finally:
        if(idxfh != None):
            idxfh.close()


def print_fastq_lines(nclfd, quafd, idxgen, ostream=sys.stdout):
    while(True):
        # Read one line of files
        nline=next(nclfd,None)
        qline=next(quafd,None)
        nidx=next(idxgen,None)

        # Quit if one is EOF
        if not all([nline,qline,nidx]): break

        nline = nline.rstrip()
        qline = qline.rstrip()
        # Truncate Quality line to length of nucleotide line
        nllen=len(nline)
        qline=qline[0:nllen]
        # Output
        print(generate_id_line(nidx), file=ostream)
        print(nline, file=ostream)
        print("+", file=ostream)
        print(qline, file=ostream)

    if bool(nline) != bool(qline):
        raise Exception('Different number of nucleotide and quality lines, '+
                 'result is truncated')
    if not nidx:
        raise Exception('Too little lines of read indices, result is truncated')

def generate_id_line(id):
    """Generate a FASTQ Short Read ID line using the
    integer parameter `id'"""
    return "@{}".format(id)


# Generator producing sequential numbers
def seq_generator(start):
    i = start
    while True:
        i = i + 1
        yield i

# Returns content of a file, line-by-line
# skipping lines beginning with #.
# Produces a Generator. 
def idx_file_generator(filehandle):
    for line in filehandle:
        s=line.strip()
        if(line != "" and line[0] == "#"):
            continue
        yield s


if __name__ == "__main__": 
    try:
        main()
    except Exception as e:
        print('Error: {}'.format(e),file=sys.stderr)


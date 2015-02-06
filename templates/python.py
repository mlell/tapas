#!/usr/bin/env python
from argparse import ArgumentParser

parser= ArgumentParser(description="Generate FASTQ File from Nucleotide Sequence and Quality Sequence lines")

parser.add_argument("nucleotide_file", metavar="NUCL-FILE")
parser.add_argument("quality_file", metavar="QUALITY-FILE")

def main():
    args= parser.parse_args()
    nclfile=args.nucleotide_file
    quafile=args.quality_file
    print("Nucleotides from {}".format(nclfile))
    print("Quality from {}".format(quafile))







if (__name__=="__main__"): main()

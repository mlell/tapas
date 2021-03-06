#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from docopt import docopt
import sys
import unittest
from collections import namedtuple
import io

doc="""Usage: fasta_substring.py [options] FASTA 

Print bases from FASTA file, as specified on STDIN.

FAIDX is an index as generated by `samtools faidx FASTA`.

Input is expected to be three words per line:
    
    RECORD FIRST LENGTH

  * RECORD: Name of FASTA record to extract from
  * FIRST: Integer; Index of first base to print, counting starts at 1.
  * LENGTH: Length of sequence to output.

Options:

--index FAIDX  (Default: FASTA.fai) Specify an alternative filename for
               the FASTA index. Per default .fai is appended to the 
               filename of the FASTA argument.

--test         Run unit tests.
"""


class FastaIndex:
    Entry = namedtuple("Entry",
        "name length_char offset nchars_line nbytes_line")

    def __init__(self,input):
        """Reads input (lines of text) and generates a FastaIndex
        object."""
        self.entries = dict()
        for line in input:
            vals = line.split()
            name = vals[0]
            vals = [(v if i==0 else int(v)) for i,v in enumerate(vals)]
            self.entries[vals[0]] = self.Entry(*vals)

    def getNames(self):
        return sorted([x for x in self.entries.keys()])

def slice(file, index, record, start, length):
    """Reads a sequence of letters from `file`. record is character: The FASTA
    record name, start is a 0-based base index, length is the desired length of
    the output"""
    def readLetters(file, amount):
        if amount < 0: raise IndexError("Amount may not be < 0")
        if amount == 0: return ""
        output = []
        while len(output) < amount:
            c = file.read(1)
            if not c: raise IndexError(
               "Index doesn't match FASTA file: EOF while reading letters")
            if c == ">": raise IndexError(
               "Index doesn't match FASTA file: End of record while reading "+
               "letters")
            if ord(c) > 126 : raise ValueError("Encountered non-ASCII character")
            if ord(c) < 33: continue # non-printable (whitespace)
            
            output.append(c)
            
        return "".join(output)

    entry = index.entries[record]

    if start >= entry.length_char: 
        raise IndexError("Start base index {} is ≥ record length ({}) (remember: 0-based index!)"
                .format(start,entry.length_char))
    if start + length > (entry.length_char-1):
        length = entry.length_char - start

    off_rec      = entry.offset
    charsperline = entry.nchars_line
    bytesperline = entry.nbytes_line
    startline    = start // charsperline # 0-based

    startline_bytes  = startline*bytesperline
    startline_chars  = startline*charsperline
    startline_offset = off_rec + startline_bytes
    file.seek(startline_offset)
    #[print("{} = {}".format(k,v)) for k,v in locals().items()]
    # Read line to start character
    readLetters(file, start - startline_chars)
    return readLetters(file, length)


def main(argv):
    args = docopt(doc,argv[1:])
    if args["--test"]:
        sys.exit(test())
   
    if args["--index"]: indexname = args["--index"]
    else: indexname = args["FASTA"]+".fai"

    with open(indexname, "rt") as ifd:
        index = FastaIndex(ifd)

    with open(args["FASTA"]) as fasta_fd:
        while True:
            line = sys.stdin.readline()
            if not line: break
            s = line.split()
            if len(s) != 3: 
                raise ValueError("Wrong format of base coordinates")
            record = s[0]
            start = int(s[1])
            length = int(s[2])

            print(slice(fasta_fd, index, record, start,length))



def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)

class Test(unittest.TestCase):
    def setUp(self):
        with open("test.fasta.fai","rt") as fd:
            self.index = FastaIndex(fd)
        self.fastafd = open("test.fasta","rt")
    
    def tearDown(self):
        self.fastafd.close()

    def test_readsFai(self):
        self.assertEqual(self.index.entries["Head1"].name, "Head1")
        self.assertEqual(self.index.entries["Head1"].length_char, 33)
        self.assertEqual(self.index.entries["Head1"].name, "Head1")
        self.assertEqual(self.index.entries["Head1"].length_char, 33)
        self.assertEqual(self.index.entries["Head1"].nchars_line, 9)
        self.assertEqual(self.index.entries["Head1"].nbytes_line, 10)
        self.assertEqual(self.index.entries["Head1"].offset, 11)

    def test_slicing(self):
        s = slice(self.fastafd, self.index, "Head1", 2, 10)
        self.assertEqual(s, "34567890ab")
    def test_slice_last(self):
        s = slice(self.fastafd, self.index, "Head1", 32, 2)
        self.assertEqual(s,"w")
    def test_outofboundsError(self):
        self.assertRaises(IndexError, 
               slice, self.fastafd,self.index,"Head1",33,1)

if __name__ == "__main__": 
    if len(sys.argv)>0 and sys.argv[1] == "--test": test()
    else: main(sys.argv)




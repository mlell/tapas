#!/usr/bin/env python
import argparse
import random 
import sys
from textwrap import dedent

# Don't throw an error if output is piped into a program that doesn't
# read all of its input, like `head`.
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL) 

description = dedent(
    """Insert insertions and deletions randomly into a sequence recieved
    via standard input.""")

def parse_arguments():
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--i-open', default=0, help=
            "Per-base probability of a seqence insertion")
    p.add_argument('--i-min', default=1, help=
            "Minimum length of a sequence insertion")
    p.add_argument('--i-decay', default=...)

def main():
    args = parse_arguments()


class MutableSequence:
    """This class holds list-like object which represents a biological
    sequence where each element is one character. Elements can be changed
    and seqences inserted and removed. A CIGAR string is updated on each
    change which represents the changes done. """

    def __init__(self, sequence):
        try:
            self.seqence = self.sequence
            self.cigar = self.cigar
        except AttributeError:
            # sequence is not a MutableSequence
            self.sequence = bytearray(sequence, encoding='ascii')
            self.cigar = bytearray(b'M'*len(sequence))

    def __len__(self):
        return len(self.sequence)

    def __repr__(self):
        return('MutableSequence: {}'.format(self))

    def __str__(self):
        return self.sequence.decode('ascii')
    
    def __getitem__(self,s):
        print("getitem: {}".format(s))
        r = self.sequence[s]
        try:
            return r.decode('ascii')
        except AttributeError: # int returned
            return chr(r) 


    def insert(self, where,what):
        what = [bytes(c,'ascii') for c in what]
        # Insert in seqence. Not reversed because insertion index stays
        # the same.
        for b in reversed(what):
            self.sequence.insert(where,ord(b))
            self.cigar.insert(where,b'i')



if __name__ == "__main__": main(sys.argv)

# vim:tw=75


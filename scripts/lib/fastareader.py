#!/usr/bin/env python

# @autor Moritz Lell
# @date 2015-Aug-25

""" This module is used by uniform.py """

import sys
import re

class FASTA:
    """Reads in a linearized(!) FASTA file and the corresponding FASTA record index.
    Because the linearized FASTA data contains no newlines or
    whitespace in its nucleotide sections, fast random access is
    possible using the slice function."""
    def __init__(self, fd):
        self.fd = fd

#    def _calc_len_data(self):
#        data_end = self.pos_head[1:] + [self.pos_end]
#        self.len_data = [ e-s for s,e in zip(self.pos_data,data_end) ]

    def readIndex(self,fd):
        """ Expects a category (head|data|end) and an offset 
        (integer) per line, separated by a space character.
        Creates an index. """
        entries = [ l.strip().split(" ") for l in fd ]
        # c: category (head|data|end), o: offset in file
        entries = [ (c,int(o)) for (c,o) in entries]

        self.pos_head = []
        self.pos_data = [] 
        self.len_data = []
        self.pos_end = -1
        for e in entries:

            category,offset = e

            if category == "head": 
                self.pos_head.append(offset)
            elif category == "data": 
                self.pos_data.append(offset)
            elif category == "len":
                self.len_data.append(offset)
            elif category == "end":
                self.pos_end = offset

        # 0 => False, [] => False in python's `if`
        if not self.pos_head  \
        or not self.pos_data  \
        or self.pos_end == -1 :
            raise ValueError("Invalid index!")

    def FASTARecordNames(self):
        if not hasattr(self,"pos_head"):
            raise ValueError("File must be indexed before usage!")
        
        recordnames = []
        p = re.compile(r'[ \r\n]')
        for offset in self.pos_head:
            self.fd.seek(offset+1)
            headerline = self.fd.readline()
            recordname = p.split(headerline, maxsplit=1)[0]
            recordnames.append(recordname.strip())

        return(recordnames)

            





    def slice(self,record,start,length):
        """ Returns a slice of coordinates after SAM specification
        i.e. first base starts with 1. This function needs the bases
        of the FASTA file to be without whitespaces or newlines! This
        is for efficient file seek operations to be possible."""

        if not hasattr(self,"pos_data"):
            raise ValueError("File must be indexed before usage!")

        if length == 0: 
            return ""

        if start < 1:
            raise ValueError("start must be >= 1, indexing is"+
            " according to SAM specification (1-based indices)")

        # Determine start offset in file. NO NON-BASE-CHARACTERS
        # (E.G. WHITESPACE MAY BE PRESENT IN THE DATA SECTION!
        record_offset = self.pos_data[record]
        self.fd.seek(record_offset+start-1)

        # Determine record end offset in file
        try:
            end_record = self.pos_head[record+1]
        except IndexError :
            end_record = self.pos_end

        if length < 0 :
            raise IndexError("Negative length is not valid")
        if start <= 0:
            raise IndexError("start index must be > 0!")
        if record_offset+start-1+length > end_record:
            raise IndexError("Slice length exceeds record end!")

        ret = self.fd.read(length)
        if len(ret) != length:
            raise ValueError(("End of file was reached while getting "+
                    "slice record {}, start {}, len {}. Current file "+ 
                    "offset {}. Read seq:.{}.")
                    .format(record, start, length, self.fd.tell(),ret))
        
        if any([x in ret for x in ["\r","\n"," ","\t"]]):
            raise ValueError("Whitespace character detected in "+
                             "FASTA slice! The input FASTA must be "+
                             "linearized!")
    

        return ret
                    




if __name__ == "__main__": main(sys.argv)



# vim: tw=70


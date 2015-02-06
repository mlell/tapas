#!/usr/bin/env python

# @author Moritz Lell
# @date   2015-Aug-25
# @unittest uniform.py

from fastareader import *
from unittest import TestCase,main
from io import StringIO

###########################################################
# WARNING: These Tests are out of date! (ML, 2015-Sep-23) #
###########################################################


class FASTATest(TestCase):
    # This input has 9 letters + 1 \n per row = 10 chars/row
    testFASTA="""\
>record 1
AAAAATTTT
GGGGGCCCC
>record 2
AATTCCGGA
AAAGGGCCC
"""
    def setUp(self):
        self.f = FASTA(StringIO(self.testFASTA))
        self.f.index()

    def test_index_data(self):
        a = self.f.pos_data
        b = [10,40]
        end = 60
        self.assertEqual(a,b)
        self.assertEqual(self.f.pos_end,end)

    def test_index_head(self):
        a = self.f.pos_head
        b = [0,30]
        self.assertEqual(a,b)

    def test_data_len(self):
        a = self.f.len_data
        b = [20,20]

    def test_slice(self):
        a = self.f.slice(1,0,4)
        b = "AATT"
        self.assertEqual(a,b)

    def test_slice_empty(self):
        a = self.f.slice(1,2,0)
        b = ""
        self.assertEqual(a,b)

    def test_slice_end(self):
        a = self.f.slice(1,18,1)
        b = "C"
        self.assertEqual(a,b)

    def test_slice_index_error(self):
        with self.assertRaises(IndexError):
            self.f.slice(0,0,30)
        with self.assertRaises(IndexError):
            self.f.slice(2,1,3)
        with self.assertRaises(IndexError):
            self.f.slice(0,-1,3)
        with self.assertRaises(IndexError):
            self.f.slice(0,4,-1)


if __name__ == "__main__": main()


# vim: tw=70
???

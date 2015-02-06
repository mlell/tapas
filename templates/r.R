#!/usr/bin/Rscript

# R script to ...
# Author: Moritz Lell (2015-Feb-13)

# Get command line: Rscript <Scriptname> A B C ...
#                                       |------- ... --|
args=commandArgs(trailing=TRUE)
# Parse command line: must have exactly 3 arguments
if(length(args) != 4)
    stop("Usage: ........")



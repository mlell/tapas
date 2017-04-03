#!/usr/bin/env python
import csv
import argparse
import subprocess as sp
import os
import os.path
import sys
import re
from collections import namedtuple

helpText="""\
Convert mapDamage output into parameters of a fitted distribution.
Currently, the R script fit_geom.R is used to perform the fitting.

Input is expected to begin with a header line matching the following
regular expression:

    ^pos [35]p[ATGC]>[ATGC]$

where whitespace can be of arbitrary length >0 and contain tab stops.

Following the input, lines are expected to contain two columns of
text, of which the second column holds the base exchange probabilities
for a distance in bp from the end of the read. The header specifies,
which end.

***NOTE:*** Due to a bug in mapDamage, the header reports incorrect
information about the read direction (5'>3' or vice versa). Therefore
this script currently determines the aforementioned informations from
the file name. The header line is ignored. The --metadata switch can
be used to change this behaviour. (as of mapDamage version 2.0.2-8)
"""

# Are we using Python3?
PYTHON3 = sys.version_info >= (3,0)

DIST_FIT_R_SCRIPT = os.path.dirname(
                    os.path.realpath(
                        sys.argv[0])  ) \
                    + "/../fit_geom"

RResult         = namedtuple("RResult"
                            , ['factor', 'geom_prob', 'intercept' ] )
MapDamageHeader = namedtuple( "MapDamageHeader"
                            , ['direction', 'fromBase', 'toBase'] )


def main():
    aparser=create_argument_parser()
    args=aparser.parse_args()

    # Create Plot folder
    plot_prefix = args.fit_plots
    if plot_prefix != None:
        create_plot_folder(plot_prefix)
    
    # List of files to process
    mdfiles=args.mdfiles

    print("strand\tfrom\tto\tfactor\tgeom_prob\tintercept")
    
    for i,f in enumerate(mdfiles):
        if plot_prefix != None:
            plot_filename="{prefix}{i:03d}_{filename}.pdf".format(
                    prefix   = plot_prefix
                  , i        = i
                  , filename = os.path.basename(f))
        else:
            plot_filename = None
        outputParams=processMapDamageFile(
            filename         = f,
            readMetadataFrom = args.metadata,
            plotFilename     = plot_filename)
        outputList = [p.rstrip('\n') for p in outputParams]
        print("\t".join(outputList))


def create_plot_folder(plotPrefix):
    """ Creates the folder specified in the plotPrefix 
    ( dir1/dir2/plot_ --> dir1/dir2 ). If the folder exists already,
    raise an error in order to prevent accidential overwriting"""
  
    plot_folder = os.path.dirname(plotPrefix)

    if plot_folder == '': return

    if os.path.isfile(plot_folder) : 
        raise IOError(("Cannot create a folder named {}: File of"+ 
                "that name exists already").format(plot_folder))
    if os.path.isdir(plot_folder):
        return
    os.makedirs(plot_folder)

def processMapDamageFile(filename,readMetadataFrom="filename"
                       , plotFilename=None):
    """ Open a file, read base exchange and strand direction, 
    read probability values, fit a function and print the parameters."""
    
    with open(filename,"rt") as fd:
        # Read strand direction and mutated base
        # Deal with mapDamage bug
        firstLine     = fd.readline()
        info          = readMetadata(filename,firstLine,readMetadataFrom)        
        # Read probabilities from file
        probabilities = [ l.split()[1] for l in fd if l.strip() != "" ]
        
        # Fit geometrical distribution
        par           = call_distribution_fitting(probabilities,
                                                  plotFilename)
    
    return (info.direction, info.fromBase, info.toBase
          , par.factor    , par.geom_prob, par.intercept)


def readMetadata(filename, firstLine, readMetadataFrom):
    if readMetadataFrom == "header":
        return(parseFirstLine(firstLine))
    elif readMetadataFrom == "filename":
        return(parseFileName(filename))
    else: 
        raise NotImplementedError("Illegal argument for \
            readMetadata!")


def call_distribution_fitting(probabilities, plotFilename=None):
    " Expects a list of probability scores to be forwarded to the R script. \
    Parses the output"
    # Arguments for R script
    outformat_arg="ofmt={factor},{geomprob},{intercept}"
    data_arg="data=-"
    plot_arg= None if plotFilename == None \
              else "plot="+plotFilename
    # Call R script
    R_call = [DIST_FIT_R_SCRIPT, data_arg , outformat_arg]

    if plot_arg != None: R_call.append(plot_arg)
    R_process=sp.Popen(R_call         , stdin=sp.PIPE
                     , stdout=sp.PIPE , stderr=None)
    r_in = os.linesep.join(probabilities) + os.linesep

    if PYTHON3 : 
        r_in = r_in.encode()

    r_out, r_err = R_process.communicate(r_in)
   
    if PYTHON3 : r_out = r_out.decode()
    # split output by whitespace
    r = r_out.split(',')
    
    return RResult( factor    = r[0]       
                  , geom_prob = r[1]
                  , intercept = r[2])


# This function cannot be used due to a possible bug in mapDamage?
# The first line of mapDamage files doesn't reflect the direction 
# of the read properly. 3' to 5' reads should (in my opinion) have
# a first line of 'pos 3pG>A' (if A is mutated to G) but has
# 'pos 5pG>A'. 5' to 3' reads have also a first line of
# 'pos 5pC>T' (if C is mutated to T). Therefore, direction is not
# inferrable from the first line. ~~~Moritz Lell, 8-May-2015
def parseFirstLine(line):
    """ Gets information about strand direction and which base to
    exchange for which base out of the first line of a mapDamage
    output. This function suffers from a bug due to mapDamage
    incorrectly reporting the read direction as always being 5'>3'."""
    p = re.compile("^pos[\t ]([35])p([ATGC])>([ATGC])")
    m = p.match(line)
    if m == None:
        raise ValueError(
        ("The line {} is not a proper mapDamage header! "+
         "An Example for a proper format: 'pos 5pG>A'").format(line))
    
    return(MapDamageHeader( direction = m.group(1)
                          , fromBase  = m.group(2)
                          , toBase    = m.group(3)))


def parseFileName(filename):
    """Parses a filename of the form [3|5]p[ATGC]to[ATGC]_freq.txt
    to infer read direction and exchanged bases. This method is a
    workaround for a possible bug in mapDamage that doesn't report the
    read direction correctly in the header line of its output"""
    #Only use basename, strip all directories in the path
    basename = os.path.basename(filename)
    # Expected filename format
    p = re.compile(".*([35])p([ATGC])to([ATCG])_freq\.txt$")
    m = p.match(basename)
    # Filename is not of expected format
    if m == None:
        raise ValueError(
        ("The file name {} is not in proper format! "+
         "An Example for a proper format:"+
         "'5pGtoA_freq.txt'").format(basename))
    
    return(MapDamageHeader( direction = m.group(1)
                          , fromBase  = m.group(2)
                          , toBase    = m.group(3)))

    
def create_argument_parser():
    aparser=argparse.ArgumentParser(description=helpText
                       , formatter_class=argparse.RawDescriptionHelpFormatter)
    aparser.add_argument("mdfiles",metavar="mapdamage-files...",nargs="+",
            help=\
    """Filenames of mapDamage output files. If no files are given, standard
    input is read. The first line of the file is expected to be a with a 
    header, as described in the --metadata help. The following lines
    are expected to be two columns of numbers. The second column is saved as
    base exchange probabilities""")
    aparser.add_argument("--metadata", choices=["filename","header"],
            default="filename",help=\
    """Whether the information about read direction, and mutated base
    shall be inferred from the filename or the first line of the file.

    ***NOTE:*** Inferring from the header line doesn't work currently
    due to a bug in mapDamage which reports always 5'>3' in its header
    line! Filename is expected to be of the form
    '.*[3|5]p[ATGC]to[ATGC]_freq.txt', XXX being an arbitrary
    string.""")

    aparser.add_argument("--fit-plots", default=None,
            help=\
    """If this switch is given, data vs. fitted plots are created. A
    prefix for the plot names is expected. This can contain folders.
    Folders are created as needed.""")

    return aparser
 


if __name__=="__main__": main()

# vim: tw=70

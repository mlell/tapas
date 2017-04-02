#!/usr/bin/env python
import sys
import argparse
from pandas import DataFrame
from textwrap import dedent
import matplotlib as plt

def main(argv):
    args = parseArgs(argv)
    print(args)

    infile = args.INFILE
    if infile == "-": infile = sys.stdin
    dat = pd.read_csv(infile, whitespace_delim = True)

def bar(x,y,height,corr_hq, corr_lq, incorr_hq, incorr_lq):
    p = plt.pie([corr_hq,corr_lq,incorr_hq,incorr_lq]
               , colors=["#FFC531","#58D452","#70DB1D","#8AE444"]
               , radius=radius)
    return mpl.collections.PatchColleckkktion(p)

def parseArgs(argv):
    p = argparse.ArgumentParser\
            ( description=__doc__
            , formatter_class=argparse.RawTextHelpFormatter
            )
    p.add_argument("TRUE_ORG", help="Column name: True read organism")
    p.add_argument("MAP_ORG",  help="Column name: Mapped read organism")
    p.add_argument("CORRECT", 
            help="Column name: Whether read was mapped correctly")
    p.add_argument("COUNT", help="Column name: Amount of reads")
    p.add_argument("PLOT_FILE", 
            help="File name: File name of plot to be generated")
    p.add_argument("INFILE", nargs="?", default="-", 
            help=dedent("""\
                File name: Text table of aggregated read data. If
                '-' or omitted, read from standard input."""))

    return p.parse_args(argv)











if __name__ == "__main__":
    main(sys.argv[1:])

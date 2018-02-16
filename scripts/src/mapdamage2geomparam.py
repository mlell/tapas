#!/usr/bin/env python
import csv
import argparse
import subprocess as sp
import os
import os.path
import sys
import re
from collections import namedtuple
from textwrap import dedent
from numbers import Number

from itertools import product

import numpy as np
import pandas as pd
from numpy import array 
from scipy.optimize import curve_fit


helpText="""\
Convert mapDamage output into parameters of a function which returs
the per-base probability that it is subjected to a certain base exchange. 
The parameters 'factor', 'geom_prob' and 'intercept' are estimated,
which relate to the following function:

    P_from(i, end, to) = factor × geom(i, geom_prob) + intercept

P is the probability that the base on position i, as counted 1-based from
the read end 'end' (end = 3' or 5') is subjected to the base exchange
'from' -> 'to' (where 'from' and 'to' may be A,T,G or C). 'geom' is the
geometric distribution density function with support {1,2,3...} and
probability parameter 'geom_prob'.

The input is the 'misincorporation.txt' file which is produced by the
mapDamage program (Jónsson et al. Bioinformatics 2013 and Ginolhac et
al. Bioinformatics 2011). Least-squares fitting is used to determine
the parameters of the aforementioned function.

The parameters are printed in a text table for each combination of
read end, mutation origin and target base.
"""

# Are we using Python3?
PYTHON3 = sys.version_info >= (3,0)

DIST_FIT_R_SCRIPT = os.path.dirname(
                    os.path.realpath(
                        sys.argv[0])  ) \
                    + "/../fit_geom"

GeomPars = namedtuple("GeomPar", 
            ['factor', 'geom_prob', 'intercept' ])

mapDamageHeaders = ['strand', 'from', 'to']

def main():
    aparser=create_argument_parser()
    args=aparser.parse_args()

    # List of files to process
    mdfiles=args.mdfiles

    M = readMisincorporationTxt(mdfiles)
    M.drop(['Chr','Std'],axis=1,inplace=True)
    M = M.groupby(['End','Pos'])
    A = M.aggregate(np.sum)
    A = A.ix[A.Total != 0,:]

    # Calculate per-base substitution rates
    for f,t in product('ATCG','ATCG'):
        if f == t: continue
        A[f+'>'+t] = A[f+'>'+t] / A[f]
    
    A = A.iloc[A.index.get_level_values('Pos') <= args.n_bp,]

    results = processMapDamageFile(A)

    # Make sure that only one intercept value is reported for each
    # base exchange. There may be two, derived from 3' and 5' read
    # ends, respectively. Assign the mean to one of the output lines
    # for that base exchange and set the value in the other output
    # line to NA.
    nIntercepts = results.groupby(['from','to']).size()
    for f,t in nIntercepts.index.tolist():
        if nIntercepts.loc[f,t] > 1:
            #import pdb;pdb.set_trace()
            i = np.flatnonzero((results['from'] == f) & (results['to'] == t))
            m = np.mean(results.loc[i,'intercept'])
            results.loc[i,'intercept']    = np.nan
            results.loc[i[0],'intercept'] = m

    # Print output
    float_format="%.{}g".format(args.print_digits)
    print(results.to_csv(sep="\t",index=False,na_rep="NA",float_format=float_format), end="")

    # Create Plot folder
    plot_filename = args.fit_plots
    
    if plot_filename != None:
        plotFitResult(A, results, plot_filename)

def processMapDamageFile(A,readMetadataFrom="filename"
                       , plotFilename=None):
    """ Open a file, read base exchange and strand direction, 
    read probability values, fit a function and print the parameters."""

    nRows = 2*4*3 # 2 strand ends, 4*3 base combinations
    pars = pd.DataFrame( index = np.arange(0, nRows) 
                       , columns=[*mapDamageHeaders, *GeomPars._fields]
                       )
    # Convert the parameter columns to numeric dtype to facilitate 
    # pretty printing of floats
    pars.factor = pd.to_numeric(pars.factor)
    pars.geom_prob = pd.to_numeric(pars.geom_prob)
    pars.intercept = pd.to_numeric(pars.intercept)

    iRow = 0

    for e in ['3p','5p']:
        A2 = A.xs(e,level='End')
        for (f,t) in product('ACGT','ACGT'):

            A2 = A.xs(e,level='End')
            if f == t: continue
            par = fitScalableGeom(np.array(A2.index), A2[f+'>'+t])
            pars.loc[iRow] = [e,f,t,*par]
            iRow = iRow + 1

    return pars

def readMisincorporationTxt(filename):
    """Convert the 'misincorporation.txt' file, as output by
    mapDamage, to a numpy array"""
    sep = "\t"
    with open(filename,'r') as fd:
        while True:
            line = fd.readline()
            if not line.startswith('#'): break
        header = line.split(sep)

        d = {k:'int' for k in header}
        for k in ['Chr','End','Std']: d[k] = 'category'
        M = pd.read_table(fd,names=header
                         , delimiter=sep
                         , dtype=d
                         )
    return M

def plotFitResult(probabilities, fit_parameters,filename, imgFormat='png'):
    """Plot the fit versus the data (mutation probabilities per base
    type and base position.

    Parameters:
        probabilities:
            Data frame containing the mutation probabilities per base
            position and base exchange

            index columns: End (5' or 3' read end), 
                           Pos (bp distance from respective end)
            columns:       A>C, A>T, A>G, C>A, C>G, ... 
                           which denote the respective base substitutions
        fit_parameters:
            Data frame containing parameters of geometric
            distributions modelling the base substitution probability
            per base substitution type and position

            columns: strand (3p or 5p)
                     from   (substitution origin base)
                     to     (substitution target base)
                     factor, geom_prob, intercept 
                            (parameters of the
                             geometric distribution which models the
                             respective substitution probability)
        filename:
            String which contains the file name of the plot to be
            created. 
        imgFormat (png [default] | pdf | show):
            png:  Output a PNG file. 
            pdf:  Output a PDF file.
            show: Show the plot on screen.
    """

    try:
        import matplotlib
        if imgFormat == 'png':  
            matplotlib.use('Agg') 
        elif imgFormat == 'pdf':
            matplotlib.use('PDF') 
        elif imgFormat == 'show':
            pass
        else: 
            raise ValueError("imgFormat must be png or pdf")

        import matplotlib.pyplot as plt

    except ImportError:
        raise ImportError("The python package matplotlib is not "+
            "installed but is required for plotting")


    nEnds = 2  # 3' and 5' end of DNA short read
    bases = 'ATCG'

    ylim = max(max(probabilities[a+">"+b]) for (a,b) in product(bases,bases) if a!=b)

    fig, ax = plt.subplots(len(bases),len(bases)*nEnds,sharex=False, sharey=True)
    fig.subplots_adjust(left=0.13, bottom=0.13, right=0.9, top=0.85,
            wspace=0.2, hspace=0.1)
    fig.set_size_inches(8,5)

    fit_parameters.set_index(['from','to','strand'],inplace=True)

    for (iF,f),(iT,t) in product(enumerate(bases),enumerate(bases)):

        for iEnd, (sign,e) in enumerate(zip([1,-1],['5p','3p'])):
            cAx = ax[iT, iF*2+iEnd] # cAx is used outside the for loop!
            cPos = cAx.get_position()
            cWidth = cPos.width

            # No plots on diagonal
            if f == t: 
                fig.delaxes(cAx)
                continue

            cPos.x0 = cPos.x0 + 0.05*cPos.width*sign
            cPos.x1 = cPos.x0 + cWidth

            cAx.set_position(cPos)

            p = probabilities.xs([e],level=['End'])[f+'>'+t]
            x = np.array(p.index.get_level_values('Pos'))

            pars = fit_parameters.loc[f,t,e].to_dict()

            # If no intercept is specified for this end, take the
            # intercept parameter from the other end.
            if np.isnan(pars['intercept']): 
                otherend = next(iter(set(['5p','3p']) - set([e])))
                pars['intercept'] = fit_parameters.loc[(f,t,otherend),'intercept']

            y_fun = scalableGeom( first_success  = x
                                , p_success      = pars["geom_prob"]
                                , factor         = pars["factor"]
                                , added_constant = pars["intercept"]
                                )

            cAx.plot(sign*x, p, 'ok', ms=2)
            cAx.plot(sign*x, y_fun, "b-")
            cAx.set_ylim([0, ylim])
            for tck in cAx.get_xticklabels(): tck.set_rotation(45)

            # Only show x tick labels for the plots at the bottom end
            # of the figure
            if (iT,iF) not in [(3,0), (3,1), (3,2), (2,3)]:
                cAx.set_xticklabels([])
        

    xmin = min(a.get_position().xmin for a in ax.flat)
    ymin = min(a.get_position().ymin for a in ax.flat)
    xmax = max(a.get_position().xmax for a in ax.flat)
    ymax = max(a.get_position().ymax for a in ax.flat)

    # Print the bases at the outer plot margins
    for i,b in enumerate(bases): 
        # A,T,C,G label offsets and spreads
        ttop, ftop = 0.21, 0.2    # top labels ("from")
        trgt, frgt = 0.24, 0.195  # right labels ("to")
        # Mutation from:
        figText(fig, b , i*ftop+ttop, 0.9   , va='bottom')
        # Mutation to:
        figText(fig, b , 0.92 , 1-(i*frgt+trgt) , ha='left')

    # Print the other outer plot margin annotations
    figText(fig, "from", 0.5, 0.95)
    figText(fig, "to"  , 0.97,0.5, rotation=90)
    figText(fig, "mutation probability"  , 0.03,0.5, rotation=90)
    figText(fig, "Base pairs"  , 0.5,0.01, va='bottom')

    # Print the markers for 5' and 3' end
    ax[1,0].annotate( "5' end", xy=(0,1), xytext=(0,20) 
                    , xycoords=('axes fraction', 'axes fraction')
                    , arrowprops = dict(arrowstyle='-'
                          , connectionstyle="angle,angleA=45,angleB=90"
                    )
                    , textcoords = 'offset points')
    ax[1,1].annotate( "3' end", xy=(1,1), xytext=(-30,20) 
                    , xycoords=('axes fraction', 'axes fraction')
                    , arrowprops = dict(arrowstyle='-'
                          , connectionstyle="angle,angleA=-45,angleB=90"
                    )
                    , textcoords = 'offset points')

    if imgFormat == 'show':
        plt.show()
    elif imgFormat == 'png':
        plt.savefig(filename, format='png', dpi=300)
    elif imgFormat == 'pdf':
        plt.savefig(filename, format='pdf')

def figText(fig, text, x, y
           , coord='figure fraction',ha='center',va='center' 
           , **kwargs):
    cAx = fig.axes[0]
    cAx.annotate(text
                , xy=(x, y)
                , xycoords='figure fraction'
                , size=14
                , ha=ha, va=va
                , **kwargs)


def geom(xs, p):
    """Geometric probability mass function. x=number of desired
    Bernoulli trials, p=Success probability of a single Bernoulli
    trial. Returns: Probability that the x's trial is the first
    success"""
    if any(xs<1) or p<0 or p>1: raise ValueError('function not defined')
    return ((1-p)**(xs-1)) * p

def scalableGeom(first_success,p_success,factor=1,added_constant=0):
    """Geometric probability mass function which can be scaled by 
    a factor and moved up and down the dependent variables axis by 
    adding a constant."""
    return factor * geom(first_success,p_success) + added_constant

def fitScalableGeom(pos,probabilities):
    pars, cov = curve_fit(scalableGeom, pos, probabilities, 
            p0 = array([1e-1,0,0]), 
            bounds=(array([1e-1,0,0]),array([1,np.inf,np.inf])))

    # pars holds values in the same order as in the signature of
    # fitScalableGeom
    return GeomPars(geom_prob=pars[0], factor=pars[1],
            intercept=pars[2])


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
    
    return(MapDamageHeader( strand   = m.group(1)
                          , fromBase = m.group(2)
                          , toBase   = m.group(3)))


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
    
    return(MapDamageHeader( strand    = m.group(1)
                          , fromBase  = m.group(2)
                          , toBase    = m.group(3)))

    
def create_argument_parser():
    aparser=argparse.ArgumentParser(description=helpText
                       , formatter_class=argparse.RawTextHelpFormatter)
    aparser.add_argument("mdfiles"
        , metavar="misincorporation.txt", help=
    """`misincorporation.txt` output file of mapDamage""")

    aparser.add_argument("--fit-plots", default=None
        , metavar="FILENAME", help=dedent(
    """If this switch is given, data vs. fitted plots are created.
    The file name of the plot is expected as an argument"""))

    aparser.add_argument("--n-bp", default=20, type=int
            , metavar="N", help=dedent("""\
    The number of base pairs from the respective read end (3' or
    5') to use for fitting. Too high values might lead to higher noise
    in the mutation probabilities due to few reads bein so long, too
    low values limit the amount of data points available for fitting.
    If in doubt, create plots using `--fit-plots` and check whether the
    mutation probabilities look sensible."""))

    aparser.add_argument('--print-digits', default=4, type=int
        , metavar="N", help=dedent("""\
    The number of digits after the decimal dot to print."""))

    aparser.add_argument('--min-gp', default=0.1, type=float
        , metavar="N" , help=dedent("""\
    [default: 0.1] The minimum value which may be estimated for
    'geom_prob'. This is to avoid high values of 'factor' if no
    elevated mutation probability near the read ends is visible.

    A position-independent mutation rate shall be modelled by the
    estimating the 'intercept' parameter with this script. However, if
    the parameter 'geom_prob' becomes small, position-independent
    mutation rate can also be modelled by the 'factor' parameter.   If
    the provided mapDamage data indicates no elevated damage near the
    read end, prohibiting very small values for geom_prob will force
    the 'factor' parameter to be estimated very small, so that the
    mutation rate of the data is solely estimated by the 'intercept'
    value.

    Increase this value if the result estimates 'intercept' lower than
    the mutation baseline visible in the plot, together with a
    non-negligible value for 'factor' and a small 'geom_prob'. 
    Decrease this value if the fitted mutation probability (blue line in plot) 
    decreases too steep compared to its data (black dots) and
    geom_prob is estimated near the value set here."""))

    return aparser
 


if __name__=="__main__": main()

# vim: tw=70

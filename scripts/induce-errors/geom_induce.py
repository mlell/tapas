#!/usr/bin/env python
from argparse import ArgumentParser
import sys
from random import random

def main():
    parser= ArgumentParser(description="""
    Change one base into another with a probability geometrically dependent 
    on proximity to string beginning or end. The function used to calculate 
    the base exchange probabilities in dependence of the base position is

        P_{Base Exchange}(x) = fac * dgeom(x, prob) + t

    where dgeom is the density function of the geometric distribution.
    x is considered therein the trial number of the first success 
    (x \\in {1,2,3,...})
    All other parameters are explained below.
    """)

    parser.add_argument("fromBase", metavar="from", type=str,
            help="The base to change")
    parser.add_argument("toBase", metavar="to", type=str,
            help="The base to be changed into")
    parser.add_argument("prob", metavar="probability", type=float,
            help="argument for geometric distribution: success probability"+
                 "(don't confuse with base exchange probability!)")
    parser.add_argument("fac",  metavar="factor",type=float,
            help="factor to multiply the probabilities of base exchange")
    parser.add_argument("t",  metavar="const",type=float,
            help="constant part of base exchange probability function")
    parser.add_argument("--inverse",action="store_true", default=False,
            help="mutate with respect to distance from the end of the read"+
                 " instead from the beginning")
    
    args = parser.parse_args()
    prob     = args.prob
    fac      = args.fac
    fromBase = args.fromBase
    toBase   = args.toBase
    t        = args.t
    inverse  = args.inverse
    #sys.argv.pop(0) # shift
    #sys.argv.pop(0) # remove first two arguments, remaining for fileinput
    while True:
        line = sys.stdin.readline()
        if not line: break
        sys.stdout.write(geom_mutate(
                                string=line,   fromBase=fromBase
                              , toBase=toBase, fac=fac
                              , prob=prob,     t=t
                              , inverse=inverse))
        sys.stdout.flush() # don't buffer multiple lines


def geom_mutate(string,fromBase, toBase, fac, prob, t, inverse=False):
    """Read in a string. Then mutate each character with a probability
dependent on the distance from the beginning or the end (inverse=True).
Probability is modulated with the geometric density function geom:

    fac * geom(x, prob) + t

x being the distance from the beginning (the end). (x=1,2,3,...)"""
    l = len(string)
    s=list(string)
    fromBase=fromBase.lower()
    for i,char in enumerate(s):
        if(char.lower() == fromBase):
            k = l-i-1 if inverse else i+1
            r = random()
            # +1 because of geom. distr (no 0 allowed)
            x = fac * geom(k,prob) + t
            if r < x :
                s[i] = toBase
    return "".join(s)


def geom(k,p):
    """ Geometric probability mass function"""
    if(k<1): return None
    else: return ((1-p)**(k-1))*p


if (__name__== "__main__"): main()

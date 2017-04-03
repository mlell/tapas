#!/usr/bin/env python
import argparse
import random 
import sys
from textwrap import dedent
import pandas as pd
import numpy as np

# Don't throw an error if output is piped into a program that doesn't
# read all of its input, like `head`.
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL) 

# Used to make sure each deprecation warning is only shown once
__warn_shown = []

helpText=dedent("""
    Change one base into another with a probability geometrically dependent 
    on proximity to string beginning or end. The function used to calculate 
    the base exchange probabilities in dependence of the base position is

        P_{Base Exchange}(x) = fac * dgeom(x, prob) + t

    where dgeom is the density function of the geometric distribution 
    with prob specifying the success probability.
    x is considered the trial number of the first success. See 
    theory of the geometric distribution for more info about the meaning
    of 'trial' and 'success' and the parameters x and prob.
    That means, x is element of {1,2,3,...}

    The nucleotide sequences are expected in raw format (only the 
    nucleotide string, no FASTA format or similar) on standard input. The 
    mutated sequence is printed on standard output. The sequences are considered
    of 5' to 3' direction.

    The parameters are read from a tabular text file (whitespace-separated).
    For each line, the input sequence is mutated. Therefore, different rates for
    mutations of different bases can be specified.

    Example of an input table:

        # Lines starting with a hash are ignored as comments
        strand  from    to      factor          geom_prob       intercept
        3p      G       A       0.79513996      0.26918746      0.039386893
        5p      C       T       0.43360246      0.35249167      0.027965522

    The from and to columns can alternatively contain an asterisk (*). In the
    from column it means every character found in the string is replaced with
    the given parameters, in the to column it means the base mutated to is
    chosen by chance.

    Therefore, * in both the from and the two column means every character 
    in the input strings is mutated to a random character
    """)

class MutationChain(list):
    """A chain of mutator objects. Mutating a string with this object
    means mutating it with every object in the list. Mutators can
    be added with usual list methods (list.append) and are expected
    to posess a mutate(str)->str  method."""
    def mutate(self,string):
        for mut in self:
            string=mut.mutate(string)
        return string

class GeomMutator(object):
    def __init__(self,fromBase, toBase, factor, geom_prob, constant, inverse):
        self.f=float(factor)
        self.p=float(geom_prob)
        self.t=float(constant)
        self.inv=inverse
        self.fromBase=fromBase.lower()
        self.toBase=toBase
    
    def mutate(self,string):
        """Read in a string. Then mutate each character with a probability
        dependent on the distance from the beginning or the end (inverse=True).
        Probability is modulated with the geometric density function geom:

            fac * geom(x, prob) + t

        x being the distance from the beginning (the end). (x=1,2,3,...)"""
        l = len(string)
        s = list(string)
        fromBase=self.fromBase.lower()
        for i,char in enumerate(s):
            if(char.lower() == self.fromBase 
            or fromBase == "*" ):
                k = l-i if self.inv else i+1
                r = random.random()
                # +1 because of geom. distr (no 0 allowed)
                x = self.f * self.geom(k,self.p) + self.t
                if r < x :
                    s[i] = self.chooseBaseToMutateTo(char)
        return "".join(s)

    def chooseBaseToMutateTo(self, currentBase):
        """Selects a base to replace an input base with, depending on the
        toBase object attribute and the input character."""
        cb = currentBase.lower()
        nucleotides = ["a","t","g","c"]
        # If the character is not in [A,T,G,C], return it unchanged.
        if cb not in nucleotides: 
            return currentBase
        # If the base to be mutated to shall be chosen by chance
        if self.toBase == "*" :
            # Don't mutate to the same nucleotide
            nucleotides.remove(cb)
            return random.choice(nucleotides)
        else:
            # If the mutator shall mutate to a specific base, return this base
            return self.toBase
    
    def geom(self,k,p):
        """ Geometric probability mass function"""
        if(k<1): return None # not defined
        else: return ((1-p)**(k-1))*p

    def __repr__(self):
        return("GeomMutator: from={} to={} f={} p={} t={} inv={}".format(
                self.fromBase.upper(), self.toBase, self.f
              , self.p,                self.t,      self.inv))

def main():
    aparser=argparse.ArgumentParser(description=helpText
      , formatter_class=argparse.RawDescriptionHelpFormatter)
    aparser.add_argument("param_file", help="A whitespace-separated table \
            containing the columns strand, from, to, factor, geom_prob and \
            intercept")
    aparser.add_argument("--seed",default=None, type=int, help=\
            "Random number generator seed. Same value and same input leads \
            to same output.")
    args=aparser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        
    m = createMutationChain(args.param_file)
    while True:
        line=sys.stdin.readline().rstrip()
        if not line: break
        print(m.mutate(line))
        # Don't buffer output to avoid deadlock in calling scripts
        sys.stdout.flush()

def createMutationChain(filename):
    """ Reads in a file and parses it as whitespace separated table
    with column names. The first line is expected to be a header line
    containing the column names, whitespace separated. A MutationChain
    containing one Mutator object for each data line is created and 
    returned. There must be the column names present which are specified
    in the main help text of this script."""

    # Read in input table, ignoring lines starting with # and empty lines
    with open(filename,"rt") as fd:
        fields=[ l.split() 
                 for l in fd 
                 if not (
                     l.lstrip().startswith("#")
                     or l.strip() == "" ) ]

    reqd_headers = "strand from to factor geom_prob intercept".split()
    if not sorted(fields[0]) == sorted(reqd_headers):
        raise ValueError("Error: specified table misses columns or contains "+
                "additional columns! Consult the help with -h.\n\n")

    dat = pd.DataFrame(fields[1:], columns = fields[0])
    dat[['factor','geom_prob','intercept']] = \
        dat[['factor','geom_prob','intercept']].apply(pd.to_numeric,
                errors="coerce")

    dat.loc[np.isnan(dat['intercept']),'intercept'] = 0

    # Initalize object to be returned
    m = MutationChain()
    
    # For every row of input table
    for a in dat.to_dict('records') :
        # Convenience function f: Access elements by column name
        if a["strand"] in ["3","5"]:
            showWarning("DEPRECATED: Old format for column 'strand' "+
                        "provided (3|5). Use (3p|5p) instead.")
            a["strand"] = a["strand"]+"p"

        # Whether to mutate from 3' end or 5' end
        if a["strand"] == "3p":
            inverse = True
        elif a["strand"] == "5p":
            inverse = False
        else:
            raise ValueError(("Illegal entry {} in strand column!"+ 
                              "Expected: 3p or 5p").format(a["strand"]))
        # Add a mutator with read parameters to the chain
        m.append(GeomMutator( fromBase=a["from"]       , toBase=a["to"]  
                            , factor=a["factor"]       , geom_prob=a["geom_prob"] 
                            , constant=a["intercept"]  , inverse=inverse))
    
    return m


def showWarning(msg):
    global __warn_shown
    if msg not in __warn_shown:
        print(msg,file=sys.stderr)
        __warn_shown.append(msg)

if (__name__== "__main__"): main() 


# vim:tw=75


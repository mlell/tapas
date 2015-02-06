#!/usr/bin/env python
import argparse
import random 
import sys
from textwrap import dedent

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
        3       G       A       0.79513996      0.26918746      0.039386893
        5       C       T       0.43360246      0.35249167      0.027965522

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
    args=aparser.parse_args()
        
    m = createMutationChain(args.param_file)
    while True:
        line=sys.stdin.readline()
        if not line: break
        sys.stdout.write(m.mutate(line))
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
    # Process header line
    try:
        h=fields[0]
        # Determine the column number of each of the columns named
        # strand, from, to, factor, geom_prob, intercept
        # i will be a dictionary: column name -> column number
        i={c: h.index(c) for c in \
                "strand from to factor geom_prob intercept".split()}
    except ValueError as e:
        raise ValueError("Error: specified table doesn't contain \
                all the required fields! Consult the help with -h.\n\n")
    
    # Initalize object to be returned
    m = MutationChain()
    
    # For every row of input table
    for a in fields[1:] :
        # Convenience function f: Access elements by column name
        f=lambda s: a[i[s]]
        # Whether to mutate from 3' end or 5' end
        if f("strand") == "3":
            inverse = True
        elif f("strand") == "5":
            inverse = False
        else:
            raise ValueError(("Illegal entry {} in strand column!"+ 
                              "Expected: 3 or 5").format(a[i_strand]))
        # Add a mutator with read parameters to the chain
        m.append(GeomMutator( fromBase=f("from")       , toBase=f("to")  
                            , factor=f("factor")       , geom_prob=f("geom_prob") 
                            , constant=f("intercept")  , inverse=inverse))
    
    return m



if (__name__== "__main__"): main() 

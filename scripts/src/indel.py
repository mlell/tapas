#!/usr/bin/env python
import argparse
import csv
import random 
import sys
import math
from math import inf
from textwrap import dedent
from editCIGAR import CIGAR
from textwrap import dedent

# Don't throw an error if output is piped into a program that doesn't
# read all of its input, like `head`.
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL) 

description = dedent("""
    Insert insertions and deletions randomly into a sequence recieved
    via standard input. 
    
    Expected input format: For every input line: A string of nucleotides
    followed by a tab character, followed by a corresponding CIGAR
    string. Example:

        –––––––––––––––––––––––
        seq             cigar
        GGTGACATAAAGGC  8M5I
        TTCCGCAGGG      10M
        CTCGTGGAGT      5M2D5M
        ....
        –––––––––––––––––––––––
        (white space stands for one tab character)

    If no CIGAR strings are available for the nucleotides, then use the
    parameter --cigar-new. In that case, only a nucleotide string per line is
    expected. Every read is expected to have complete (mis)match to the 
    reference (CIGAR character M).
    """)

def parse_arguments(argv):
    p = argparse.ArgumentParser(description=description, 
        formatter_class= argparse.RawTextHelpFormatter)
    for s,l in [('in','insert'),('del','deletion')]:
        p.add_argument('--{}-prob'.format(s), default=0, 
            type = checkPositive(float), metavar='P', help=
            "Per-base probability of a seqence {}".format(l))
        p.add_argument('--{}-exp'.format(s), default=None, metavar = 'L',
            type = float, help=dedent("""\
                Length distribution of {}s shall be exponentially
                distributed, with 50%% of reads longer than L""")\
               .format(l))
    p.add_argument('--cigar-new', default = False, 
        action='store_true', help=dedent("""\
        Do not read CIGAR strings from standard input, but assume a 
        complete (mis)match (no indels, CIGAR character M) for every 
        nucleotide string."""))
    p.add_argument('--col-seq', default = 'seq', type = str,
        help = "Column name of the nucleotide strings")
    p.add_argument('--col-cigar', default = 'cigar', type = str,
        help = "Column name of the CIGAR strings")
   # p.add_argument('--input-fmt', default = ['lines'],
   #     nargs='+', metavar='',
   #     help =dedent("""\
   #     Format of the file containing the CIGAR strings. 
   #     Usage: --input-fmt lines
   #            --input-fmt tab COL-NUCL COL-CIGAR 
   #     Choices: 
   #     'lines': One nucleotide and CIGAR string per input line
   #     (use --cigar-new to assume only M instead of giving 
   #     CIGAR input)
   #     
   #     'tab COL-NUCL COL-CIGAR': The file is in a tabular format.
   #     The first line contains the column names, the following
   #     files contain the content.  Only the contents of the
   #     columns named COL-NUCL and COL-CIGAR are used.  Columns 
   #     are separated by a tab character (\\t), unless another 
   #     character is specified by the --sep argument
   #     """))
   # p.add_argument('--change-coords', nargs=2, 
   #     help=dedent("""\
   #     If an output CIGAR string begins or ends with an insertion
   #     or a deletion, change the true read coordinates instead.
   #     Else, such reads would not be assigned to their true position.
   #     """))
    p.add_argument('--no-header',default = False, action = 'store_true',
        help="Do not expect a table header. Specify column indices instead.")
    p.add_argument('--sep', default='\t', help=dedent("""\
        Character separating the input columns if the input is 
        in tabular format (see --input-fmt). Common choices
        are '\\t' (default), ',' or ';'."""))
    p.add_argument('--seed', default = None, type=int,
        help = dedent("""\
        Set the random number generator seed to 
        this value. Calls with the same input files
        and seed always produce the same result."""))
    args = p.parse_args(argv)

    if args.sep == '\\t':
        args.sep = '\t'

    if len(args.sep) != 1:
        raise ValueError('--sep must be followed by only one character')

    if args.in_exp is not None and (args.in_exp >= 1 or args.in_exp < 0):
        raise ValueError('--in-exp must be >=0 and < 1')
    if args.del_exp is not None and (args.del_exp >= 1 or args.del_exp < 0):
        raise ValueError('--del-exp must be >=0 and < 1')
    if args.in_prob < 0 or args.in_prob > 1:
        raise ValueError('--in-prob must be >= 0 and <= 1')
    if args.del_prob < 0 or args.del_prob > 1:
        raise ValueError('--del-prob must be >= 0 and <= 1')

    return args

def main(argv):
    # --- Argument checks ----------------------------------------
    args = parse_arguments(argv[1:])
    if args.in_prob != 0:
        if args.in_exp is None:
            raise ValueError("--in-prob requires --in-exp")
    if args.del_prob != 0:
        if args.del_exp is None:
            raise ValueError("--del-prob requires --del-exp")
    if args.seed is not None:
        random.seed(args.seed, version=2)

    # --- Input parsing --------------------------------------------
    input = sys.stdin
    def safe_index(l, what):
        try: return l.index(what)
        except ValueError: return None
    if not args.no_header:
        header = next(input).rstrip().split(args.sep)
        i_nucl, i_cigar =  \
            (safe_index(header, x) for x in \
            (args.col_seq, args.col_cigar))#, cn_start, cn_stop))
        if i_nucl is None or i_cigar is None:
            raise ValueError('Non-existent column names specified')
        i_rest = [i for i in range(0,len(header)) if i not in (i_nucl, i_cigar)]
    else:
        i_nucl, i_cigar = 0, 1
        i_rest = []

    rows = (s.rstrip() for s in input)
    fields = (s.split(args.sep) for s in rows if s != '')
    if args.cigar_new:
        step1 = splitter(fields, [(i_nucl,), i_rest])
        step1a = (n for (n,),r in step1)
        step2 = ((x,) for x in addCIGAR(step1a)) 
    else:
        step2 = splitter(fields, [(i_nucl,i_cigar)])

    step3 = mutatorExpLen((s[0] for s in step2), args.in_prob
            , args.in_exp, args.del_prob, args.del_exp)

    if not args.no_header:
        print(args.sep.join([args.col_seq, args.col_cigar]))
    for x in step3:
        print(args.sep.join(x))

def splitter(tuples, idxs):
    """idxs: list of tuples of indices (integer).  Returns a tuple with one 
    element for each element i in `idxs`. Return tuple i contains all tuples[j]
    for all j in idxs[i].
    >>> l = [(1,2,3), (4,5,6), (7,8,9)]
    >>> list(splitter(l, [(1), (2,3)]))
    [((1), (2, 3)), ((4), (5, 6)), ((7), (8, 9))]
    """
    for n in tuples:
        yield tuple(tuple(n[j] for j in idx) for idx in idxs) 


        

def inputNormalizer(strings, sep):
    """Make sure no invalid data format (too many columns)
    is specified and remove newlines"""
    iLine = 0
    ncols = None
    while True:
        s = next(strings)
        iLine += 1
        s.rstrip("\n")
        s = s.split(sep)
        if ncols is None: ncols = len(s)
        if len(s) != ncols:
            raise ValueError(("Invalid input in line {}: {} columns "+
            "expected on every input line. Got: {}. (Wrong column separator?)")
           .format(iLine, ncols, len(s)))
        if any(c in x for c in [' ','\t'] for x in s):
            raise ValueError(("Invalid input in line {}: Illegal Whitespace"+
            "found in Nucleotide or CIGAR strings.").format(iLine))
        yield s

def addCIGAR(nucl):
    for n in nucl:
        yield (n, str(len(n))+'M')

def mutatorExpLen(inputTuples, i_prob, i_len, d_prob, d_len ):
    """`inputTuples` is a interable on string tuples `(nucl, cigar)`.
    `cigar` may also be of class CIGAR, this way unnessecary conversions
    to and from strings can be avoided if this method is applied multiple
    times on the same stream of data.

    Insert/delete parts of the nucleotide strings `nucl` (the short read
    nucleotide strings) and document the result by changing the CIGAR
    strings provided by `cigar`. Operation starts with a constant
    per-character (per-base) probability and the operation length is
    exponentially distributed with rate `1/i_len` or `1/d_len`,
    respectively.
    """
    ln2 = math.log(2)
    #rndPos = lambda p: math.floor(random.expovariate(p))+1 if p != 0 else inf
    #rndLen = lambda s: math.floor(random.expovariate(ln2/s))+ 1 \
    #                    if s is not None else None
    rndPos = lambda p: rGeom(p)+1 if p != 0 else inf
    rndLen = lambda s: rGeom(1-s)+1 if s is not None else None
    toCIGAR = lambda x: CIGAR.fromString(x) if isinstance(x,str) else x

    # State automaton:
    # ================
    # -- Possible states:
    NEXT_STRING = 'next_str'  # Optain a new nucleotide string
    DET_NEXT_OP = 'det_op'  # Determine if in/del takes place in this string
    INSERT = 'insert'       # Insert a sequence and get a new insert position
    DELETE = 'delete'       # Delete a sequence and get a new delete position
    YIELD = 'yield'        # Return current, possibly modified string to the caller
    # -- Queue of next states (new states can be inserted at front and at
    #    end)
    todo = [NEXT_STRING]
    # -- Current state:
    l = 0
    nucl, cigar = "", ""
    bpToNextIns  = rndPos(i_prob)-1 # only for the first time may this also be 0
    bpInsLen    = rndLen(i_len) 
    bpToNextDel = rndPos(d_prob) # same as bpToNextIns
    bpDelLen    = rndLen(d_len)
    # -- State transitions:
    # The loop ends if StopIteration is thrown by next(.)
    while True: 
        # Corner case: if all mutation probabilities are 0, return input
        # unchanged
        if bpToNextIns == inf and bpToNextDel == inf:
            yield next(inputTuples)
            continue

        #print(",".join(todo))
        do = todo.pop(0) if len(todo) > 0 else YIELD
        # Tie break by random choice of one of the two actions (insert or
        # delete. The other action is skipped => another exp-distributed
        # number is added to it.
        if do == NEXT_STRING:
            bpToNextIns -= l
            bpToNextDel -= l
            nucl, cigar = next(inputTuples)
            l = len(nucl)
            todo.append(DET_NEXT_OP)

        elif do == DET_NEXT_OP:
            todo.clear()
            if bpToNextIns < bpToNextDel:
                # Check/queue insert operation first
                if bpToNextIns < l: todo.append(INSERT)
                if bpToNextDel < l: todo.append(DELETE)
            elif bpToNextDel < bpToNextIns:
                # Check/queue delete operation first
                if bpToNextDel < l: todo.append(DELETE)
                if bpToNextIns < l: todo.append(INSERT)
            elif bpToNextIns == bpToNextDel:
                assert not (bpToNextIns == inf and bpToNextDel == inf)
                # Skip one of the two operations, randomly
                if random.choice([True, False]):
                    bpToNextIns += rndPos(i_prob)
                else: 
                    bpToNextDel += rndPos(d_prob)
                todo.insert(0, DET_NEXT_OP)
            else: assert False

        elif do == INSERT:
            nucl = insertRandom(nucl, bpToNextIns, bpInsLen)
            cigar = toCIGAR(cigar)
            cigar.operationAt('I',bpInsLen, bpToNextIns)
            print(f'insert {bpInsLen} at {bpToNextIns}')
            l = len(nucl) # String gets longer
            # Skip the insert when calculating the bp to the next operation
            bpToNextDel += bpInsLen
            bpToNextIns += rndPos(i_prob) + bpInsLen
            bpInsLen = rndLen(i_len)
            todo.insert(0, DET_NEXT_OP)

        elif do == DELETE:
            # Deletion stops at end of string if delete position is
            # nearer at `nucl` string end than bpDelLen
            nucl = nucl[:bpToNextDel] + nucl[(bpToNextDel+bpDelLen):]
            cigar = toCIGAR(cigar)
            effDelLen = min(l - bpToNextDel, bpDelLen)
            cigar.operationAt('D',effDelLen, bpToNextDel)
            l = len(nucl) # String gets shorter
            # If an insert operation is pending, it must be recalculated if
            # it is still on this nucleotide string, as that just got
            # shorter.
            bpToNextDel += rndPos(d_prob)
            bpDelLen = rndLen(d_len)
            todo.insert(0, DET_NEXT_OP)

        elif do == YIELD:
            yield (nucl, str(cigar))
            todo.append(NEXT_STRING)
        #print((nucl, str(cigar), f'I={bpToNextIns}/{bpInsLen}, D={bpToNextDel}/{bpDelLen}'))


def insertRandom(string, pos, length):
    """Insert a random sequence into a string
    >>> s = insertRandom('AAAAA', 2, 3)
    >>> [s[0:2], s[5:8]]
    ['AA', 'AAA']
    >>> all(x in 'ATCG' for x in s[2:5])
    True
    """
    s = "".join(random.choice(['A','T','G','C']) for _ in range(0,length))
    string = string[:pos] + s + string[pos:]
    return string

def rGeom(p):
    """Generate a geometrically distributed random number. p is the success
    probability. The numbers are in the range {0, 1, 2,...}"""
    # CDF = 1-(1-p)^(k+1) (CDF of geometric distribution)
    # (1-p)^(k+1) = 1-CDF  (... solve for k ...)
    # k+1 = log(1-CDF)/log(1-p)
    # k = (log(1-CDF)/log(1-p)) - 1
    # insert a uniform random number in [0;1] for CDF to 
    # obtain geometrically distributed numbers
    u = random.random()
    if p == 1 : return 0
    return math.ceil( (math.log(1-u,1-p))-1 )


def zip_samelen(*streams):
    """`streams` are multiple iterables. Does the same as zip, except if
    it throws ValueError if not all streams throw StopIteration at the 
    same time.
    >>> list(zip_samelen([1,2,3],[4,5,6]))
    [(1, 4), (2, 5), (3, 6)]
    >>> list(zip_samelen([1,2,3],[4,5,6,7]))
    Traceback (most recent call last):
    ...
    ValueError: The supplied inputs are of different lengths

    """
    iters = [iter(s) for s in streams]
    sentinel = object()
    while True:
        ret = tuple(next(s,sentinel) for s in iters)
        if all(s is sentinel for s in ret):
            raise StopIteration
        elif any(s is sentinel for s in ret):
            # Not all streams have ended 
            raise ValueError("The supplied inputs are of different lengths")
        else:
            yield ret




def checkPositive(expectedType):
    "For use in parse_arguments"
    def check(value):
        try:
            value = expectedType(value)
            if value <= 0: raise ValueError()
        except ValueError:
            raise argparse.ArgumentTypeError(
                    ("{} is an invalid positive {}"+
                    +"value").format(value,str(expectedType)))
        else: 
            return value
    return check


if __name__ == "__main__": main(sys.argv)

# vim:tw=75

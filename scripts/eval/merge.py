#!/usr/bin/env python

import sys
from collections import OrderedDict
import subprocess as sp
from textwrap import dedent
import random as rnd
import string 
import os
import os.path
import tempfile as tmpf
import atexit 
import time 
import signal

# Set this to true to enable debugging
debug = True

doc = """
Usage: merge.py [options] \\
                -a TAB_A [by[=byNew] [colA[=colAnew]]...]\\
                -b TAB_B [by         [colB[=colBnew]]...] \\
                         
Merge two text tables TAB_A and TAB_B. This is a wrapper around the
UNIX commands `awk`, `sort` and `join`.

TAB_A and TAB_B are merged using the first column specified after the
file name as a key. See examples below.

By default, a natural join is performed, that is: only rows corresponding
to values in TAB_A and TAB_B are inserted in the output. 

Options:
    
    --prefix-a PREFIX  A string which shall be prepended to the column
                       names of TAB_A
    --prefix-b PREFIX  Like prefix-a, but for TAB_B

    --all-a            Do left outer join, i.e. output all fields 
                       from TAB_A
    --all-b            Do right outer join, i.e. output all fields 
                       from TAB_B
    --all              Do full outer join, i.e. --all-a and --all-b
    --empty VAL        Replace missing fields with val if doing outer
                       join. Default: NA
    --a-sorted         Table A is sorted already; do not sort again
    --b-sorted         Table B is sorted already; do not sort again  


"""

def main(argv):
    args = parseArguments(argv[1:])
    # with open(args["a"],"rt") as a_fd:
    #     a_fdno = a_fd.fileno()
    #     header_a = a_fd.readline().rstrip().split("\t")
    # with open(args["b"],"rt") as b_fd:
    #     b_fdno = b_fd.fileno()
    #     header_b = b_fd.readline().rstrip().split("\t")
    if args["a"] == "-":
        llfd_a = sys.stdin.fileno()
    else:
        llfd_a = os.open(args["a"],os.O_RDONLY)

    if args["b"] == "-":
        llfd_b = sys.stdin.fileno()
    else:
        llfd_b = os.open(args["b"],os.O_RDONLY)

    print(args,file=sys.stderr)
    print([llfd_a,llfd_b],file=sys.stderr)

    if llfd_a == sys.stdin.fileno() and llfd_b == sys.stdin.fileno():
        raise ValueError("-a and -b cannot both read from standard in!")

    a_fh = os.fdopen(llfd_a)
    b_fh = os.fdopen(llfd_b)


    header_a = a_fh.readline().rstrip().split("\t")
    header_b = b_fh.readline().rstrip().split("\t")

    print(a_fh.tell())
    print(b_fh.tell())

    # acols, bcols: list of 2-tuples. First value of tuple specifies
    # column name in input, second value of tupls specifies column 
    # name in output (first != second => column is renamed)
    acols = args["acols"]
    bcols = args["bcols"]

    # Check if correct column names specified
    missing_a = [x[0] for x in acols if x[0] not in header_a]
    missing_b = [x[0] for x in bcols if x[0] not in header_b]

    if missing_a or missing_b: 
        raise ValueError('non-existant column names '+','
                .join(missing_a + missing_b) + ' specified!'+
                '\n valid A: {}, B: {}'.format(header_a,header_b))

    # If no columns are specified: add first columns as key (by) columns
    if len(acols) == 0 : acols.append([header_a[0]]*2)
    if len(bcols) == 0 : bcols.append([header_b[0]]*2)
    
    # Output all columns if only by-column (and no additional columns)
    # is specified
    if len(acols) == 1 : acols.extend(
            [(col,col) for col in header_a if col != acols[0][0]])
    if len(bcols) == 1 : bcols.extend(
            [(col,col) for col in header_b if col != bcols[0][0]])

    # Column indices of columns selected for output
    a_cols_i = [header_a.index(x[0]) for x in acols]
    b_cols_i = [header_b.index(x[0]) for x in bcols]

    a_by = acols[0] 
    b_by = bcols[0]
    a_by_i = a_cols_i[0]
    b_by_i = b_cols_i[0]

    # Add pre-/suffixes to all column names from table 1,
    # except key (a_by) column.
    a_cols_print = [cn_new for cn_old,cn_new in acols if cn_old != a_by[0]]
    a_cols_print = [args["prefix_a"] + cn + args["suffix_a"] 
                       for cn in a_cols_print]
    # Add key column, but without pre-/suffix
    a_cols_print = [a_by[1]] + a_cols_print

    # Add pre-/suffixes to cols from table 2, except key column (omitted)
    b_cols_print = [cn_new for cn_old,cn_new in bcols if cn_old != b_by[0]]
    b_cols_print = [args["prefix_b"] + cn + args["suffix_b"] 
                       for cn in b_cols_print]
    
    # Add outer join arguments
    joinargs = []
    if "a" in args["all"] : joinargs.extend(["-a","1"])
    if "b" in args["all"] : joinargs.extend(["-a","2"])
    if args["all"] : # Any join
        # Old versions of join want this, can't take '-o auto'
        fieldspec=",".join(["1.{}".format(i+1) for i in range(0,len(acols))]+
                           ["2.{}".format(i+1) for i in range(1,len(bcols))])
        joinargs.extend(["-e", args["empty"]])
        joinargs.extend(["-o", fieldspec])

    # #namedpipe_a = os.path.join(tmpf.gettempdir(),rnd_string(40))
    # namedpipe_a = os.path.join(rnd_string(40))
    # atexit.register(os.unlink, namedpipe_a)
    # #namedpipe_b = os.path.join(tmpf.gettempdir(),rnd_string(40))
    # namedpipe_b = os.path.join(rnd_string(40))
    # atexit.register(os.unlink, namedpipe_b)
    # 
    # os.mkfifo(namedpipe_a)
    # os.mkfifo(namedpipe_b)

    # sp.Popen("{awk} <&{fd} | sort > {fifo}".format(
    #     awk=awk_select_cols(a_cols_i), 
    #     #tab=args['a'], 
    #     fd = llfd_a,
    #     fifo=namedpipe_a),
    #     shell=True, close_fds=False)
    # sp.Popen("{awk} <&{fd} | sort > {fifo}".format(
    #     awk=awk_select_cols(b_cols_i), 
    #     #tab=args['b'], 
    #     fd = llfd_b,
    #     fifo=namedpipe_b),
    #     shell=True, close_fds=False)

    # cmd = ("join {args} -t '\t' {fifo1} {fifo2}".format(
    #         args = " ".join(joinargs), 
    #         fifo1=namedpipe_a, fifo2=namedpipe_b))

    os.set_inheritable(llfd_a,True)
    os.set_inheritable(llfd_b,True)

    sort_cmd_a = "| LC_ALL=C sort -k1 -t$'\\t'" if not args["a_sorted"] else ""
    sort_cmd_b = "| LC_ALL=C sort -k1 -t$'\\t'" if not args["b_sorted"] else ""

    cmd_taba = "{awk} <&{fd} {sort}".format(
            awk = "cat",
            #awk  = awk_select_cols(a_cols_i),
            fd   = llfd_a,
            #sort = sort_cmd_a 
            sort = "")
    
    cmd_tabb = "{awk} <&{fd} {sort}".format(
            awk = "cat",
            #awk  = awk_select_cols(b_cols_i),
            fd   = llfd_b,
            #sort = sort_cmd_b 
            sort = "")

    cmd = ("join {args} -j1 -t$'\\t' <({input_a}) <({input_b})").format(
            input_a = cmd_taba,
            input_b = cmd_tabb,
            args = " ".join(joinargs))


    #print(a_cols_print + b_cols_print, file=sys.stderr)
    if debug:     
        print("EXECUTE:", file=sys.stderr)
        print(cmd, file=sys.stderr)
        print("----------------------------------",file=sys.stderr)
        print(a_cols_i, file=sys.stderr)
        print(b_cols_i, file=sys.stderr)

    print("\t".join(a_cols_print+b_cols_print)) 
    sys.stdout.flush()

    # Handle SIGPIPE properly, e.g. when piped to head
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    #sp.check_call(cmd_tabb, close_fds=False,shell=True, executable="/bin/bash")
    sp.check_call("cat <&{}|wc -l".format(llfd_a), pass_fds=[llfd_a,llfd_b],shell=True, executable="/bin/bash")
    print("-----------------")
    sp.check_call("cat <&{}|wc -l".format(llfd_b), pass_fds=[llfd_a,llfd_b],shell=True, executable="/bin/bash")

    sys.stdout.flush() 

    return 0

def rnd_string(length):
    chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
    o = rnd.sample(chars, length)
    return "".join(o)

def awk_select_cols(cols_list):
    col_s = ",".join(["$"+str(i+1) for i in cols_list])
    return r'''awk 'BEGIN{OFS="\t";FS="\t"}(NR!=1){print '''+col_s+"} ' "
                    

def parseArguments(argv):
    # Is str a parameter name? (e.g. -a, --bcols)
    def is_parname(str): return str != "-" and str.startswith("-")

    # Get number of parameter before next param name
    def n_args(argv, acc=0): 
        try: 
            if is_parname(argv[0]): return acc
            else:                   return n_args(argv[1:],acc+1)
        except IndexError:          return acc

    def parse_ab(argv,name):
        n = n_args(argv)
        xcols = []
        if n == 0: 
            raise ValueError("-{} needs at least 1 argument!".format(name))
        x = argv.pop(0)
        if n > 1 : xcols = parse_colspec(argv)

        return (x,xcols)

    def parse_colspec(argv):
        n = n_args(argv)
        o = []
        for i in range(1,n+1):
            s = argv.pop(0)
            spl = tuple(s.split("="))
            if len(spl) not in [1,2]:
                raise ValueError("column spec must be col or "+
                                 "col=newname; is: {}".format(s))
            o.append(spl if len(spl) == 2 else (spl[0],spl[0]))
        return o
    
    def getSingleArg(argv,name):
        n = n_args(argv)
        if n_args(argv) != 1: 
            raise ValueError("--{} needs 1 parameter!".format(name))
        return argv.pop(0)

    argv = list(argv) # Do not modify input argv, but modify a copy

    a = None 
    b = None
    acols = []
    bcols = []
    prefix_a = ""
    prefix_b =""
    suffix_a = ""
    suffix_b = ""
    empty = "NA"
    a_sorted = False
    b_sorted = False
    all=set()

    while argv:
        arg = argv.pop(0)
        if  arg == "--help":
            print(doc)
            sys.exit(0)
        elif  arg == "-a":
            a,acols = parse_ab(argv,"a")
        elif arg == "-b":
            b,bcols = parse_ab(argv,"b")

        elif arg == "--suffix-a":
            suffix_a = getSingleArg(argv,"suffix-a")
        elif arg == "--suffix-b":
            suffix_b = getSingleArg(argv,"suffix-b")
        elif arg == "--prefix-a":
            prefix_a = getSingleArg(argv,"prefix-a")
        elif arg == "--prefix-b":

            prefix_b = getSingleArg(argv,"prefix-b")
        elif arg == "--empty": empty = getSingleArg(argv,"empty")

        elif arg == "--all-a": all.update("a")
        elif arg == "--all-b": all.update("b")
        elif arg == "--all":   all.update(["a","b"])
        elif arg == "--a-sorted": a_sorted = True
        elif arg == "--b-sorted": b_sorted = True

        else: raise ValueError("Unknown argument {}".format(arg))

    if not a or not b:
        raise ValueError("-a and -b must be supplied!")


    return {"a":a, "b":b, "acols":acols, "bcols":bcols,
            "suffix_a":suffix_a, "suffix_b":suffix_b, 
            "prefix_a":prefix_a, "prefix_b":prefix_b, 
            "all":all, "empty":empty,
            "a_sorted":a_sorted, "b_sorted":b_sorted}


if __name__=="__main__":
    if "--debug" in sys.argv: 
        debug = True
        sys.argv.remove("--debug")
    try:
        sys.exit(main(sys.argv))
    except Exception as e:
        if debug : raise
        print("Error: ",end="",file=sys.stderr)
        print(e,file=sys.stderr)
        sys.exit(1)


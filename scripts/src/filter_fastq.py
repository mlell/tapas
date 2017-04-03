#!/usr/bin/env python3

import sys
from subprocess import Popen, PIPE
import os

def usage(error=False):
    out = sys.stdout if not error else sys.stderr
    out.write("""

Filter a FASTQ file through part-specific filters.
==================================================

    Usage: filter-fastq.py [-h | --help]\\
            [ --nucleotide @ FILTER-CMD arg1 arg2 ... @ ] \\
            [ --quality    @ FILTER-CMD arg1 arg2 ... @ ] \\
            [ --id         @ FILTER-CMD arg1 arg2 ... @ ] \\
            < input.fastq \\
            > output.fastq

Filters the FASTQ file on standard input through the specified
commands. The @ - Signs can be chosen arbitrarily, per command, but
they must be equal before and after the command string.

The parts of the FASTQ-File are forwarded to the specified commands on
standard input, one record per line. afterwards, the outputs of these
commands are assembled to form the output FASTQ file.

The specified FILTER-CMDs must take one line of input and must output
one line per input line!

ATTENTION: DEADLOCK POSSIBLE DUE TO BUFFERED I/O:
The subcommands may not buffer multiple lines of output before
actually printing them (standard e.g in Python). This script will
hang then because it has to process one line from each subscript at
a time. Ensure that the output buffer of the subprocesses is flushed
after each line by using appropriate switches in interpreter programs
or by calling stdout.flush() equivalents in the subprograms after 
each line of output!

-h or --help   Print this message

--nucleotide   read the next argument and use this as sentinel
--quality      character. Read arguments until this sentinel is read 
--id           again. All ntermediate arguments form the command that 
               is executed for the respective FASTQ part.

""")
    out.flush()
    sys.exit(1 if error else 0)


def main():
    # Are we on a POSIX compliant OS?
    ON_POSIX = 'posix' in sys.builtin_module_names

    # Parse Arguments and declare process handles
    # id_ nc_, qu_ = ID line, nucleotide line, quality line
    # of a FASTQ record
    id_cmd, nc_cmd, qu_cmd = parse_arguments()
    id_prc = None
    nc_prc = None 
    qu_prc = None

    try:
        # Launch processes and set up pipes
        if id_cmd:
            id_prc = Popen(id_cmd, stdin= PIPE, stdout= PIPE,
                           close_fds=ON_POSIX, universal_newlines=True,
                           bufsize=0)
        if nc_cmd:
            nc_prc = Popen(nc_cmd, stdin= PIPE, stdout= PIPE,
                           close_fds=ON_POSIX, universal_newlines=True,
                           bufsize=0)
        if qu_cmd:
            qu_prc = Popen(qu_cmd, stdin= PIPE, stdout= PIPE,
                           close_fds=ON_POSIX, universal_newlines=True,
                           bufsize=0)
        
        # Break if there are no more lines on STDIN, error if incomplete
        # records remain.
        while(True):
            try:
                idline = input_or_error(sys.stdin)
            except EOFError:
                break
            try:
                nclline   = input_or_error(sys.stdin)
                sepline   = input_or_error(sys.stdin)
                qualiline = input_or_error(sys.stdin)
            except EOFError:
                raise EOFError("Incomplete FASTQ record!")
            
            # Input lines to the subprocesses
            if id_prc: 
                write_line(id_prc.stdin, idline)
            if nc_prc: 
                write_line(nc_prc.stdin, nclline)
            if qu_prc:
                write_line(qu_prc.stdin, qualiline)

            if not check_record(idline,nclline,sepline,qualiline):
                raise ValueError(
                "The following input FASTQ record is invalid:\n"+
                str_fastq(idline,nclline,sepline,qualiline))

            newid = readline_strip(id_prc.stdout) if id_prc else idline
            newnc = readline_strip(nc_prc.stdout) if nc_prc else nclline
            newsep = "+" if sepline.rstrip() == "+" \
                         else "+" + newid[1:]
            newqu = readline_strip(qu_prc.stdout) if qu_prc else qualiline

            if not check_record(newid,newnc,newsep,newqu):
                raise ValueError(
                "The following filtered FASTQ record is invalid:\n" +
                str_fastq(newid,newnc,newsep,newqu))
            
            print(newid)
            print(newnc)
            print(newsep)
            print(newqu)

    finally:
        if id_prc: id_prc.stdin.close()
        if nc_prc: nc_prc.stdin.close()
        if qu_prc: qu_prc.stdin.close()

def str_fastq(idline,nclline,sepline,qualiline):
    """ Create a FASTQ record"""
    return "{}\n{}\n{}\n{}".format(idline,nclline,sepline,qualiline)

def check_record(idline,nclline,sepline,qualiline):
    """ Check if the lines of this FASTQ record start with the correct
    symbols"""
    return check_idline(idline) and check_sepline(sepline)

def check_idline(line):
    return line[0] == "@"

def check_sepline(line):
    return line[0] == "+"

def parse_arguments():
    """Separate the command line arguments of this script in 
    arguments forwarded to the filtering commands.
    Returns a triple of string lists: each contains nothing 
    or a command name, followed optionally by command line parameters
    for this command."""
    # shift away script name
    scriptname=sys.argv[0]
    shift()
    ncl_cmd=list()
    quali_cmd=list()
    id_cmd=list() 
    while(len(sys.argv)>0):
        carg = sys.argv[0]
        shift()
        if(carg == "--nucleotide"):
            ncl_cmd = mungeArgs(sys.argv)
        elif(carg == "--quality"):
            quali_cmd = mungeArgs(sys.argv)
        elif(carg == "--id" ):
            id_cmd = mungeArgs(sys.argv)
        elif(carg in ["-h", "--help"]):
            usage()
        else:
            usage(error=True)
    # Excess arguments which are not processed 
    if(len(sys.argv) > 0):
        sys.stdout.write("Excess arguments!\n")
        sys.stdout.flush()
        usage(error=True)

    # external modules rely on non-empty argv array, 
    # re-append the script name as first command line argument
    sys.argv.append(scriptname)
    return (id_cmd, ncl_cmd, quali_cmd)


def readline_strip(stream):
    """Read one line of the given file/stream and remove the trailing 
    newline"""
    assert hasattr(stream,"read")
    line = stream.readline()
    line = line.rstrip("\n")
    return line

def write_line(stream, line):
    """Write one line to the specified stream, and append a newline
    character."""
    assert hasattr(stream,"write")
    stream.write(line)
    stream.write("\n")
    stream.flush()


def input_or_error(stream=sys.stdin):
    """Read one line from the specified stream/file. Raise an 
    EOFError if there are no more lines to be read."""
    line = readline_strip(stream)
    if not line: raise EOFError("End of input")
    return line

def requireArgument(array):
    """Return first element of an array. Raise exception
    if array is empty"""
    if(len(array)==0):
        raise ValueError("one additional argument is \
                needed but not provided!")
    return array[0]

def mungeArgs(array):
    """
    Input: array     [S, a, b, c, S, d, e, f] 
                      xxxxxxxxxxxxx
    MODIFIES array:                 [d, e, f]
    RETURN value:      [ a, b, c ]
    This function has a side effect of modifying the given array"""
    # Define the first element of the array to be the sentinel.
    # Error if no element is found
    sentinel = requireArgument(array)
    shift(array)  
    ret=list()
    # Consume elements until sentinel is reached again
    while(len(array) > 0 and array[0] != sentinel):
        ret.append(array[0])
        shift(array)
    # Remove sentinel from the array. 
    if(len(array) > 0): 
        shift(array)
    return ret

def shift(array=sys.argv):
    """Remove the first argument of an array"""
    array.pop(0)



if (__name__=="__main__"): main()

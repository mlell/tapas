# Helper functions for python pipeline scripts
# Use this file via the python 'include' statement
import re
import ruffus
import itertools
import sys


# Input/Output Helper functions
# ===========================
def echo(*args, **kwargs):
    """
    Print a string s to a file f
    """
    f = kwargs.pop("f",sys.stdout)
    append = kwargs.pop("append",False)
    # Replace or overwrite output file
    mode = "wt" if not append else "at"
    # Concatenate positional arguments to one string to be printed.
    s = " ".join([str(x) for x in args])
    with open(f, mode) as fd:
        if type(s) == list :
            fd.writelines([s+"\n" for s in args])
        elif type(s) == str :
            fd.write(s+"\n")

def read_tab(filename,**kwargs):
    """ 
    Read in a tab-separated file and store it as a list of lists (one list per
    input file line) if the input table contains no header line. If the input
    table contains a header line, a list of dictionaries is returned. 
    """
    with open(filename, "rt") as fd:
        return read_tab_str([l for l in fd],**kwargs)


def read_tab_str(text, sep="\t", header=False):
    if sep == "": sep = None
    tab = [ [ l for l in line.strip().split(sep) ]
            for line in text ]
    if header: 
        colnames = tab.pop(0)
    if header:
        tab = [ dict(zip(colnames, line)) for line in tab ]
    return tab


def dictlist_to_nested_list(tab):
    header = list(tab[0].keys())
    header.sort()
    tab = [ [ line[x] for x in header ] 
            for line in tab ]
    tab.insert(0, header)
        
    return tab
    
def write_tab(tab, filename, sep="\t", mode="wt"):
    if not isinstance(tab, list) :
        raise ValueError("A list is required!")
    
    # If column headers exist
    if hasattr( tab[0] , "keys"):
        tab = tab_values(tab)
    
    # Convert items to strings
    tab = [[str(i) for i in line] for line in tab]
    with open(filename, mode) as fd:
        # Write table to file
        for line in tab:
            fd.write(sep.join(line)+"\n")


# Functions for data structure conversion
# =======================================

def dict_expand(dict_of_lists):
    """
    Converts a dictionary containing lists as values to a list of dictionaries,
    using all combinations of the list values.
    >>> cross_product( {"a" : [1,2] }
                     , {"b" : [3,4] })
    [{'a': 1, 'b': 3}, {'a': 1, 'b': 4}, 
     {'a': 2, 'b': 3}, {'a': 2, 'b': 4}]
    """
    return [ dict(zip(dict_of_lists.keys(),v)) 
             for v 
             in itertools.product(*dict_of_lists.values()) ]

# Functions for simpler Ruffus syntax
# ===================================

def kw_formatter(*args):
    fargs = [ 
       re.sub(pattern=r"\{\*(\w+)\}",
              repl=   r"(?P<\1>\w+)",
              string= s) 
       for s in args ]
    print("My formatter: {}".format(fargs))
    return ruffus.formatter(*fargs)


# vim: tw=80

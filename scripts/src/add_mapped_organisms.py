#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
"""

From tabular information about mapped reads, infer the organisms the
reads should be mapped to, and are actually mapped, from the FASTA
record the reads were mapped to. 
"""

import sys
import argparse
import fasta_substring as fasub
import itertools
import pandas as pd


help_params = {
'readtab':
"""A text table containing at least the following columns. 
Column names can be changed by additional parameters to 
this command:

    ─── readtab ──────────
    qname       rname
    read_0      record1
    read_1      record2
    read_2      *
    read_3      record1
    ...         ...
    ─────────────────────
""",
"--endogenous":
"""A set of endogenous reads. 

ORG is a string holding the
organism"s name, FAI is a .fai file (see samtools) of the
reference genome and RNAME is a file containing a 
newline-separated list of read names which belong to
this organism.""",
"--exogenous":
"""A set of exogenous reads. These reads will carry "*" as 
true organism name. RLIST is a file containing a 
newline-separated list of read names which are considered 
exogenous reads.""",
"--read-col"   : "The name of the read name column of READTAB",
"--record-col" : "The name of the record name column of READTAB"
}

# Character representing a non-mapped read <=> "no organism"
NO_ORGANISM = "*" 

def main(argv):
    args = parseArguments(argv)

    # Run self-test if requested
    if args.doctest: 
        import doctest
        doctest.testmod(verbose=True)
        sys.exit(0)

    # User-chosen names for read sources
    endoOrgNames = [a[0] for a in args.endogenous]
    exoOrgNames = [a[0] for a in args.exogenous] \
            if args.exogenous else []
    # File names of FAI files of read source genomes
    endoFAINames = [a[1] for a in args.endogenous]
    exoFAINames = [a[1] for a in args.exogenous] \
            if args.exogenous else []
    # File names of text tables with true read position information
    endoReadListNames = [a[2] for a in args.endogenous]
    exoReadListNames = [a[2] for a in args.exogenous] \
            if args.exogenous else []
    

    # Lookup table: For every FASTA record name, list the organism
    # name it belongs to (endogenous organisms only)
    endoRecordToOrganismTab = pd.DataFrame()
    for org,FAIName in zip(endoOrgNames, endoFAINames):
        with open(FAIName,'rt') as f:
            FAI = fasub.FastaIndex(f)
        ret = pd.DataFrame()
        record_list = FAI.getNames()
        for record in record_list:
            endoRecordToOrganismTab = endoRecordToOrganismTab.append(
                {'record':record,'mapped_organism':org},
                ignore_index = True)

    endoRecordToOrganismTab = endoRecordToOrganismTab.append(
        {'record':NO_ORGANISM,'mapped_organism':NO_ORGANISM},
        ignore_index = True)


    # Make sure the record names of the endogenous organisms are
    # unique
    if not allUnique(endoRecordToOrganismTab['record']): 
        raise Exception("The record names of all endogenous "+
        "organisms must be all unique among each other!")

    endoRecordToOrganismTab = endoRecordToOrganismTab.set_index(['record'])

    readnameToTrueOrganismTab = pd.DataFrame()

    # Make a lookup table where the true organism of all reads can be
    # looked up
    readname_col = 0

    # Endogenous reads
    for org,readlist_name in zip(endoOrgNames, endoReadListNames):
        readnameToTrueOrganismTab = \
                readnameToTrueOrganismTab.append(
                        prepareReadList(readlist_name, org))
    # Exogenous reads
    for org,readlist_name in zip(exoOrgNames, exoReadListNames):
        r = prepareReadList(readlist_name, org)
        if sorted(r.columns.tolist()) != \
            sorted(readnameToTrueOrganismTab.columns.tolist()):
            raise Exception(
                'All read information tables must have the same columns')
        readnameToTrueOrganismTab = readnameToTrueOrganismTab.append(r)


    readnameToTrueOrganismTab = \
        readnameToTrueOrganismTab.set_index('readname')

    mapped_reads = pd.read_table(args.readtab, delim_whitespace=True)
    c = mapped_reads.columns.tolist()
    c[1:] = ['mapped_'+x for x in c[1:]]
    mapped_reads.columns = c
    mapped_reads = mapped_reads.merge(endoRecordToOrganismTab, \
            how='left', left_on=['mapped_rname'], right_index=True)
    mapped_reads = mapped_reads.merge(readnameToTrueOrganismTab, 
            how='left', left_on=['qname'], right_index=True)


    mapped_reads.to_csv(sys.stdout, sep="\t", index=False)
    

def prepareReadList(readlist_name, org):
    readSourceName = 'organism'
    readlistPrefix = 'true_'

    readlist = pd.read_table(readlist_name,delim_whitespace=True)
    readlist.rename(columns={readlist.columns[0]:'readname'},inplace=True)
    
    try:
        iConflictingCol = readlist.columns.get_loc(readSourceName)
        c = readlist.columns.tolist()
        c[iConflictingCol] = uniquefy(readSourceName,readlist.columns)
        readlist.columns = c
    except KeyError:
        pass

    readlist[readSourceName] = org

    c = readlist.columns.tolist()
    c[1:] = readlistPrefix + readlist.columns[1:]
    readlist.columns = c

    return readlist


# Thanks to Paul McGuire@stackoverflow
def allUnique(x):
    """Returns true if and only if no element in x appears more than
    once
    >>> allUnique([1,2,3])
    True
    >>> allUnique([1,1,3])
    False
    """
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)


def parseArguments(argv):
    p = argparse.ArgumentParser(description=__doc__, 
            formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('readtab', help=help_params['readtab'])
    p.add_argument('--endogenous','--endo', nargs=3,
                   metavar=('ORG', 'FAI', 'RNAMES'),
                   action='append',
                   help=help_params['--endogenous'])
    p.add_argument('--exogenous','--exo',nargs=3,
                   metavar=('ORG', 'FAI', 'RNAMES'),
                  action='append',
                  help=help_params['--exogenous'])
    p.add_argument('--read-col',default="qname",
                  help=help_params['--read-col'])
    p.add_argument('--record-col',default="rname",
                  help=help_params['--record-col'])
    p.add_argument('--doctest', action="store_true",
            help="Run self-tests")
    return p.parse_args(argv)

def uniquefy(name, existingNames):
    if name not in existingNames: return name
    i = 2
    while name+str(i) in existingNames:
        i += 1
    return name+str(i)

if __name__ == "__main__": 
    try:
        main(sys.argv[1:])
    except Exception as e:
        print('ERROR: {}'.format(e),file=sys.stderr)
        sys.exit(1)


# vim:tw=70

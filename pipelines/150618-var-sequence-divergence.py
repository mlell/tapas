#!/usr/bin/env python

from ruffus import *
import subprocess as sp
import sys
import os
import os.path
import sh
import re
from pipeline_helpers import echo, read_tab, write_tab, \
                             cross_product, kw_formatter,\
                             read_tab_str
from shutil import copy
import itertools
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


PYTHON2 = True if sys.version_info[0] == 2 else False

# Define Iterator-zip for Python2/3 compatibility
def zip(*iterables):
    return itertools.izip(*iterables) if PYTHON2 else \
           zip(*iterables)

# Set variables
# =============

# Project root
pr                = os.environ["pr"]
# Script directory
d_sps             = pr+"/mapper-compare"

# Worker Scripts
s_md2geomparam           = sh.Command(d_sps+"/distribution-parametrization/"+
                                     "mapdamage2geomparam.py")
s_filter_fastq      = sh.Command(pr+"/scripts/filter-fastq.py")
str_multiple_mutate = d_sps+"/induce-errors/multiple_mutate.py"
s_map_bwa           = sh.Command(d_sps+"/bwa/map-reads-bwa.sh")
s_eval_mapping      = sh.Command(d_sps+"/eval/eval-mapping.sh")
s_tab2line          = sh.Command(pr+"/scripts/tab2line.py")

# Output directory
d_out             = pr+"/data/gen/150620-ruffus-test"

# Input data
# ==========

#  *  MapDamage
d_in_md=pr+"/data/in/150325_mapdamage_johanna_alex"
#  *  Unmutated Reads
in_reads=pr+"/data/gen/150602-reads/unmut/reads.fastq"

#  *  Mapping: BWA
bwa_ref=pr+"/mapper-compare/bwa/Usp_mito/Usp_mito"

# Output parameters
# =================

# Levels of artificial additional sequence divergence introduced.
mut_levels        = [ 0, 0.01, 0.02, 0.05, 0.1 ]

# Mapper parameters. Each combination of these is tried.

bwa_parameters = { "-n" : [0.04, 0.08, 0.15],
                   "-l" : [ 999, 4 ],
                   "-k" : [ 2, 10 ],
                   "-M" : [ 3, 1, 10 ]}

bwa_par_combinations = cross_product(bwa_parameters)

# --- Determine distribution parameters of mutation -------------------

@follows( mkdir("fit") )
@merge(   input  = d_in_md + "/GS136_*_freq.txt",
          output = "fit/GS136.tab")
def fit_distribution(infiles, outfile):
        s_md2geomparam("--fit-plots", "fit/GS136_fit_plots/", *infiles, 
                   _out=outfile)

# --- Add constant mutation rates -------------------------------------

@follows( mkdir("par/GS136") )
@split(   fit_distribution ,
          "par/GS136/c_*.tab",
          extras=[mut_levels])
def multiple_parameter_tables(infile, outfiles, mut_levels):
    # Clean up previous runs
    for f in outfiles:
        os.unlink(f)

    for l in mut_levels:
        o = "par/GS136/c_{:.2f}.tab".format(l)
        copy(infile, o)
        #     strand  from  to  factor geom_prob intercept filename 
        echo("3       *     *   0      0.1       {} ".format(l),
             f=o, append=True)

# --- Mutate the unmutated.fastq --------------------------------------

@follows( mkdir("fastq/GS136"))
@transform( input  = multiple_parameter_tables 
          , filter = formatter()
          , output = "fastq/GS136/{basename[0]}.fastq")
def mutate_reads(infile, outfile):
    with open(in_reads,"rt") as ifd:
        s_filter_fastq( "--nucleotide", "@"
                      , str_multiple_mutate, infile, "@"
                      , _out=outfile, _in=ifd)


# --- Map the mutated reads -------------------------------------------
# Map the reads for each combination of input parameters.
# the aligned SAM file an a table containing the used parameters are 
# saved.

@follows( mkdir("bwa/GS136") )
@subdivide( input  = mutate_reads
          , filter = formatter()
          , output = [ "bwa/GS136/{basename[0]}_*.bwapar.tab"]
          , extras = [ "bwa/GS136/{basename[0]}"] )
def write_bwa_parameters(infile, outfiles, out_stem):
    # For all combinations of BWA parameters perform a mapping
    for bwa_par in bwa_par_combinations:
        # Generate filename from parameter values
        # Sample string: -l32-n3-o2 from params {-l:32, -n:3, -o:2}
        par_signature = "".join([ k+str(v) for (k,v) in bwa_par.items()])
        tab_name = out_stem+"_"+par_signature+".bwapar.tab"
        if os.path.exists(tab_name): continue
        print("New Parameter file: {}".format(par_signature))
        # Write parameters in file
        write_tab( [bwa_par], tab_name)



@transform( input = write_bwa_parameters
          , filter = formatter(r"bwa/GS136/(c_[0-9\.]+)_(.*)\.bwapar\.tab$")
          , output = "bwa/GS136/{1[0]}_{2[0]}/aln.sam"
          , extras = [ "bwa/GS136/{1[0]}_{2[0]}"
                     , "fastq/GS136/{1[0]}.fastq"])
def map_bwa(infile, outfile, out_stem, fastq_file):
        # BWA mapping call
        # Read parameter file. Table will contain only one line,
        # therefore take only first element of resulting list
        bwa_par = read_tab(infile,header=True)[0]
        # Merge dictionary to flat list
        # { "-a":3, "-b":4 } >> [ "-a", "3", "-b", "4" ]
        par_list = [ [k,v] for (k,v) in bwa_par.items() ]
        par_list = list(itertools.chain(*par_list))
        # Forward this list as parameters to BWA
        if os.path.isdir(out_stem): return
        # Print command parameters for manual correctness check
        echo("BWA: in:",fastq_file,bwa_ref,out_stem,*par_list, 
                f=out_stem+".call")
        s_map_bwa(fastq_file, bwa_ref, out_stem, *par_list)

# --- Evaluate and plot mapping correctness----------------------------

@transform( input  = map_bwa
          , filter = formatter()
          , output = "{subpath[0][0]}.stat")
def eval_bwa(infile, outfile):
    pdfout = outfile[:-5]+".pdf"
    s_eval_mapping("-s", outfile, infile, 25, pdfout)

#.# --- Summarize the evaluation results into one table ----------------
#.
@merge( input  = eval_bwa
      , output = "bwa.eval")
def merge_bwa_eval( infiles, outfile):
    # Get input filenames with removed .stat extension
    fnames_no_ext = [ f[:-5] for f in infiles]
    toMerge = []
    headers = None
    # Convert all statistic tables to one-line format
    # Append to each line the used mapping parameters
    for (f, bn) in zip(infiles, fnames_no_ext):
        # Determine mutation level
        diverg_level = re.search(r"/c_([0-9\.]+)_",bn).group(1)
        # Convert table to one-liners
        statline = s_tab2line(f).split("\n")
        statline = read_tab_str(statline, header=False)
        bwa_params = read_tab(bn+".bwapar.tab")
        # Set headers
        lheader = statline[0] + bwa_params[0] + ["divergence"] 
        if headers == None: headers = lheader
        # Check that headers don't change mid-task
        if lheader != headers: 
            raise ValueException("column/row names of input files differ!")

        toMerge.append(statline[1]+bwa_params[1] + [diverg_level])

    write_tab([headers] + toMerge, filename=outfile)



# =====================================================================

# Start the pipeline

if not os.path.exists(d_out):
    os.mkdir(d_out)

wd = os.getcwd()
os.chdir(d_out)
pipeline_run(multiprocess=4)
os.chdir(wd)


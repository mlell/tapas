#!/usr/bin/env python
from docopt import docopt
import sys
import csv

help="""
Usage: format_file.py [options] TEMPLATE_FILE 

Reads in the text file TEMPLATE_FILE. text in {..} is substituted by respective
column values of the input table.

The input table is read from standard input.
It is a TAB-separated text table. The first line is treated as header line
whose column names can be used in {...} patterns, as described above.

Options:
    --output FILENAME_TMPL  Writes the output to the given file.
                            FILENAME_TMPL should contain {...} expressions,
                            which are replaced by the values of the respective
                            input column. 
    --append                Don't give an error if an output file exists,
                            but append to this file
    --overwrite             Overwrite existing output files
"""

def main(argv):
    args = docopt(help)
    f_tmpl = args["TEMPLATE_FILE"]
    fname_tmpl = args["--output"]
    append = args["--append"]
    overwrite = args["--overwrite"]
    if append and overwrite:
        raise ValueError("--append and --overwrite can not be used together!")
    output_mode = "xt"
    if append:
        output_mode = "at"
    elif overwrite:
        output_mode = "wt"

    with open(f_tmpl,"rt") as fd:
        tmpl = fd.read()

    reader = csv.DictReader(sys.stdin,delimiter="\t", lineterminator="\n")

    for row in reader:
        o = fill_template(tmpl,row)
        if fname_tmpl:
            output_filename = fill_template(fname_tmpl,row)
            with open(output_filename, output_mode) as ofd:
                ofd.write(o)
        else:
            sys.stdout.write(o)
            sys.stdout.flush()


    return 0

def fill_template(tmpl,dict):
    o = tmpl
    for key in dict:
        pat = "{"+key+"}"
        o = o.replace(pat, dict[key])
    return o

if __name__ == "__main__":
    try:
        c = main(sys.argv)
        sys.exit(c)
    except Exception as e:
        sys.stderr.write("ERROR: {}\n".format(e))


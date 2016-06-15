TAPAS
=====

This software package is meant for comparing NGS short read mappers.

Artificial reads can be generated from genome sequences such that their true
mapping positions are known. By comparing these to the positions the reads were
assigned to by the mapper, the sensitivity and specificity of the mapper can be
assessed.

There are means to run mappers with different combinations of parameters, to 
find the optimal set of parameters. 

Additionally, reads can be mutated in a pattern similar to typical damage found
in ancient DNA (aDNA). The effect of this mutations can be inspected as well.

All the scripts are designed with the UNIX philosophy "do one thing and do it 
well" in mind. Therefore an analysis consists of a pipeline of these scripts. 

The universal data format is the text table, a simple text file containing data
in whitespace- or tab-separated columns. The first line serves as header line 
with column names.


Dependencies
-------------

This software package needs the following tools to be installed:

  * R and several R packages
  * Python 3 and several Python packages
  * Standard UNIX tools like `head`, `awk`, `sort`, `join`, `sed`. These are
    included in all Linux and Mac distributions. On Windows you can install
    Cygwin to get these programs. However, this software package is not yet
    tested on Windows.


Installation
------------

As stated above, R, Python 3 and the requireed packages must be installed.

Run `scripts/setup_check_dependencies` to check if all dependencies are met
on your computer. Read the manual for instructions on how to install
packages for R and Python. 

If the dependencies are satisfied, these scripts can be copied to an arbitrary
any location on the computer.


The scripts
-----------

All scripts lie in the `scripts/` folder. Read the manual to get an overview.
Additionally, each script can be executed with the `--help` switch to get 
detailed information about the script's functionality and how it can be tailored
to your specific needs.


The manual
-----------

The manual lies in the `manual/` folder. Open the file `manual/manual.html`
with your browser.

If you just want to read the manual, and use the software, you can stop reading
here. In the following the generation process of the manual is explained.

The manual is written in a literate programming style with executable examples
weaved into the text. It can be compiled from the markdown-formatted chapters
in the `manual/src/` folder by using the script `gen-html.sh`. In the process,
the program calls written in the manual are executed and the output is weaved
into the manual text. Samtools and the mapper BWA is needed for the examples
and Pandoc is needed to convert the resulting Markdown document into HTML.


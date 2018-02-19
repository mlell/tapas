TAPAS
=====

This software package is meant for comparing NGS short read mappers.

Artificial reads can be generated from genome sequences such that their true
mapping positions are known (`scripts/uniform`). Artificial point mutations
(`scripts/multiple_mutate`) and indels (`scripts/indel`) can be introduced.
By comparing the original read locations to the positions the reads were 
assigned to by the mapper, the sensitivity and specificity of the mapper can 
be assessed.

By running the mapper with different combinations of parameters, an optimal
parameter set can be found (`scripts/cross_tab` and `scripts/table2calls`).
TAPAS is compatible with all short read mappers by through a simple text
file which contains the mapping command and the relevant parameters. Instead
of the parameter values, bash variables (`${variablename}`) are used. They
are replaced with the mapping parameter values to be tested by TAPAS. 

Additionally, reads can be mutated in a pattern similar to typical damage found
in ancient DNA (aDNA) (`scripts/mapdamage2geomparam`). The effect of this 
mutations can be inspected as well.

All the scripts are designed with the UNIX philosophy "do one thing and do it 
well" in mind. Therefore an analysis consists of a pipeline of these scripts.

The universal data format is the text table, a simple text file containing data
in whitespace- or tab-separated columns. The first line serves as header line 
with column names.

The manual
-----------

The availabe tools are described in-depth in the TAPAS manual. 
The manual is located in the `docs/` folder. Open the file `docs/index.html`
inside the TAPAS folder with your browser to view it. 

The manual can also be found online, [click here](https://mlell.github.io/tapas).

There is also one **example script** which summarises the steps of the manual.
It can be found at `manual/example-manual.sh`.

To get help about one specific TAPAS tool, execute the tool with the option
`--help`. Each tool prints then an extensive help page which explains how
to use it. Example: `TAPAS/scripts/uniform --help`, where `TAPAS` is the
folder you installed TAPAS to, prints the help of the artificial read 
generation tool `uniform`.

Installation
------------

This software package needs the following tools to be installed:

  * R >= 3.2 
  * Python >= 3.4 and Pip, the Python package manager
  * Standard GNU tools like `head`, `awk`, `sort`, `join`, `sed`. These are
    included in all GNU/Linux and Mac distributions. On Windows you can install
    Cygwin to get these programs. However, this software package is not yet
    tested on Windows.

These are the commands needed to install these dependencies on your 
system. Select those which match your GNU/Linux distribution:

**Ubuntu** and derivatives, like **Scientific Linux** and **Linux Mint**:

    sudo apt-get install r python3 python3-pip

**CentOS** or **Red Hat Linux**:

    sudo yum --enablerepo=extras install epel-release
    sudo yum install r python3 python3-pip


To install TAPAS, first download it from the 
[Releases section](https://github.com/mlell/tapas/releases)

Then, execute the script 

    TAPAS/scripts/gen/install_dependencies

where you replace `TAPAS` by the folder where you installed TAPAS into. The
tool downloads and installs the needed R and Python packages. The packages 
are installed inside the TAPAS folder and do no affect the rest of the system.

If you want to run TAPAS using R and Python packages which are installed 
globally on your system, instead of the `install_dependencies` script, run

    TAPAS/script/gen/gen-launchers.sh --ext-libs

To check if all dependencies are met, run

    TAPAS/scripts/setup_check_dependencies

on your computer. 

The scripts
-----------

All scripts lie in the `scripts/` folder. Read the manual to get an overview.
Additionally, each script can be executed with the `--help` switch to get 
detailed information about the script's functionality and how it can be tailored
to your specific needs.


The manual is written in a literate programming style with executable examples
weaved into the text. It can be compiled from the markdown-formatted chapters
in the `manual/src/` folder by using the script `gen-html.sh`. In the process,
the program calls written in the manual are executed and the output is weaved
into the manual text. Samtools and the mapper BWA is needed for the examples
and Pandoc is needed to convert the resulting Markdown document into HTML.


---
title: 
  - Generate mapper calls
---

A call is an order to the computer to execute a program. It is a
string which contains the program name and can include variables which
will be set in advance to executing the program and which influence
the program. 

We will in the following generate calls to start our favourite mapper
(BWA in this tutorial) with different combinations of parameter
values. The results will be analysed in coming sections to determine
the effects of the parameter values on the mapping result.

General procedure
-------------------

Here are the main steps which will be taken in subsequent subsections: 

 1. To generate the calls to the mapper using different combinations of 
    parameters, several files holding the values of the different parameters
    are first combined to a table holding all possible combinations of them.

 2. Subsequently, in this tutorial every line is given a unique index.
    Though this is not nessecary, it facilitates tasks like the naming of
    output files.  

 3. Because every mapper is different in how it expects the parameter
    values, you will be expected to write a small script which feeds 
    the parameter values into the mapping program. This will be explained 
    further below.

How the parameter values are stored
-----------------------------------

The parameter values are saved in several files, one per parameter. 
In this example, the BWA parameters n and k are varied which results
in two files:

For your project, you will of course create your own files which hold
the parameter values you want to compare

Here is a list of the parameter files used in this tutorial:

```{.bash}
ls data/mapping/*.par
```
```{.output}
data/mapping/k.par
data/mapping/n.par
```
The files can have arbitrary filenames. They are in a tabular format
where the column names determine the variable names which will be used in
the mapping script which is created later on.

```{.bash}
column -t data/mapping/n.par
```
```{.output}
n
0
4
8
```

Generate combinations of parameter values
-----------------------------------------

To generate all combinations of parameters, `scripts/cross_tab` 
will be used. It expects multiple files and outputs all
possible combinations of their lines. 

Generate all possible combinations of parameters, retaining 1 header
line:

```{.bash}
scripts/cross_tab --head 1 data/mapping/*.par > data/4/partab
head data/4/partab | column -t
```
```{.output}
k   n
2   0
2   4
2   8
10  0
10  4
10  8
```

Mark the parameter combinations with a unique index
----------------------------------------------------

As stated above, this is not nessecary, but facilitates the 
naming of the output text files.

Again, `scripts/index_column` can be used for this purpose. 
This script prepends a counting number to each input line. It can be used to 
generate index columns for text tables.

Add an index column called runidx:
```{.bash}
scripts/index_column --colname runidx --inplace data/4/partab
head data/4/partab | column -t
```
```{.output}
runidx  k   n
0       2   0
1       2   4
2       2   8
3       10  0
4       10  4
5       10  8
```

The mapping script
-------------------

Read now the script `data/mapping/map-bwa.sh`. 

```{.bash}
#!/bin/bash

## This script performs a mapping using BWA.
## It requires the variables k, n, runidx and fastq be set 
## prior to its execution.

# Fail if any needed variable is not set
set -ue

bwa aln -n ${n} -k ${k}      \
    data/genome/volpertinger \
    data/3/all.fastq         \
    > data/4/${runidx}.sai   \
    2> data/4/${runidx}.log   &&

bwa samse                      \
      data/genome/volpertinger \
      data/4/${runidx}.sai     \
      data/3/all.fastq         \
      > data/4/${runidx}.sam   \
      2>> data/4/${runidx}.log

```

As you can see, the script uses several variables, denoted like this:
`${variable}`. These are not defined inside the script, but will be
set from outside at the time this script will be run. 

The variable names are exactly equal to the column names of
the file `data/4/partab` and therefore to the column names of all the
files which lie in `data/mapping/*.par`. They are the means how the
different parameter values will be fed to the mapper.

You will be required to write a script like this for your mapper. All
it must do is to call the mapper, to specify the output file names
and to forward the parameters values on to the mapper using the
`${variable}` syntax.

Generate mapper calls
---------------------

The script `table2calls` converts the table with the parameter value
combinations and the filename of the mapping script to calls which
can be executed on the shell. 

```{.bash}
# Convert the table into calls that can be executed in the next section
scripts/table2calls  data/4/partab \
                    data/mapping/map-bwa.sh \
                  > data/4/calls
cat data/4/calls
```
```{.output}
runidx=0 k=2 n=0 data/mapping/map-bwa.sh
runidx=1 k=2 n=4 data/mapping/map-bwa.sh
runidx=2 k=2 n=8 data/mapping/map-bwa.sh
runidx=3 k=10 n=0 data/mapping/map-bwa.sh
runidx=4 k=10 n=4 data/mapping/map-bwa.sh
runidx=5 k=10 n=8 data/mapping/map-bwa.sh
```

Executing multiple mapping runs in parallel
===========================================

For this task, many programs can be used, from simple shell background
spawning using & (in bash) to job managers orchestrating a big network
of worker machines. In this package, a simple program is implemented
which executes a user-definable number of jobs in parallel and
waits with spawning new ones until another of its already started jobs
finishes.

Note that some mappers can use more than one processor core
themselves. Therefore if you spawn multiple mapper processes where
each mapper process utilizes multiple cores, the total number of
utilized cores is the number of cores used per mapper multiplied with
the number of mapper processes launched in parallel.

Invoke `scripts/mcall --help` to get more information about
this tool.

Example: Run the previously generated mapper calls. 

```{.bash}
    # Execute calls, at 2 cores
    scripts/mcall -c data/4/calls -t 2 \
                  --status
    # Standard error was piped to log files,
    # Standard output was piped to sam files, as specified in the
    # `tmpl` file.
    head data/4/0.log
    head -n15 data/4/0.sam
```
```{.output}
[bwa_aln_core] calculate SA coordinate... 0.00 sec
[bwa_aln_core] write to the disk... 0.00 sec
[bwa_aln_core] 75 sequences have been processed.
[main] Version: 0.7.15-r1140
[main] CMD: bwa aln -n 0 -k 2 data/genome/volpertinger data/3/all.fastq
[main] Real time: 0.068 sec; CPU: 0.003 sec
[bwa_aln_core] convert to sequence coordinate... 0.00 sec
[bwa_aln_core] refine gapped alignments... 0.00 sec
[bwa_aln_core] print alignments... 0.00 sec
[bwa_aln_core] 75 sequences have been processed.
@SQ	SN:A1	LN:6000
@SQ	SN:A2	LN:6000
@SQ	SN:A3	LN:6000
@SQ	SN:B1	LN:6000
@SQ	SN:B2	LN:6000
@SQ	SN:B3	LN:6000
@SQ	SN:B4	LN:6000
@SQ	SN:MT	LN:6000
@SQ	SN:X	LN:6000
@PG	ID:bwa	PN:bwa	VN:0.7.15-r1140	CL:bwa samse data/genome/volpertinger data/4/0.sai data/3/all.fastq
volpertinger_1	4	*	0	0	*	*	0	0	TTGTACCAGTTATTAGTCAATCAGAT	FFFFFFFFFFFFFFFFFFFFFFFFFF
volpertinger_2	4	*	0	0	*	*	0	0	TCTAGTTCCTAACTTTTCCC	FFFFFFFFFFFFFFFFFFFF
volpertinger_3	4	*	0	0	*	*	0	0	GTAAACTTTATCTTCTGGGGCCGA	FFFFFFFFFFFFFFFFFFFFFFFF
volpertinger_4	4	*	0	0	*	*	0	0	TCAAGAAGTTTTCTACTTAGC	FFFFFFFFFFFFFFFFFFFFF
volpertinger_5	4	*	0	0	*	*	0	0	TACGATGTCGATGTTGGATCAGG	FFFFFFFFFFFFFFFFFFFFFFF
```




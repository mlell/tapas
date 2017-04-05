---
title:
  - Input files
---

In this tutorial different parameters for the short read mapper BWA will be 
compared for their recall and accuracy in mapping damaged reads to a refence
genome. 

This chapter explains the input files needed for this tutorial.

Reference genomes
----------------

A genome must be provided from which sample reads can be generated. Two types of
genomes are needed: The genome to which reads shall be mapped is called genome
of an *endogenous* species. The genome (or genomes) from which contaminant reads
stem (e.g. soil bacteria or humans) is called genome(s) of *exogenous* species.

In this tutorial, mutated reads of the genome `data/genome/volpertinger.fasta`
shall be generated and mapped back to that genome. Therefore, `volpertinger` is
the endogenous species. 

The file `data/retli/retli_tr.fasta` contains an excerpt (if this were not a
demonstration, the whole genome would be used, of course) genome of the soil
bacterium *R. etli*. Reads from this genome will be generated as exogenous,
contaminant reads.

Read Mutation probabilities
---------------------------

In order to simulate mutation of the synthetic reads, probabilities that a
mutation happens must be set. An example of this can be found in the file
`data/mut-tables/mut.tab`, which is shown below

```{.bash}
cat data/mut-tables/mut.tab
```
```{.output}
strand   from   to   factor  geom_prob  intercept
3        C      T    0.3     0.4        0.1
5        C      T    0.1     0.2        0.0
3        *      *    0.0     0.1        0.12
```

These mutation parameters can be set to user-defined values. If different
sets of mutations are to be compared, multiple files of this format can be
created using the script `fill_template`.

Alternatively, a file like shown above can be created by deriving the mutation
parameters from mapDamage output. Both possibilities are detailed in the section
about introducing read mutations.

Mapping script
--------------

As mappers are different in the way they are called, a shell script must be
created which forwards the values of the parameters to the mapper. The script
will be called for each combination of mapping parameters to be tested. 
The script must use variables for each parameter which varies in the comparison.

An example for the short read mapper is given below.

```{.bash}
#!/bin/bash

## This script performs a mapping using BWA.
## It requires the variables k, n and runidx be set 
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

The script reflects the common procedure of short read mapping using BWA: First,
`bwa aln` is called to map a set of reads (`all.fastq`) to a reference genome 
(`volpertinger`). Afterwards, the command `bwa samse` is used to convert the
output of the mapper to the SAM format. 

Note that the script contains the variables `${n}`, `${k}` and `${runidx}`,
which are not set to any values inside the script.  For each of the variables,
different values will be provided for each time a mapping is performed with a
different set of mapping parameters. 

As will be detailed later, `${runidx}` serves as a run index, taking counting
values, the values for the variables `${n}` and `${k}` will be provided starting
from a set of parameter files which will be shown in the following. 

Parameter files
---------------

The parameter values which are to be compared must be written into dedicated
files. For each parameter which is to be tested in differing combinations with
other parameters, one file must be created. Parameters which always vary
together must be written into the same file.

To compare different combinations of parameter values, the lines of these files
will be merged in different combinations and the mapping script mentioned above
will be run for each combination. 

Example files, which are used in this tutorial, can be seen in he folder
`data/mapping` and are printed below. The file names are arbitrary, however, the
column names (first line of each file) determines the name of the variable in
the mapping script (previous section) which will take the values of that column.

In the following, the file contents are printed:

```{.bash}
cat data/mapping/k.par
```
```{.output}
k
2
10

```

```{.bash}
cat data/mapping/n.par
```
```{.output}
n
0
4
8
```

It can be seen that the first line of each file contains a name for the
parameter (in this case, the letters k and n, respectively). This name will be
used later on in the mapping script each time when the parameter value must be
inserted. 








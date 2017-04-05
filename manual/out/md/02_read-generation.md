---
title: 
  - Generation of simulated read sets
---

Two sets of reads are needed:

 * *Endogenous reads* mimic *ancient DNA* reads which shall be mapped to a
   reference
 * *Exogenous reads* mimic contaminant DNA which should not be mapped to the
   reference

Generating endogenous reads
---------------------------

In this tutorial, endogenous reads are generated from the sample genome 
`volpertinger.fasta`, which is stored in the `data/genome` folder of this
manual. The script `uniform` is used to sample reads uniformly from the
reference: 

```{.bash}
scripts/uniform data/genome/volpertinger.fasta \
    --seed 1234 \
    --name volpertinger_ \
    --output-fastq data/2/volpertinger.coord data/2/volpertinger.fastq \
    25 20 5
```
```{.output}
```

The call is explained in the following:

The output files are `volpertinger.fastq` and `volpertinger.coord`. They contain
the generated reads and the positions on the reference from which they were
extracted, respectively. 

The parameter `--seed` is used to initialize the random number generator to a 
defined state. Calling `uniform` with same seed value and same input yields the
same set of reads. If you don't specify `--seed`, you will generate different reads each
time you call this script. 

The parameter `--name` specifies a prefix for the names the
generated reads get, to identify them in the SAM file once they were mapped.


Generating exogenous reads
--------------------------

In this tutorial, contaminant reads are generated from the genome 
`retli_tr.fasta`, which is a part of the *Rhizobium etli* genome. 

The process of read generation is very similar to the previous section:

```{.bash}
scripts/uniform data/retli/retli_tr.fasta \
    --seed 1235 \
    --name retli_ \
    --output-fastq data/2/retli.coord data/2/retli.fastq \
    50 20 5
```
```{.output}
```

Read quality scores
-------------------

The generated reads have only `FFFF.....` as base quality scores, if you want
more control over the read generation process, see the section "Advanced read
generation". 



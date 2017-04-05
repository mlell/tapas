---
title:
- Appendix A2: Advanced read generation
---

Advanced read generation
=======================

The output FASTQ file will be constructed by interleaving the contents
of three files, containing the read names, the nucleotide strings and
the quality strings, respectively. These files will be generated in
the following.

Additionally, a table containing the read names with the true read
positions will be created, to evaluate later on whether a read was
mapped correctly.

By adding additional custom steps between the steps shown here it is
possible to match advanced requirements to the generated reads.

Create the subfolder which holds the generated files:

```{.bash}
mkdir data/2e
```
```{.output}
```

Generate nucleotide strings and read names
------------------------------------------

The `uniform` script can be used to sample reads from a reference
genome. The script needs a FASTA file as input, as well as the desired
amount of reads to be generated, the minimum length and the decay
length. The read lengths are exponentially distributed; the decay
length parameter specifies the length by which half of the reads are
longer than the minimum read length.

For the FASTA file, an index file must exist which was generated in
the previous section using samtools.

Example: Extract 25 reads, with minimum length 20 basepairs, where
half of the reads have a length longer than 25 bp. The value 123 
is used to initialize the random number generator, i.e. can be used to
obtain reproducible reads. This last parameter can be omitted.

The resulting output will be a raw list of nucleotide sequences and a
table containing three columns:

 1. The FASTA record name (e.g. chromosome) where the read originated.
 2. 1-based base number of the reads' first base.
 3. 1-based base number of the reads' last base.


The base indices are 1-based because base indices are 1-based in
SAM-files as well. (whereas in BAM-files, they are 0-based, but we
don't need to deal with BAM-files here.)

We will generate sample reads from our sample genome of a
volpertinger.

Execute the following script to generate random nucleotide sequences:

```{.bash}
scripts/uniform data/genome/volpertinger.fasta \
    --seed 1234 \
    --output data/2e/volpertinger.coord data/2e/volpertinger.nucl \
    25 20 5
```
```{.output}
```

Two files are generated when the `--output` switch is used, as is the
case above: One holds the read names and coordinates and the other one 
holds the raw nucleotide sequences. When omitting ``--output``, all
information is printed in tabular form on the standard output and not
saved to distinct files.

The resulting files look like this:

```{.bash}
head data/2e/volpertinger.coord | column -t
```
```{.output}
record  start  end
B1      2143   2168
MT      3402   3421
A3      1413   1436
A3      5689   5709
MT      3280   3302
A3      4936   4960
A1      1320   1340
A3      4480   4504
X       2381   2400
```

Putting together the FASTQ file
-------------------------------

This task needs three input files: 

  1. The list of read names
  2. The list of nucleotide strings 
  3. The list of quality strings

The first list is extracted from the file `volpertinger.coord`, the second
list exists already (`volpertinger.nucl`) and the third list is generated
using standard UNIX tools from the nucleotide strings

Read names
----------

In this tutorial we generate read names consisting of the organism
name (*volpertinger*) followed by an underscore and a counting number.

To have the origin information of the reads available along with their
newly-generated reads, it is advisable to add the read names to the
`volpertinger.coord` file generated above.

There is a script included for adding this kind of column, which is
shown in the next code example. You can as well use `awk` or whichever
tool you like to accomplish this task if you need more sophisticated
read names. 

```{.bash}
scripts/index_column  --prefix volpertinger_ \
                      --colname name  \
                      --inplace data/2e/volpertinger.coord

head data/2e/volpertinger.coord | column -t
```
```{.output}
name            record  start  end
volpertinger_0  B1      2143   2168
volpertinger_1  MT      3402   3421
volpertinger_2  A3      1413   1436
volpertinger_3  A3      5689   5709
volpertinger_4  MT      3280   3302
volpertinger_5  A3      4936   4960
volpertinger_6  A1      1320   1340
volpertinger_7  A3      4480   4504
volpertinger_8  X       2381   2400
```

To use the read names to generate a FASTQ file, they must be available
as a raw list without additional columns or a header. `awk` can be
used to perform this task:

```{.bash}
awk '(NR!=1){print $1}' \
      data/2e/volpertinger.coord \
    > data/2e/volpertinger.i

head data/2e/volpertinger.i
```
```{.output}
volpertinger_0
volpertinger_1
volpertinger_2
volpertinger_3
volpertinger_4
volpertinger_5
volpertinger_6
volpertinger_7
volpertinger_8
volpertinger_9
```

Quality strings
---------------

Currently, the effect of quality strings on the mapping result has not
been investigated. Currently only strings of constant quality score
are used. This can be done by the UNIX `sed` tool, which replaces every 
character by an F:

```{.bash}
sed 's/./F/g' \
      data/2e/volpertinger.nucl \
    > data/2e/volpertinger.q

head data/2e/volpertinger.q
```
```{.output}
FFFFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
```

If you want to generate more elaborate quality strings, you are free
to do so using whichever tools you desire. Just generate a list with as
many lines as there are nucleotide strings in `volpertinger.nucl` to input them 
into the pipeline.

Putting the FASTQ file together
-------------------------------

The `synth_fastq` tool creates a FASTQ file from its components,
nucleotide string, quality string and read name (ID line). If the file
containing the read lines is omitted, the reads are numbered
sequentially.

```{.bash}
scripts/synth_fastq data/2e/volpertinger.nucl \
                    data/2e/volpertinger.q    \
                    data/2e/volpertinger.i    \
    > data/2e/volpertinger.fastq

head data/2e/volpertinger.fastq
```
```{.output}
@volpertinger_0
TTCCACAAGATATTAGCCAACCAGAT
+
FFFFFFFFFFFFFFFFFFFFFFFFFF
@volpertinger_1
TCTATTTAATAACTTCTCCC
+
FFFFFFFFFFFFFFFFFFFF
@volpertinger_2
TTGAACTCTATCTTCCGGGGCTCA
```

Repeat the above steps to generate contaminant reads
----------------------------------------------------

This commands generate some reads from a truncated *Rhizobium etli*
genome, to supply reads which are not supposed to map. This way,
contamination with non-endogenous reads are simulated.

The endogenous (`volpertinger.fastq`) and contaminant (`retli.fastq`) 
read will be merged into one fastq file (`all.fastq`) once the
sample reads have undergone mutation simulation. This will be 
done in the next section.

Note that two kinds of abbreviations are used here:

 *  Terms like `const_{a,b,c}` are expanded by `bash` to `const_a
    const_b const_c` and can therefore be used to specify mulitple
    paths which share some parts. 
 *  The temporary files (similar to `volpertinger.q` and `volpertinger.i` 
    above) are omitted here by using `bash`'s *process substitution*
    (`<(...)`) which uses the output of one argument instead of a file
    name which the other command expects.

If you do not understand why these commands are equivalent to the
commands listed above used to generate `reads.fastq`, you can use
these as well without problems.

Index genome and sample nucleotide seqences:
```{.bash}
samtools faidx data/retli/retli_tr.fasta

scripts/uniform \
    data/retli/retli_tr.fasta \
    --seed 2345 \
    --output data/2e/retli.{coord,nucl} \
    25 20 5
```
```{.output}
```

Read names:

```{.bash}
scripts/index_column  --prefix retli_ \
                      --colname name  \
                      --inplace data/2e/retli.coord
```
```{.output}
```

Put the FASTQ together:

 * Quality strings are generated without an intermediate file using 
   `sed`
 * Read names are extracted without an intermediate file using `awk`


```{.bash}
scripts/synth_fastq \
    data/2e/retli.nucl \
    <(sed 's/./F/g'           data/2e/retli.nucl) \
    <(awk '(NR!=1){print $1}' data/2e/retli.coord) \
    > data/2e/retli.fastq

head data/2e/retli.fastq
```
```{.output}
@retli_0
TCGTTCTTGTAGCCTTCCGGGAA
+
FFFFFFFFFFFFFFFFFFFFFFF
@retli_1
ACTGAAGCGCAAGCTCTGAA
+
FFFFFFFFFFFFFFFFFFFF
@retli_2
TGGCCGAGGGACGCTTGCGTCG
```




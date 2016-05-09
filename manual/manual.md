<span class="title">The TAPAS manual</span>

Dependencies of the scripts
===========================

The scripts consisting this software depend on 

  * A Python 3 installation
  * R

Furthermore, the scripts depend on several packages which are
included.



vim:tw=70
Genome Preparation
==================

 
Record index table
------------------

First, index the genome using `samtools`. This is needed for several
downstream tools:
```{.bash}
samtools faidx data/genome/sample.fasta
```
```{.output}
```



Generating sample reads
=======================

The output FASTQ file will be constructed by interleaving the contents
of three files, containing the read names, the nucleotide strings and
the quality strings, respectively. These files will be generated in
the following. 

Additionally, a table containing the read names with the true read
positions will be created, to evaluate later on whether a read was
mapped correctly.

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
    --output data/2/volpertinger.coord data/2/volpertinger.nucl \
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
head data/2/volpertinger.coord | column -t
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

```
head data/2/volpertinger.nucl | column -t
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
scripts/index-column  --prefix volpertinger_ \
                      --colname name  \
                      --inplace data/2/volpertinger.coord

head data/2/volpertinger.coord | column -t
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
      data/2/volpertinger.coord \
    > data/2/volpertinger.i

head data/2/volpertinger.i
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
      data/2/volpertinger.nucl \
    > data/2/volpertinger.q

head data/2/volpertinger.q
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

The `synth-fastq` tool creates a FASTQ file from its components,
nucleotide string, quality string and read name (ID line). If the file
containing the read lines is omitted, the reads are numbered
sequentially.

```{.bash}
scripts/synth-fastq data/2/volpertinger.nucl \
                    data/2/volpertinger.q    \
                    data/2/volpertinger.i    \
    > data/2/volpertinger.fastq

head data/2/volpertinger.fastq
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
    --output data/2/retli.{coord,nucl} \
    25 20 5
```
```{.output}
```

Read names:

```{.bash}
scripts/index-column  --prefix retli_ \
                      --colname name  \
                      --inplace data/2/retli.coord
```
```{.output}
```

Put the FASTQ together
 * Quality strings are generated without an intermediate file using 
   `sed`
 * Read names are extracted without an intermediate file using `awk`


```{.bash}
scripts/synth-fastq \
    data/2/retli.nucl \
    <(sed 's/./F/g'           data/2/retli.nucl) \
    <(awk '(NR!=1){print $1}' data/2/retli.coord) \
    > data/2/retli.fastq

head data/2/retli.fastq
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



vim:tw=70
Mutation of reads
=================

Mutation probabilities
----------------------

The reads are mutated using per base probabilities derived from the
geometric distribution. The mutation probability at the read ends is
the highest. By this, the chemical damage near read ends can be
modelled. For this, three parameters are important:

  * The base-independent mutation probability $t$ ($0<t<1$). This is
    the probability of any base to mutate, regardless of its proximity
    to the end of the read. This can be used to model evolutionary
    distance.

  * The steepness $p$ ($0<p<1$) of the mutation probability decline
    when moving away from the read end. The higher this parameter the
    steeper is the decline of mutation probability when moving away
    from the read end.

  * The multiplying factor $f$. At the read end, $f+t$ is the
    probability of the first base of the read to be mutated.

With this model, its possible to archive mutation probabilities
greater than one. This makes of course no sense and the mutation
probability is cut back to one in such cases.

In mathematical notation, the mutation probability $P_{mut}$ of a base
number $x$, starting to count at the reads' end, is:

$$P_{mut}(x) = f \cdot dgeom(x;p) + t$$

with $dgeom(X;P)$ being the density function of the geometric
distribution, with parameters X = number of tries; P = success probability.

The following sketch graphs illustrate the three parameters:

<img src="fig/mut.svg" width="800" />

Specifying the parameters
-------------------------

The mutation probabilities are saved as a text table. It looks like
this:

```{.bash}
cat data/mut-tables/mut.tab
```
```{.output}
strand   from   to   factor  geom_prob  intercept
3        C      T    0.3     0.4        0.1
5        C      T    0.1     0.2        0.0
3        *      *    0.0     0.1        0.12
```

The columns have the following meaning:
 
  * strand:  [3 or 5] On which end of the read should base 1 be
    located, the base with the highest mutation probability
  * from: [Letter or *] Which bases should mutate according to this
    lines' parameters. * means this rule applies to every base.
  * to:   [Letter or *] Which base should a mutation event yield. 
          * means a base (A,T,C,G) different from the original base
          is chosen at random.
  * factor: $f$ from the previous section
  * geom_prob: $p$ from the previous section
  * intercept: $t$ from the previous section

In the example above, a base is $x$ bp away from the 5' end of
a read of length l. That means, it is $(l-x)$ bp away from the 3' end
of the read. The exchange probability depends on the type of the
nucleotide and on $x$:

Base at position $x$ is not Cytosine:

$$P_{\ast\rightarrow\ast}(x) = 0 \times dgeom(x;0.1) + 0.12 = 0.12 = 
P_{\ast\rightarrow\ast}$$

Base at position $x$ is Cytosine (C): 

$$P_{C\rightarrow T}(x) = P_{\ast\rightarrow\ast} + 
          (0.3\times dgeom(x;0.4) + 0.1) + 
          (0.1\times dgeom((l-x);0.2) + 0.0) $$

Mutate a sequence
-----------------

The `multiple-mutate.py` tool takes a table of the previous section as
input and mutates strings provided to it on standard input
accordingly. 

Mutations can be inserted either before a FASTQ file is assembled
(`synth-fastq.py`, see previous section), or afterwards. This example
uses raw nucleotide strings generate during the creation of our
*volpertinger* samples. This serves well as an example how nucleotide
strings are processed line by line and mutated. You can see the
mutations in this example showing up as lower-case letters. 

```{.bash}
scripts/multiple_mutate\
    data/mut-tables/mut.tab \
    < data/2/volpertinger.nucl \
    | head
```
```{.output}
TTCTACAAGtTATTcGCCtACCAGAT
TCTATgaAATAACTTCTCgC
aTtAACcTTATCTTCTGGGGCTCA
TCcTGgGGcTTTCTATTTAGA
TATGtCCgCGATGTTcGATCAGG
ACCCAgGcGCCCCCAGCCtaGTTGa
TGccAATAGCaCTGaGTTTcT
AATAAACTTAAAtAAATTAGTGGCA
ACGATGACCATCTTtTTGCG
cATGaTATTTGccATATATGgAGcTTGTGTG
```

An already existent FASTQ file can be mutated using the `filter-fastq`
tool in cooperation with `multiple-mutate`. The tool `filter-fastq`
enables you to apply transformations to existing fastq files. To this
effect, `filter-fastq` extracts one part out of a FASTQ file (read
name, nucleotide string or quality string) and feeds it into another
sub-program specified between two `@`-signs. The sub-program is required to
take lines of text as input and return the same number of lines on
standard output. The output of the sub-program is then placed into the output
fastq file. By combining `filter-fastq` and `multiple_mutate`, the tool
which applies mutations to strings of nucleotides, a FASTQ file can be
mutated:

```{.bash}
scripts/filter-fastq --nucleotide \
  @ scripts/multiple_mutate data/mut-tables/mut.tab @ \
  < data/2/volpertinger.fastq \
  > data/3/volpertinger_mut.fastq
```
```{.output}
```
Note how the nucleotide strings of the output FASTQ file now carry
mutations (lower-case letters):

```{.bash}
head data/3/volpertinger_mut.fastq
```
```{.output}
@volpertinger_0
TTCCAaAAGATATTAGCCAACCAGAg
+
FFFFFFFFFFFFFFFFFFFFFFFFFF
@volpertinger_1
TgTATTTgATAACTTaTCCC
+
FFFFFFFFFFFFFFFFFFFF
@volpertinger_2
TTGAACTCTATCTTCCGGGGTgCA
```

The `filter-fastq.py` script enables you to apply an arbitrary script
or program on just one part of a FASTQ file (ID line, nucleotide line,
quality line). The used script must accept the respective part on
standard input and print the modified version on standard output. The
modified FASTQ file is assembled by `filter-fastq.py` from the output
of its children scripts and printed on standard output. 

On the `filter-fastq.py` call, the @ sign serves as a sentinel
character, which determines start and end of the sub-program's
command line. It can also be any arbitrary other character, as long as
it doesn't occur inside the child script's command line but only at
the beginning and the end.


Combining endogenous and non-endogenous reads
---------------------------------------------

In this example, the endogenous reads from *volptertinger* undergo 
simulated mutation and damage prior to mapping, while the contaminant
reads from *R. etli* do not.

Therefore only now, after applying mutations to our *volpertinger*
reads, is the time to combine the mutated sample reads
and the contaminant reads generated in the last section to one
file. For this purpose, the UNIX tool `cat` is used:

```{.bash}
cat data/3/volpertinger_mut.fastq data/2/retli.fastq \
    > data/3/all.fastq
```
```{.output}
```

Obtaining mutation rates from mapDamage
---------------------------------------

Damage patterns from mapDamage can be converted into a table
with mutation parameters by least-squares fitting. For this purpose,
the mapDamage output files ending with `... _freq.txt` are needed.

The following command fits a geometric distribution to mapDamage data, 
shows the derived parameters and plots the data with the fitted curve.

The `cut` command is used only to limit the output to a
width acceptable for this manual. Use the bash `>` redirection
operator to write this output into a file suitable for
`multiple_mutate.py`.

```{.bash}
scripts/mapdamage2geomparam \
    --fit-plots data/3/fit_ \
    data/mapdamage/*.txt | \
    cut -f1-6 | \
    column -t
```
```{.output}
strand                                from  to  factor      geom_prob   intercept
3                                     G     A   0.79513996  0.26918746  0.039386893
data/mapdamage/GS136_3pGtoA_freq.txt
5                                     C     T   0.43360246  0.35249167  0.027965522
data/mapdamage/GS136_5pCtoT_freq.txt
```

The generated plots can be viewed 
<a href="data/3/fit_001_GS136_5pCtoT_freq.txt.pdf">here (C→T)</a> and
<a href="data/3/fit_000_GS136_3pGtoA_freq.txt.pdf">here (G→A)</a>.
fit_000_GS136_3pGtoA_freq.txt.pdf

Generating multiple damage patterns using a parameter table
-----------------------------------------------------------

Sometimes, multiple damage patterns need to be compared. There is a
possibility to generate the `multiple_mutate` input files from one table
which lists all different values of the different mutation parameters. 

This approach will be seen again later, where there is a possibility
to generate many short read mapper calls from exactly the same kind of
parameter table. You can therefore generate appropriate input files
as well as appropriate short read mapper calls out of only one table
which lists all the parameters.

The `fill_template.py` script expects a table, where each row is used
to fill a prespecified template with values. 

For example, if a template is written which looks like this:

```{.bash}
cp data/mut-tmpl/mut-tmpl data/3
column -t data/3/mut-tmpl
```
```{.output}
strand  from  to  factor  geom_prob  intercept
5       C     T   {fac}   {geom}     0
3       G     A   {fac}   {geom}     0
3       *     *   0       0          {all_intercept}
```

And a table is created which looks like this:

```{.bash}
cp data/mut-tmpl/tab data/3/mut-tab
column -t data/3/mut-tab
```
```{.output}
fac  geom  all_intercept
0    0.1   0
0    0.1   0.3
0.5  0.1   0
0.5  0.1   0.3
```

several files can be generated with 

```{.bash}
scripts/fill_template \
    data/3/mut-tmpl \
    < data/3/mut-tab
```
```{.output}
strand	from	to	factor	geom_prob	intercept
5	C	T	0	0.1	0
3	G	A	0	0.1	0
3	*	*	0	0	0

strand	from	to	factor	geom_prob	intercept
5	C	T	0	0.1	0
3	G	A	0	0.1	0
3	*	*	0	0	0.3

strand	from	to	factor	geom_prob	intercept
5	C	T	0.5	0.1	0
3	G	A	0.5	0.1	0
3	*	*	0	0	0

strand	from	to	factor	geom_prob	intercept
5	C	T	0.5	0.1	0
3	G	A	0.5	0.1	0
3	*	*	0	0	0.3

```

Use the `--output` switch of this script to write each file in a
separate file. The argument of `--output` can (and should!) contain
column names of the table, enclosed in braces {...}. This creates a
separate filename per input row. 

We will now write each of the tables shown above to its own file. We
want to name the files using a counting number, but our input table
doesn't yet contain a column with that counter. Therefore we must
first add one.

The mentioned-above table can be prepended with an index
column:

```{.bash}
scripts/index-column --inplace data/3/mut-tab

head data/3/mut-tab | column -t
```
```{.output}
index  fac  geom  all_intercept
0      0    0.1   0
1      0    0.1   0.3
2      0.5  0.1   0
3      0.5  0.1   0.3
```

Now, each output of `fill_template.py` can be written to its own 
output file, using the information from the newly-generated `index`
column:

```{.bash}
scripts/fill_template \
    --output "data/3/{index}_filled" \
    data/3/mut-tmpl \
    < data/3/mut-tab

# Show all the generated files
for f in data/3/*_filled; do
    echo " === $f === "
    column -t $f
done
```
```{.output}
 === data/3/0_filled ===
strand  from  to  factor  geom_prob  intercept
5       C     T   0       0.1        0
3       G     A   0       0.1        0
3       *     *   0       0          0
 === data/3/1_filled ===
strand  from  to  factor  geom_prob  intercept
5       C     T   0       0.1        0
3       G     A   0       0.1        0
3       *     *   0       0          0.3
 === data/3/2_filled ===
strand  from  to  factor  geom_prob  intercept
5       C     T   0.5     0.1        0
3       G     A   0.5     0.1        0
3       *     *   0       0          0
 === data/3/3_filled ===
strand  from  to  factor  geom_prob  intercept
5       C     T   0.5     0.1        0
3       G     A   0.5     0.1        0
3       *     *   0       0          0.3
```

If several combinations of mutation parameters shall be tested,
`cross_tab.py` can be used to generate the table from predefined
parameter values, like described with mapper parameters in the next
section.



Generate mapper calls
=====================

To generate the calls to the mapper using different combinations of 
parameters, several files holding the values of the different parameters
are first combined to a table holding all possible combinations of them.

Subsequently, every line is given a unique index which can be referred to
e.g. when writing output files of the mapping process. By this index, each
run writes to a different output file.

The parameter values are saved in several files, one per parameter. 
In this example, the BWA parameters n and k are varied which results
in two files:

```{.bash}
ls data/mapping/*.par
```
```{.output}
data/mapping/k.par
data/mapping/n.par
```

The files can have arbitrary filenames, they are in a tabular format
where the column names relate to variables which are set automatically
later in the process.

```{.bash}
column -t data/mapping/n.par
```
```{.output}
n
0
4
8
```

To generate all combinations of parameters, two scripts are used:

  * `scripts/cross_tab` expects multiple files and outputs all
    possible combinations of their lines. 

  * `scripts/index-column` This script prepends a counting number 
    to each input line. It can be used to generate index columns for text 
    tables.

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

Add an index column called runidx:
```{.bash}
scripts/index-column --colname runidx --inplace data/4/partab
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

Read now the script `data/mapping/map-bwa.sh` and see how the variables
used there correspond to the column names of partab. The script is
shown in the next code block. 

This is a script which can be called using different parameter
combinations: It calls the mapper `bwa` and forwards the values of the
variables set via `data/4/partab` as command line arguments to the
mapper. 

```{.bash}
#!/usr/bin/bash

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

Below the calls are generated.

```{.bash}
# Convert the table into calls that can be executed in the next section
scripts/table2calls  data/4/partab \
                    data/mapping/map-bwa.sh \
                  > data/4/calls
cat data/4/calls
```
```{.output}
runidx=0 n=0 k=2 data/mapping/map-bwa.sh
runidx=1 n=4 k=2 data/mapping/map-bwa.sh
runidx=2 n=8 k=2 data/mapping/map-bwa.sh
runidx=3 n=0 k=10 data/mapping/map-bwa.sh
runidx=4 n=4 k=10 data/mapping/map-bwa.sh
runidx=5 n=8 k=10 data/mapping/map-bwa.sh
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
[bwa_aln_core] 50 sequences have been processed.
[main] Version: 0.7.13-r1126
[main] CMD: bwa aln -n 0 -k 2 data/genome/volpertinger data/3/all.fastq
[main] Real time: 0.110 sec; CPU: 0.000 sec
[bwa_aln_core] convert to sequence coordinate... 0.00 sec
[bwa_aln_core] refine gapped alignments... 0.00 sec
[bwa_aln_core] print alignments... 0.00 sec
[bwa_aln_core] 50 sequences have been processed.
@SQ	SN:A1	LN:6000
@SQ	SN:A2	LN:6000
@SQ	SN:A3	LN:6000
@SQ	SN:B1	LN:6000
@SQ	SN:B2	LN:6000
@SQ	SN:B3	LN:6000
@SQ	SN:B4	LN:6000
@SQ	SN:MT	LN:6000
@SQ	SN:X	LN:6000
@PG	ID:bwa	PN:bwa	VN:0.7.13-r1126	CL:bwa samse data/genome/volpertinger data/4/0.sai data/3/all.fastq
volpertinger_0	4	*	0	0	*	*	0	0	TTCCAAAAGATATTAGCCAACCAGAG	FFFFFFFFFFFFFFFFFFFFFFFFFF
volpertinger_1	4	*	0	0	*	*	0	0	TGTATTTGATAACTTATCCC	FFFFFFFFFFFFFFFFFFFF
volpertinger_2	4	*	0	0	*	*	0	0	TTGAACTCTATCTTCCGGGGTGCA	FFFFFFFFFFFFFFFFFFFFFFFF
volpertinger_3	4	*	0	0	*	*	0	0	GCATGAGGGTTTCTATTTAGA	FFFFFFFFFFFFFFFFFFFFF
volpertinger_4	4	*	0	0	*	*	0	0	TACTGGCTCGCTGTAGGAACAGG	FFFFFFFFFFFFFFFFFFFFFFF
```



Parsing of SAM files
====================

With the following tools, SAM files can be parsed to gain information of read
names, where they were mapped, which quality score the mapping was assigned
and so on. 

The procedures in this chapter may vary more than the previous ones, 
depending on the research question.

In the setting this package was originally designed for, the names of the
reads carry the information where the reads actually belong to. This
information can subsequently be compared to the actual mapping information
obtained from the SAM file.

Extraction of information
-------------------------

For this purpose, the `sam-extract.R` tool can be used. This tool
converts a SAM file into a table, where the columns can be
informations obtained from the read names or SAM fields. The names of
the SAM fields can be looked up in the SAM specification online, but
the most important ones are:

* qname: read name
* rname: FASTA record name of genome this read was mapped to. `*` if 
         not mapped.
* pos:   base index of mapping position (1-based index!)
* mapq:  quality score assigned by the mapper
* cigar: CIGAR String: Information about gaps and mismatches in
         the alignment read -- reference

Take care not to put any spaces in the argument of --sam-fields.

```{.bash}
scripts/sam-extract --sam-fields qname,rname,pos,mapq \
    data/4/1.sam  >  data/5/1.tab
```
```{.output}
```

```{.bash}
head data/5/1.tab | column -t
```
```{.output}
qname           rname  pos   mapq
volpertinger_0  B1     2143  37
volpertinger_1  MT     3402  37
volpertinger_2  A3     1413  37
volpertinger_3  A3     5689  37
volpertinger_4  *      0     0
volpertinger_5  *      0     0
volpertinger_6  A1     1320  23
volpertinger_7  *      0     0
volpertinger_8  X      2381  37
```

```{.bash}
tail data/5/1.tab | column -t
```
```{.output}
retli_15  *   0     0
retli_16  MT  2791  25
retli_17  *   0     0
retli_18  *   0     0
retli_19  *   0     0
retli_20  *   0     0
retli_21  *   0     0
retli_22  *   0     0
retli_23  *   0     0
retli_24  *   0     0
```

Bring together true read information from all origin organisms
--------------------------------------------------------------

This can be done by concatenating the tabular files generated during
the read sampling process (Section 2). `awk` is used to concatenate
the files while not repeating the header line of the second file.

Prior to this we append a column to the tables which indicates the
organism of each read. This enables us to group the reads by origin
organism later.

```{.bash}
# Add column 'organism' with value 'volpertinger'
scripts/add_const_column \
    data/2/volpertinger.coord \
    organism        \
    volpertinger    \
    > data/5/volpertinger_org.coord

# Same for R. etli reads
scripts/add_const_column \
    data/2/retli.coord \
    organism        \
    retli    \
    > data/5/retli_org.coord
```
```{.output}
```

This yields files like this:
```{.bash}
head -n5 data/5/volpertinger_org.coord | column -t
```
```{.output}
name            record  start  end   organism
volpertinger_0  B1      2143   2168  volpertinger
volpertinger_1  MT      3402   3421  volpertinger
volpertinger_2  A3      1413   1436  volpertinger
volpertinger_3  A3      5689   5709  volpertinger
```

Now the tables can be concatenated. Make sure both tables contain the
same columns in the same order or else you will get invalid data!
```{.bash}
awk '(NR==1 || FNR!=1)' \
      data/5/volpertinger_org.coord \
      data/5/retli_org.coord  \
    > data/5/all.coord
```
```{.output}
```

Identify correctly mapped reads
-------------------------------

One possibility is the script used below, `exactmap.R`

This script relies on the input table columns having specific names. 
For details see the help of the script by calling 
`scripts/eval/exactmap.R -h`.

Use the `--qthresh` parameter to declare all reads with a mapping
quality below a certain threshold as not mapped. 

```{.bash}
scripts/exactmap   data/5/all.tab \
                   data/5/1.tab  \
                   > data/5/1.crct

cat data/5/1.crct | column -t
```
```{.output}
```

***TODO:*** Organism column 

This script can also deal with an additional organism column in the
input tables. This may be important if multiple of the organisms have
FASTA records of the same name. A common case of this is multiple
eukaryotes with similarly named chromosomes. 

Custom determination of correct match
--------------------------------------

If you want to determine correctly mapped reads by your own means, you
can merge the two tables, the correct positions of the reads and the
actual mapping positions of the reads, to one table which you can
inspect afterwards. There is a tool designed to make merging
information from two tables as easy as possible. To merge the
information, both tables need to share at least one column, which is
described as the *key column*. In this case, the read name is the key
because it is present in both tables. 

The `merge` tool can also rename columns in the process of merging. We
will use this functionality to distinguish the true mapping positions
from `all.tab` from the actual mapping positions from `1.tab` by
prepending a 't' to the former. 

Here is an example to match the nominal and actual read positions into
one table. `-a` and `-b` denote the two tables to be merged. The first
argument after those is the file name, followed by the key column and
all other columns which shall be merged. If columns shall be renamed,
there are arguments of the form `oldname=newname`. 

```{.bash}
scripts/merge -a data/5/all.coord name  record=trecord start=tstart \
                                      organism=torg\
              -b data/5/1.tab   qname rname=record   pos=start \
          > data/5/merge_example.tab

# Show parts of the table
(head data/5/merge_example.tab; tail data/5/merge_example.tab)| column -t

```
```{.output}
name             trecord   tstart  torg          record  start
retli_0          retli_tr  121502  retli         *       0
retli_1          retli_tr  133167  retli         *       0
retli_10         retli_tr  110631  retli         *       0
retli_11         retli_tr  82809   retli         *       0
retli_12         retli_tr  66530   retli         *       0
retli_13         retli_tr  108831  retli         *       0
retli_14         retli_tr  109927  retli         *       0
retli_15         retli_tr  82777   retli         *       0
retli_16         retli_tr  66982   retli         MT      2791
volpertinger_22  MT        615     volpertinger  MT      615
volpertinger_23  B3        608     volpertinger  B3      608
volpertinger_24  B2        4581    volpertinger  *       0
volpertinger_3   A3        5689    volpertinger  A3      5689
volpertinger_4   MT        3280    volpertinger  *       0
volpertinger_5   A3        4936    volpertinger  *       0
volpertinger_6   A1        1320    volpertinger  A1      1320
volpertinger_7   A3        4480    volpertinger  *       0
volpertinger_8   X         2381    volpertinger  X       2381
volpertinger_9   A1        2751    volpertinger  A1      2751
```

Grouping of reads
-----------------

For the next steps, the reads must be grouped by the original organism
and the organism they were mapped to. This can be done by merging 
the table `idlist` from Section 1 two times:

The last two lines of the first command in the following example serve 
for replacing `data/5/5.crct` using a temporary file.

The first argument of `merge_organisms.R` may be a hypen (-) in which case
the first table is read from standard input. This is handy for merging
multiple information.

Note that the information about the true origin organism of the
*R. etli* contaminant reads needs to be merged into 
the information about the organism of the sample organisms'
chromosomes. Speaking in files, `data/1/sample.recids` must be
concatenated with `data/2/retli.recids`

This is done by:

```{.bash}
awk '(NR==1 || FNR!=1)' \
    data/1/sample.recids \
    data/2/retli.recids \
    > data/5/all.recids

cat data/5/all.recids | column -t
```
```{.output}
```

This is because the reads weren't mapped
against the *R. etli* reference genome, therefore the *R. etli*
chromosome can not appear as a `rname` value of the SAM file.

```{.bash}
scripts/eval/merge_organisms.R data/5/1.crct \
                               m.orig \
                               data/5/all.recids \
                               organism=m.org  |  \
scripts/eval/merge_organisms.R - \
                               t.orig \
                               data/5/all.recids \
                               organism=t.org  \
                            > data/5/1.crct.tmp &&
                            mv data/5/1.crct{.tmp,}

cat data/5/1.crct | column -t
```
```{.output}
```

As next step, the number of reads are counted which belong to 
certain categories. Here, the categories are:
  * Correctly mapped or not
  * Origin organism
  * Organism a read was mapped to

the `cbind` function is needed in order to name the column containing 
the read count

```{.bash}
scripts/general/pocketR.R '
    aggregate(cbind(count=read) ~ t.org+m.org+correct,
        FUN=length, data=input)
    ' \
    data/5/1.crct > data/5/1.agg

cat data/5/1.agg | column -t
```
```{.output}
```

Another possibility if you're proficient in dplyr:

```{.bash}
scripts/general/pocketR.R --pkg dplyr '
    group_by(input, t.org, m.org, correct) %>%
    summarize(count=n())
    ' \
    data/5/1.crct > data/5/1.agg

head data/5/1.agg | column -t
```
```{.output}
```

This format may be used to plot the read fate of a single mapper run
and to derive the measures sensitivity and specificity:

```{.bash}
scripts/eval/plot-read-fate.R t.org        m.org  \
                              correct      count \
                              data/5/1.pdf data/5/1.agg
```
```{.output}
```

<a href="data/5/1.pdf">Click here</a> to see the plot.

Sensitivity and specificity
---------------------------

  * **Sensitivity** (recall) shows how many reads have been mapped
    correctly by the mapper which are supposed to map.
  * **Specificity** (precision) shows how many reads have been
    correctly identified as non-endogenous and were therefore not
    mapped.

If non-endogenous reads were included in the reads, like we did by
including the *R. etli* reads, both measures can be calculated.

The following script needs the same kind of input as the
`plot-read-fate.R` script. Additionally, a list of organisms must be
specified, whose genomes the mapper used as a reference. 

If you specify multiple organisms, separate them by commas and don't
include any spaces.

```{.bash}
scripts/eval/sensspec.R data/5/1.agg volpertinger \
    > data/5/1.parameters

column -t data/5/1.parameters
```
```{.output}
```



Repeat all steps for every SAM file
-----------------------------------

The code needed to evaluate the data generated by the mapper might as
well be included in the mapping template script introduced in the last
section. If this is done, the data evaluation can be as well
parallelized as the mapping process.

All scripts used here were already introduced in this section.

The files `data/5/all.tab` and `data/5/all.recids` must be calculated
prior to execution of this script. This has been done in this section 
as well.

Browse the <a href="data/5">directory `data/5`</a> to see the results.

```{.bash}
for sam in data/4/*.sam; do
    # Generate output prefix from input name: `4.sam` -> `4`
    bn=$(basename $sam)
    opref=${bn%.sam}

    # Extract SAM fields
    scripts/eval/sam-extract.R --sam-fields qname,rname,pos,mapq \
        ${sam}  >  data/5/${opref}.tab

    # Mark correctly/incorrectly mapped reads
    scripts/eval/exactmap.R data/5/all.tab \
                            data/5/${opref}.tab  \
                          > data/5/${opref}.crct

    # Get organisms for chromosome names
    scripts/eval/merge_organisms.R data/5/${opref}.crct \
                                   m.orig \
                                   data/5/all.recids \
                                   organism=m.org  |  \
    scripts/eval/merge_organisms.R - \
                                   t.orig \
                                   data/5/all.recids \
                                   organism=t.org  \
                                > data/5/${opref}.crct.tmp &&
                                mv data/5/${opref}.crct{.tmp,}

    # Count reads per origin/target organism and mapping status
    scripts/general/pocketR.R '
        aggregate(cbind(count=read) ~ t.org+m.org+correct,
            FUN=length, data=input)
        ' \
        data/5/${opref}.crct > data/5/${opref}.agg

    # Plot mapping targets per origin organism
    scripts/eval/plot-read-fate.R t.org        m.org  \
                                  correct      count \
                                  data/5/${opref}.pdf data/5/${opref}.agg

    # Calculate sensitivity, specificity and balanced accuracy
    scripts/eval/sensspec.R data/5/${opref}.agg volpertinger \
        > data/5/${opref}.performance

    echo "$sam done. -> Generated data/5/${opref}.{tab,agg,crct,pdf,performance}"

done
```
```{.output}
data/4/0.sam done. -> Generated data/5/0.{tab,agg,crct,pdf,performance}
data/4/1.sam done. -> Generated data/5/1.{tab,agg,crct,pdf,performance}
data/4/2.sam done. -> Generated data/5/2.{tab,agg,crct,pdf,performance}
data/4/3.sam done. -> Generated data/5/3.{tab,agg,crct,pdf,performance}
data/4/4.sam done. -> Generated data/5/4.{tab,agg,crct,pdf,performance}
data/4/5.sam done. -> Generated data/5/5.{tab,agg,crct,pdf,performance}
```

    

Comparing multiple mapper runs
==============================

The file `data/4/partab` holds the information which parameters were
used for which mapping run. By relating the output measures like
sensitivity, specificity or balanced accuracy to these parameters, the
influence of individual parameters can be assessed.

First step is to combine the output measures of all runs:

```{.bash}
for f in data/5/*.performance; do
    i=$(basename ${f%.performance})

    scripts/general/add_const_column.sh $f runidx $i \
        > data/6/${i}.performance
done

awk '(NR==1||FNR!=1)' data/6/*.performance > data/6/performance

cat data/6/performance | column -t
```
```{.output}
```

Next, the parameter values belonging to the run indices are joined in, 
appending the parameter columns to `data/6/parameters` itself.

```{.bash}
scripts/general/pocketR.R '
    merge(inputs[[1]], inputs[[2]], by="runidx", all.x=TRUE)
    ' \
    data/6/performance data/4/partab > data/6/performance.tmp &&
    mv data/6/performance{.tmp,}

head data/6/performance | column -t
```
```{.output}
```

The value of one parameter can be plotted against some measure. The
following command shows plots where the X and Y axis are free to
choose. If multiple runs yield a similar score on the Y axis, their
data points are merged to form one bigger dot on the plot. Here all
numbers are rounded to one significant digit, because only 8 mapping
runs are compared in this example. Therefore results must be
aggregated coarsely to demonstrate the results.

```{.bash}
# Plot n versus BCR
scripts/eval/plot_parameter_effects.R --signif 1 data/6/performance n bcr \
    data/6/n.pdf

# Plot k versus BCR
scripts/eval/plot_parameter_effects.R --signif 1 data/6/performance k bcr \
    data/6/k.pdf
```
```{.output}
```

View the plots: <a href="data/6/n.pdf">n vs. BCR</a> and
 <a href="data/6/k.pdf">k vs. BCR</a>.

 It can be seen that n seems to have an impact on the BCR whereas k
 does not. The BCR rises and falls again because the gain in
 sensitivity is offset by the loss in specificity if n rises too high.


Glossary
========

Some terms are explained here, which are used in the rest of the
manual and may have a special meaning:

~table: A text table is the most widely used data format in this
project. It is a simple text file, where the columns are separated by
a special character. Usually this is a tabulator (tab) character, but
sometimes space-separated tables are also used. 

~FASTA record: A FASTA record is a block in a fasta file which is
delimited by two > signs. It consists of the following parts:
 
 1)  The header line: >.................(line end). 
    a) The FASTA identifier, which is the first 'word' of the header
       line. E.g. in a header line 
       
    >A1 Felis catus genome ID:012345...
        
        the FASTA identifier is 'A1'.
    b) The FASTA record description: All the text between identifier
       and line end. 
 2) Biological sequence data, IUPAC one-character-code. Should not be wider 
    than 80 characters and may contain whitespace.
    E.g. nucleotides: ACCTCTCTACCT...

~FASTA identifier: -> FASTA record

~FASTA description: -> FASTA record

~file offset: This is the
distance in bytes from the beginning of a file. The first character of
a file has the offset 0.

~offset: -> file offset

~i-based index: An index is i-based if it starts counting with
number i. For example, the mapping position (pos) field of a SAM file 
is a 1-based index. If the position 1 is written there, the read maps
to the first base of the genome. Conversely, if the index were
0-based,
the first base of the genome would be referenced with the number 0.

~0-based: -> i-based index

~1-based: -> i-based index

~standard input: Many commands expect input on this stream. Input can
be provided either by typing into the console, by using the < operator
to provide input from a file or by the | operator, which forwards the
content on standard output of a previous command to standard input of
this command. Refer to the "Redirection" section of your shell for
more information.

~standard output: All output a command writes is by default redirected
to the standard output or standard error streams. Per convention,
standard output is used for the results of the program, whereas
standard error is used for status and error messages. Content on
standard output can be written in a file by using the > operator or
redirected to standard input of another command by using the |
operator. Standard error output can be redirected to a file using the
2> operator. Consult the "Redirection" section of your shell for more
information. 

~standard error: -> standard output

~command line argument: a value which is written on the command line
behind the name of the program which shall be invoked. They are
forwarded to the program and influence it. The valid parameters of a
program are described in the program's manual. (often accessible via
the `--help` command line argument. 

~command line switch: -> command line argument




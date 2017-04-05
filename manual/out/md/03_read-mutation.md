---
title: 
- Mutation of reads
---

Mutation of reads
=================

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
Two types of per-base mutation probabilities are distinguished:

 * The  **position-independent** mutation probability is the same for
   all bases of the read. This can be used to model read derivation by
   evolution.
 * The **position-dependent** mutation probability is dependent of the
   proximity of a base to the end of the read. The nearer a base is to
   the read end, the higher is the mutation probability of the base.
   This can be used to model chemical damage to ancient DNA.

Probability values  are specified which range from 0 (never mutate
that base) to 1 (always mutate that base). Probabilities of multiple
lines which are applicable to the same base add up. The columns have the 
following meaning:
 
  * strand:  [3 or 5] Which side (3' or 5' end) of the read shall be
    considered the read end when the base-dependent mutation
    probability is calculated. If both sides of the read shall see
    heightened mutation probabilities, include two lines, one with a
    value `3` and one with a value `5`.
  * from: [Letter or `*`] Which bases should mutate according to this
    lines' parameters. The character `*` means this line applies to every base.
  * to:   [Letter or `*`] Which base should a mutation event yield. 
          `*` means a base (A,T,C,G) different from the original base is
            chosen at random.
  * factor: Maximum position-dependent mutation probability at the
    read end (specified by `strand`)
  * geom_prob: How fast the position-dependent mutation probability
    declines for bases further away from the read end. 0 means no
    decline, higher values lead to faster decline. 
  * intercept: The position-independent mutation probability.

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


Subject a FASTQ file to artificial mutations
---------------------------------------------

The `multiple-mutate.py` tool takes a table of the previous section as
input and mutates strings provided to it on standard input
accordingly. 

An already existent FASTQ file can be mutated using the `filter_fastq`
tool in cooperation with `multiple-mutate`. The tool `filter_fastq`
enables you to apply transformations to existing fastq files. To this
effect, `filter_fastq` extracts one part out of a FASTQ file (read
name, nucleotide string or quality string) and feeds it into another
sub-program specified between two `@`-signs. The sub-program is required to
take lines of text as input and return the same number of lines on
standard output. The output of the sub-program is then placed into the output
fastq file. By combining `filter_fastq` and `multiple_mutate`, the tool
which applies mutations to strings of nucleotides, a FASTQ file can be
mutated. The `--seed` can be set to an arbitrary value to generate a
reproducable result.

```{.bash}
scripts/filter_fastq --nucleotide \
  @ scripts/multiple_mutate --seed 123 data/mut-tables/mut.tab @ \
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
@volpertinger_1
TTgTACcAGtTATTAGtCAATCAGAT
+
FFFFFFFFFFFFFFFFFFFFFFFFFF
@volpertinger_2
TCTAgTTccTAACTTtTCCC
+
FFFFFFFFFFFFFFFFFFFF
@volpertinger_3
gTaAACTtTATCTTCTGGGGCcgA
```

The `filter_fastq.py` script enables you to apply an arbitrary script
or program on just one part of a FASTQ file (ID line, nucleotide line,
quality line). The used script must accept the respective part on
standard input and print the modified version on standard output. The
modified FASTQ file is assembled by `filter_fastq.py` from the output
of its children scripts and printed on standard output. 

On the `filter_fastq.py` call, the @ sign serves as a sentinel
character, which determines start and end of the sub-program's
command line. It can also be any arbitrary other character, as long as
it doesn't occur inside the child script's command line but only at
the beginning and the end.


Combining endogenous and non-endogenous reads
---------------------------------------------

In this example, the endogenous reads from *volpertinger* undergo 
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
strand  from  to  factor      geom_prob   intercept
3       G     A   0.79513996  0.26918746  0.039386893
5       C     T   0.43360246  0.35249167  0.027965522
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
scripts/index_column --inplace data/3/mut-tab

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




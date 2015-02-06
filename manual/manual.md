Genome Preparation
==================
 

Prior to extraction of reads, the original genomes must be 
preprocessed. This encompasses three steps:
 
Record index table
------------------
The FASTA record identifiers must be written in a table.
This enables to assign different chromosomes to the same organism
later on in the analysis (Section 5)

In this example, the reads stem from our sample organism
'volpertinger':

```{.bash}
scripts/genome/mfasta-idlist.sh data/genome/sample.fasta volpertinger \
    > data/1/sample.recids
head data/1/sample.recids
```
```{.output}
record	organism
A1	volpertinger
A2	volpertinger
A3	volpertinger
B1	volpertinger
B2	volpertinger
B3	volpertinger
B4	volpertinger
MT	volpertinger
X	volpertinger
```

The second parameter is optional, but handy if the target genome is
comprised of multiple FASTA records. It adds a column called
"organism" which holds the string of the second argument (in this
case, "sample"). The resulting table can be used to associate all the
FASTA records of this FASTA file to the same organism in subsequent
analysis steps.

Linearization
-------------

The genome files must be linearized. This means the deletion of
all whitespace and newline characters in the data section of
each FASTA record. This is needed because this makes it much
quicker to jump to a specific base in the FASTA file.

In the following example the output lines are truncated for better
readability

```{.bash}
scripts/generate-reads/nucl/linearize_fasta \
    data/genome/sample.fasta > data/1/sample.fasta.lin

# Show output, partially
cut -c-80 data/1/sample.fasta.lin
```
```{.output}
>A1 dna:chromosome chromosome:Felis_catus_6.2:A1:1:239302903:1 REF
CCAAACAATAAAGACTCTTAAAAACTGAGAACAATGAGGGTTGATGGGGGGTGGGAGAGGAGGGGAGGGTGGGTGATGGG
>A2 dna:chromosome chromosome:Felis_catus_6.2:A2:1:169043629:1 REF
CCGTACCAGCAGAACCCAACCCCAACCCCAACCCCAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAAC
>A3 dna:chromosome chromosome:Felis_catus_6.2:A3:1:142459683:1 REF
TCACTGGATCCCCCTTAGGATCTCTTGTAGGGCTGGTTTAGTGGTGATGAATTCCTTCAGTTTTTGTTTGTTTGGGAAGA
>B1 dna:chromosome chromosome:Felis_catus_6.2:B1:1:205241052:1 REF
ATCTAGACTTTAAAATAAAGACTGCAACAAGAGATGAAGAATGGTGTTGTATCATAATTAAGGGAGTCTATCCACCAAAA
>B2 dna:chromosome chromosome:Felis_catus_6.2:B2:1:154261789:1 REF
AAAAAAAAAGAAAGAAAAGAAAAGAAAATCTGGATCTCAAAAAGGTATCTGCACTCCTGTGTGATAATACTGTGTTACAG
>B3 dna:chromosome chromosome:Felis_catus_6.2:B3:1:148491654:1 REF
GCACTGGGTGATTGAATAAAAATATAGGACCCACATATCTTCTACCTACAAGAGACTAATTATAGAACTGAAGTATCAAA
>B4 dna:chromosome chromosome:Felis_catus_6.2:B4:1:144259557:1 REF
CTGGTCTGAAGAGCCTGGAAAGGATGACAGGACATGGGCCTATTCCTTTTTCCCACTCAGACTCAATGTGAAGACTTTAG
>MT dna:chromosome chromosome:Felis_catus_6.2:MT:1:17009:1 REF
GGACTAATGACTAATCAGCCCATGATCACACATAACTGTGGTGTCATGCATTTGGTATTTTTTATTTTTAGGGGGTCGAA
>X dna:chromosome chromosome:Felis_catus_6.2:X:1:126427096:1 REF
CACCACTTCCTTGTTCCCCATCTATCACATCCGGCCATTAGGAGAAAATTACAGGGTATACTGACAGGTGACAAACGTGA
```

Record offset index
-------------------

To efficiently know the location of a specific FASTA record in a
FASTA-file, an index of file offsets of these records must be saved. 

```{.bash}
scripts/generate-reads/nucl/fasta_record_index \
    data/1/sample.fasta.lin > data/1/sample.idx

# Show output, partially
head data/1/sample.idx
```
```{.output}
head 0
data 67
len 6000
head 6068
data 6135
len 6000
head 12136
data 12203
len 6000
head 18204
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

The uniform.py script can be used to sample reads from a reference
genome. The script needs a FASTA file as input, as well as the desired
amount of reads to be generated, the minimum length and the decay
length. The read lengths are exponentially distributed; the decay
length parameter specifies the length by which half of the reads are
longer than the minimum read length.

The input genome is linearized and an offset index is created by default, 
as described in the previous section. This can be suppressed by the 
command line switches `--linearized` and `--index`, if these steps are
executed manually previously.

Example: Extract 25 reads, with minimum length 20 basepairs, where
half of the reads have a length longer than 25 bp. The value 123 
is used to initialize the random number generator, i.e. can be used to
obtain reproducible reads. This last parameter can be omitted.

The resulting output is a table containing four columns:

 1. The FASTA record name (e.g. chromosome) where the read originated.
 2. 1-based base number of the reads' first base.
 3. 1-based base number of the reads' last base.
 4. The nucleotides of the read

The base indices are 1-based because base indices are 1-based in
SAM-files as well. (whereas in BAM-files, they are 0-based, but that
is not of interest here.)

Generate reads without prior genome processing steps:

```{.bash}
scripts/generate-reads/nucl/uniform.py data/genome/sample.fasta \
    25 20 5 123  >  data/2/sample.tab
# Show output
head data/2/sample.tab | column -t
```
```{.output}
record  start  end   read
A2      498    518   AGAATGAAATCTTGCCATTTG
B2      4899   4923  AACCAGAGCACACGTAGGCAGCCAT
X       3674   3693  ATCCTGCGAGGGGGCCCGAG
B2      3616   3640  TTTTGCTTTTGTTTCCCTTGGCTCT
B1      3675   3694  GAGGAGAAAGCAGACAAAAA
A2      4682   4701  ATGTAATATTATTTANNNNN
B2      4974   4994  ATCCTTGGAGGTAGAGTCACC
A3      1510   1532  GTTAAGTCCCGCTGGCTGTCAGA
MT      4875   4910  GCTTTGAAATGAACCTATTAGCCATCATCCCCATCC
```

Generate reads while using a pre-processed genome (linearized and
indexed). See previous section for generation of the used input files.


```{.bash}
scripts/generate-reads/nucl/uniform.py \
    --index data/1/sample.idx \
    --linearized data/1/sample.fasta.lin \
    25 20 5 123 >  data/2/sample.tab
# Show output
head data/2/sample.tab | column -t
```
```{.output}
record  start  end   read
A2      498    518   AGAATGAAATCTTGCCATTTG
B2      4899   4923  AACCAGAGCACACGTAGGCAGCCAT
X       3674   3693  ATCCTGCGAGGGGGCCCGAG
B2      3616   3640  TTTTGCTTTTGTTTCCCTTGGCTCT
B1      3675   3694  GAGGAGAAAGCAGACAAAAA
A2      4682   4701  ATGTAATATTATTTANNNNN
B2      4974   4994  ATCCTTGGAGGTAGAGTCACC
A3      1510   1532  GTTAAGTCCCGCTGGCTGTCAGA
MT      4875   4910  GCTTTGAAATGAACCTATTAGCCATCATCCCCATCC
```

As a last step, the output table is given an index column which
assigns a unique name to each read:

```{.bash}
scripts/general/index-column.py --prefix "sample_" \
                                --colname name \
                                --inplace data/2/sample.tab

head data/2/sample.tab | column -t
```
```{.output}
name      record  start  end   read
sample_0  A2      498    518   AGAATGAAATCTTGCCATTTG
sample_1  B2      4899   4923  AACCAGAGCACACGTAGGCAGCCAT
sample_2  X       3674   3693  ATCCTGCGAGGGGGCCCGAG
sample_3  B2      3616   3640  TTTTGCTTTTGTTTCCCTTGGCTCT
sample_4  B1      3675   3694  GAGGAGAAAGCAGACAAAAA
sample_5  A2      4682   4701  ATGTAATATTATTTANNNNN
sample_6  B2      4974   4994  ATCCTTGGAGGTAGAGTCACC
sample_7  A3      1510   1532  GTTAAGTCCCGCTGGCTGTCAGA
sample_8  MT      4875   4910  GCTTTGAAATGAACCTATTAGCCATCATCCCCATCC
```


Splitting the read sampler output
---------------------------------

The first two columns of the output will be included in a table which
lists the true positions of the reads. Therefore the column names will
start with 't' (true) in this case, but the names are arbitrary.

This table will also list the future read names, which are generated
using awk. 

The last column will be the nucleotide strings of the new FASTQ file.
This column will be written to an extra file.

Generate the table with true read positons and add the FASTA record
name (tail -n+2 ... removes the first line (header line)):

```{.bash}
awk '(NR!=1){
        print $1 > "data/2/sample.i";
        print $5 > "data/2/sample.n";
     }' \
     data/2/sample.tab
```
```{.output}
```
Show output
```{.bash}
head data/2/sample.i
```
```{.output}
sample_0
sample_1
sample_2
sample_3
sample_4
sample_5
sample_6
sample_7
sample_8
sample_9
```

```{.bash}
head data/2/sample.n
```
```{.output}
AGAATGAAATCTTGCCATTTG
AACCAGAGCACACGTAGGCAGCCAT
ATCCTGCGAGGGGGCCCGAG
TTTTGCTTTTGTTTCCCTTGGCTCT
GAGGAGAAAGCAGACAAAAA
ATGTAATATTATTTANNNNN
ATCCTTGGAGGTAGAGTCACC
GTTAAGTCCCGCTGGCTGTCAGA
GCTTTGAAATGAACCTATTAGCCATCATCCCCATCC
TCAGCCCCACAGTGAGGAGAAACCAA
```

```

Quality strings
---------------

Currently, the effect of quality strings on the mapping result has not
been investigated. Currently only strings of constant quality score
are used. This can be done by the sed tool, which replaces every 
character by an F:

```{.bash}
sed 's/./F/g' data/2/sample.n > data/2/sample.q
head data/2/sample.q
```
```{.output}
FFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFFFFFFFFFFFF
```

Creating a FASTQ file
---------------------

The `synth-fastq.py` tool creates a FASTQ file from its components,
nucleotide string, quality string and read name (ID line). If the file
containing the read lines is omitted, the reads are numbered
sequentially.

```{.bash}
scripts/generate-reads/synth-fastq.py data/2/sample.{n,q,i} \
    > data/2/sample.fastq

head data/2/sample.fastq
```
```{.output}
@sample_0
AGAATGAAATCTTGCCATTTG
+
FFFFFFFFFFFFFFFFFFFFF
@sample_1
AACCAGAGCACACGTAGGCAGCCAT
+
FFFFFFFFFFFFFFFFFFFFFFFFF
@sample_2
ATCCTGCGAGGGGGCCCGAG
```

Repeat the above steps to generate contaminant reads
----------------------------------------------------

This commands generate some reads from a truncated Rhizobium etli
genome, to supply reads which are not supposed to map. This way,
contamination with non-endogenous reads are simulated.

The endogenous (`sample.fastq`) and contaminant (`retli.fastq`) 
read will be merged into one fastq file (`all.fastq`) once the
sample reads have undergone mutation simulation. This will be 
done in the next section.

```{.bash}
scripts/genome/mfasta-idlist.sh data/retli/retli_tr.fasta retli \
    > data/2/retli.recids

scripts/generate-reads/nucl/uniform.py \
    data/retli/retli_tr.fasta \
    25 20 5 234 \
    > data/2/retli.tab

scripts/general/index-column.py  --prefix retli_ \
                                 --colname name  \
                                 --inplace data/2/retli.tab

awk '(NR!=1){
       print $1 > "data/2/retli.i";
       print $5 > "data/2/retli.n";
     }' \
    < data/2/retli.tab

sed 's/./F/g' < data/2/retli.n \
              > data/2/retli.q

scripts/generate-reads/synth-fastq.py \
    data/2/retli.n \
    data/2/retli.q \
    data/2/retli.i \
    > data/2/retli.fastq

```
```{.output}
```

Mutation of reads
=================

Mutation probabilities
----------------------

The reads are mutated using per base probabilities derived from the
geometric distribution. The mutation probabiltiy at the read ends is
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
of the read. The exchage probability depends on the type of the
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
(`synth-fastq.py`, see previous section):
```{.bash}
scripts/induce-errors/multiple_mutate.py data/mut-tables/mut.tab \
    < data/2/sample.n
```
```{.output}
AGAcTGAAAgTTTGCCATTTG
AACCAGAGCACACGTAGGCAGCTAc
ATCCTGCGAGGGGGCCCGAG
TTTTGCTTTTGTaTCCTTTGGaTCT
tAGaAGgAAGCAcACAAAAA
ATtTAATATcATTTANNNNN
ATCCTTGaAGtTAGAtTgcCT
GTTAAGTCCCtCTGcCTGTCAGA
tCTTTGAAATGAACCTATTAGTCATCATCCCCATCC
TCAGgCCCACAGaGAacAcgAACCAA
TcGTCACAGAACTAGAAcAAAT
GGGAAGAGTGTGGTTGCTGTGa
CAAcCAAGAATATCCAATTcTTGc
TGAGTCCAGGAGTTCAGGGT
GATAGCgACTgTgGgCTAGGgAT
ACCATAAAATACCTAGGggTAA
NNNNNNNNNNNNNNNNNNNNNNNN
NNNNNNNNNNNNNNNNNNNNNN
gTCTAAGCAAGgCTTcCAGACgT
AAcATcGCACCcCTATCAATCT
ttATTCTGTGGTTtCACAGACAGG
aATaTACTaagAcTAAATTACG
NNNNNNNNNNNNNNNNNNNNNNN
GAAGGATtgAaGGCAAAAAT
TcGTTaATcatAGcAGAAGGTgA
```

Alternatively, a already existant FASTQ file can be mutated using the
`filter-fastq.py` tool in cooperation with `multiple-mutate.py`:

```{.bash}
scripts/general/filter-fastq.py --nucleotide \
  @ scripts/induce-errors/multiple_mutate.py data/mut-tables/mut.tab @ \
  < data/2/sample.fastq > data/3/sample_mut.fastq

head data/3/sample_mut.fastq
```
```{.output}
@sample_0
AGAATGAAAaCTTGCCATTTG
+
FFFFFFFFFFFFFFFFFFFFF
@sample_1
AACCAtgGCcCACaTAGGCAGgCAT
+
FFFFFFFFFFFFFFFFFFFFFFFFF
@sample_2
ATCCTGCGAaGGaGCCCGAG
```

The `filter-fastq.py` script enables you to apply an arbitrary script
on just one part of a FASTQ file (ID line, nucleotide line, quality
line). The used script must accept the respective part on standard
input and prints the modified version on standard output. The modified
FASTQ file is assembled by `filter-fastq.py` from the output of its
children scripts and printed on standard output. 

On the `filter-fastq.py` call, the @ sign serves as a sentinel character,
which determines start and end of the child scripts' command line. It
can be an arbitrary character, as long as it doesn't occur inside the
child scripts' command line.


Combining endogenous and non-endogenous reads
---------------------------------------------

In this example, the endogenous reads undergo simulated mutation
and damage prior to mapping, while the contaminant reads do not.

Therefore, now is the time to combine the mutated sample reads
and the contaminant reads generated in the last section to one
file. For this purpose, the UNIX tool `cat` is used:

```{.bash}
cat data/3/sample_mut.fastq data/2/retli.fastq \
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
scripts/distribution-parametrization/mapdamage2geomparam.py \
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

The `fill_template.py` script expects a table, where each row is used
to fill a prespecified template with values. 

For example, if a template is written which looks like this:

```{.bash}
column -t data/mut-tmpl/mut-tmpl
```
```{.output}
strand  from  to  factor  geom_prob  intercept
5       C     T   {fac}   {geom}     0
3       G     A   {fac}   {geom}     0
3       *     *   0       0          {all_intercept}
```

And a table is created which looks like this:

```{.bash}
column -t data/mut-tmpl/tab
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
scripts/general/fill_template.py \
    data/mut-tmpl/mut-tmpl \
    < data/mut-tmpl/tab
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

For example, the mentioned-above table can be prepended with an index
column:

```{.bash}
scripts/general/index-column.py <data/mut-tmpl/tab >data/3/tab-i

head data/3/tab-i | column -t
```
```{.output}
index  fac  geom  all_intercept
0      0    0.1   0
1      0    0.1   0.3
2      0.5  0.1   0
3      0.5  0.1   0.3
```

Now, each output of `fill_template.py` can be written to its own 
output file:

```{.bash}
scripts/general/fill_template.py \
    --output "data/3/{index}_filled" \
    data/mut-tmpl/mut-tmpl \
    < data/3/tab-i

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

  * `scripts/general/cross_tab.py` expects multiple files and outputs all
    possible combinations of their lines. 

  * `scripts/general/index-column.py` This script prepends a counting number 
    to each input line. It can be used to generate index columns for text 
    tables.

Generate all possible combinations of parameters, retaining 1 header
line:
```{.bash}
scripts/general/cross_tab.py --head 1 data/mapping/*.par > data/4/partab
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
scripts/general/index-column.py --colname runidx --inplace data/4/partab
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
shown in the next code block. There is an additional
variable there, `$fastq`. This variable needs to be set and exported before
executing the calls, which will be done in the next section.

```{.bash}
#!/usr/bin/bash

## This script performs a mapping using BWA.
## It requires the variables k, n, runidx and fastq be set 
## prior to its execution.

# Fail if any needed variable is not set
set -ue

bwa aln -n $n -k $k        \
    data/genome/sample     \
    $fastq                 \
    > data/4/${runidx}.sai \
    2> data/4/${runidx}.log &&

bwa samse data/genome/sample \
      data/4/${runidx}.sai   \
      $fastq                 \
      > data/4/${runidx}.sam \
     2>> data/4/${runidx}.log

```

Below the calls are generated.

```{.bash}
# Convert the table into calls that can be executed in the next section
scripts/general/table2calls.py  data/4/partab \
                                data/mapping/map-bwa.sh \
                              > data/4/calls
head data/4/calls
```
```{.output}
(n=0; runidx=0; k=2; source data/mapping/map-bwa.sh);
(n=4; runidx=1; k=2; source data/mapping/map-bwa.sh);
(n=8; runidx=2; k=2; source data/mapping/map-bwa.sh);
(n=0; runidx=3; k=10; source data/mapping/map-bwa.sh);
(n=4; runidx=4; k=10; source data/mapping/map-bwa.sh);
(n=8; runidx=5; k=10; source data/mapping/map-bwa.sh);
```

Executing multiple mapping runs in parallel
===========================================

For this task, many programs can be used, from simple shell background
spawning using & (in bash) to job managers orchestrating a big network
of worker machines. In this package, a simple programm is implemented
which executes a user-definable number of jobs in parallel and
waits with spawning new ones until another of its already started jobs
finishes.

Note that it is possible to use user-defined shell functions or
variables, if they are made available using the `export VARIABLE` or
`export -f FUNCTION` bash commands (replace UPPERCASE letters by 
actual name). Refer to the manual of your shell if you're using a 
different shell than bash.

Note as well that more CPU cores than started parallel processes are
needed if the mappers run on multiple cores themselves. Whether to
exploit parallelism implemented in the mappers or to use
`mcall.py` is up to you.

Invoke `scripts/general/mcall.py --help` to get more information about
this tool.

Example: Run the previously generated mapper calls. 

```{.bash}
    # Export variable for use in mcall.py
    export fastq="$(pwd)/data/3/all.fastq"
    # Execute calls, at 2 cores
    scripts/general/mcall.py -c data/4/calls -t 2 \
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
[main] Version: 0.7.12-r1039
[main] CMD: bwa aln -n 0 -k 2 data/genome/sample /home/motschow/Studium/Hiwi/hiwiwork/manual/data/3/all.fastq
[main] Real time: 0.085 sec; CPU: 0.000 sec
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
@PG	ID:bwa	PN:bwa	VN:0.7.12-r1039	CL:bwa samse data/genome/sample data/4/0.sai /home/motschow/Studium/Hiwi/hiwiwork/manual/data/3/all.fastq
sample_0	4	*	0	0	*	*	0	0	AGAATGAAAACTTGCCATTTG	FFFFFFFFFFFFFFFFFFFFF
sample_1	4	*	0	0	*	*	0	0	AACCATGGCCCACATAGGCAGGCAT	FFFFFFFFFFFFFFFFFFFFFFFFF
sample_2	4	*	0	0	*	*	0	0	ATCCTGCGAAGGAGCCCGAG	FFFFFFFFFFFFFFFFFFFF
sample_3	4	*	0	0	*	*	0	0	TGTTGCTTTTGTTTCCCTAGGCATA	FFFFFFFFFFFFFFFFFFFFFFFFF
sample_4	4	*	0	0	*	*	0	0	GAGGAGAAAGTAGATAAAAA	FFFFFFFFFFFFFFFFFFFF
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
scripts/eval/sam-extract.R --sam-fields qname,rname,pos,mapq \
    data/4/1.sam  >  data/5/1.tab
```
```{.output}
```

```{.bash}
head data/5/1.tab | column -t
```
```{.output}
qname     rname  pos   mapq
sample_0  B1     755   0
sample_1  *      0     0
sample_2  X      3674  37
sample_3  *      0     0
sample_4  B1     3675  23
sample_5  *      0     0
sample_6  B2     4974  37
sample_7  A3     1510  37
sample_8  *      0     0
```

```{.bash}
tail data/5/1.tab | column -t
```
```{.output}
retli_15  *  0  0
retli_16  *  0  0
retli_17  *  0  0
retli_18  *  0  0
retli_19  *  0  0
retli_20  *  0  0
retli_21  *  0  0
retli_22  *  0  0
retli_23  *  0  0
retli_24  *  0  0
```

Bring together true read information from all origin organisms
--------------------------------------------------------------

This can be done by concatenating the tabular files generated during
the read sampling process (Section 2). `awk` is used to concatenate
the files while not repeating the header line of the second file:

```{.bash}
awk '(NR==1 || FNR!=1)' \
      data/2/sample.tab \
      data/2/retli.tab  \
    > data/5/all.tab
```
```{.output}
```

Alternatively: Do the same and additionally ensure that the header 
lines of the two files match.

```{.bash}
awk '(NR==1){
         header=$0
     }(FNR==1 && header!=$0){
         print "Headers dont match!"|"cat >&2"
         exit 1
     }(NR==1 || FNR!=1){
        print
     }' \
     data/2/sample.tab \
     data/2/retli.tab  \
   > data/5/all.tab
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
scripts/eval/exactmap.R data/5/all.tab \
                        data/5/1.tab  \
                      > data/5/1.crct

cat data/5/1.crct | column -t
```
```{.output}
read       m.orig  t.orig    mapq  correct
retli_0    *       retli_tr  0     FALSE
retli_1    *       retli_tr  0     FALSE
retli_10   *       retli_tr  0     FALSE
retli_11   *       retli_tr  0     FALSE
retli_12   X       retli_tr  25    FALSE
retli_13   *       retli_tr  0     FALSE
retli_14   *       retli_tr  0     FALSE
retli_15   *       retli_tr  0     FALSE
retli_16   *       retli_tr  0     FALSE
retli_17   *       retli_tr  0     FALSE
retli_18   *       retli_tr  0     FALSE
retli_19   *       retli_tr  0     FALSE
retli_2    *       retli_tr  0     FALSE
retli_20   *       retli_tr  0     FALSE
retli_21   *       retli_tr  0     FALSE
retli_22   *       retli_tr  0     FALSE
retli_23   *       retli_tr  0     FALSE
retli_24   *       retli_tr  0     FALSE
retli_3    *       retli_tr  0     FALSE
retli_4    *       retli_tr  0     FALSE
retli_5    *       retli_tr  0     FALSE
retli_6    *       retli_tr  0     FALSE
retli_7    *       retli_tr  0     FALSE
retli_8    *       retli_tr  0     FALSE
retli_9    *       retli_tr  0     FALSE
sample_0   B1      A2        0     FALSE
sample_1   *       B2        0     FALSE
sample_10  *       A2        0     FALSE
sample_11  B4      B4        37    TRUE
sample_12  A2      A2        37    TRUE
sample_13  B1      B2        37    FALSE
sample_14  B3      B3        37    TRUE
sample_15  B1      B1        37    TRUE
sample_16  *       B4        0     FALSE
sample_17  *       X         0     FALSE
sample_18  MT      MT        37    TRUE
sample_19  MT      MT        37    TRUE
sample_2   X       X         37    TRUE
sample_20  B3      B3        37    TRUE
sample_21  A1      A1        37    TRUE
sample_22  *       B4        0     FALSE
sample_23  B4      B4        37    TRUE
sample_24  *       B4        0     FALSE
sample_3   *       B2        0     FALSE
sample_4   B1      B1        23    TRUE
sample_5   *       A2        0     FALSE
sample_6   B2      B2        37    TRUE
sample_7   A3      A3        37    TRUE
sample_8   *       MT        0     FALSE
sample_9   B3      B3        25    TRUE
```


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
record    organism
A1        volpertinger
A2        volpertinger
A3        volpertinger
B1        volpertinger
B2        volpertinger
B3        volpertinger
B4        volpertinger
MT        volpertinger
X         volpertinger
retli_tr  retli
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
t.orig    m.orig  read       mapq  correct  m.org         t.org
A1        A1      sample_21  37    TRUE     volpertinger  volpertinger
A2        A2      sample_12  37    TRUE     volpertinger  volpertinger
A2        *       sample_5   0     FALSE    *             volpertinger
A2        B1      sample_0   0     FALSE    volpertinger  volpertinger
A2        *       sample_10  0     FALSE    *             volpertinger
A3        A3      sample_7   37    TRUE     volpertinger  volpertinger
B1        B1      sample_15  37    TRUE     volpertinger  volpertinger
B1        B1      sample_4   23    TRUE     volpertinger  volpertinger
B2        *       sample_3   0     FALSE    *             volpertinger
B2        B1      sample_13  37    FALSE    volpertinger  volpertinger
B2        *       sample_1   0     FALSE    *             volpertinger
B2        B2      sample_6   37    TRUE     volpertinger  volpertinger
B3        B3      sample_20  37    TRUE     volpertinger  volpertinger
B3        B3      sample_14  37    TRUE     volpertinger  volpertinger
B3        B3      sample_9   25    TRUE     volpertinger  volpertinger
B4        *       sample_16  0     FALSE    *             volpertinger
B4        *       sample_24  0     FALSE    *             volpertinger
B4        B4      sample_11  37    TRUE     volpertinger  volpertinger
B4        *       sample_22  0     FALSE    *             volpertinger
B4        B4      sample_23  37    TRUE     volpertinger  volpertinger
MT        MT      sample_19  37    TRUE     volpertinger  volpertinger
MT        MT      sample_18  37    TRUE     volpertinger  volpertinger
MT        *       sample_8   0     FALSE    *             volpertinger
retli_tr  *       retli_0    0     FALSE    *             retli
retli_tr  *       retli_1    0     FALSE    *             retli
retli_tr  *       retli_10   0     FALSE    *             retli
retli_tr  *       retli_11   0     FALSE    *             retli
retli_tr  *       retli_24   0     FALSE    *             retli
retli_tr  *       retli_13   0     FALSE    *             retli
retli_tr  *       retli_14   0     FALSE    *             retli
retli_tr  *       retli_15   0     FALSE    *             retli
retli_tr  *       retli_16   0     FALSE    *             retli
retli_tr  *       retli_17   0     FALSE    *             retli
retli_tr  *       retli_18   0     FALSE    *             retli
retli_tr  *       retli_19   0     FALSE    *             retli
retli_tr  *       retli_2    0     FALSE    *             retli
retli_tr  *       retli_20   0     FALSE    *             retli
retli_tr  *       retli_21   0     FALSE    *             retli
retli_tr  *       retli_22   0     FALSE    *             retli
retli_tr  *       retli_23   0     FALSE    *             retli
retli_tr  *       retli_6    0     FALSE    *             retli
retli_tr  *       retli_3    0     FALSE    *             retli
retli_tr  *       retli_4    0     FALSE    *             retli
retli_tr  *       retli_5    0     FALSE    *             retli
retli_tr  *       retli_7    0     FALSE    *             retli
retli_tr  *       retli_8    0     FALSE    *             retli
retli_tr  *       retli_9    0     FALSE    *             retli
retli_tr  X       retli_12   25    FALSE    volpertinger  retli
X         X       sample_2   37    TRUE     volpertinger  volpertinger
X         *       sample_17  0     FALSE    *             volpertinger
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
t.org         m.org         correct  count
retli         *             FALSE    24
volpertinger  *             FALSE    9
retli         volpertinger  FALSE    1
volpertinger  volpertinger  FALSE    2
volpertinger  volpertinger  TRUE     14
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
t.org         m.org         correct  count
retli         *             FALSE    24
retli         volpertinger  FALSE    1
volpertinger  *             FALSE    9
volpertinger  volpertinger  FALSE    2
volpertinger  volpertinger  TRUE     14
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
map.true  map.actl  sensitivity  nomap.true  nomap.actl  specificity  bcr
25        14        0.56         25          24          0.96         0.76
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
map.true  map.actl  sensitivity  nomap.true  nomap.actl  specificity  bcr   runidx
25        0         0            25          25          1            0.5   0
25        14        0.56         25          24          0.96         0.76  1
25        20        0.8          25          5           0.2          0.5   2
25        0         0            25          25          1            0.5   3
25        14        0.56         25          24          0.96         0.76  4
25        21        0.84         25          5           0.2          0.52  5
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
runidx  map.true  map.actl  sensitivity  nomap.true  nomap.actl  specificity  bcr   k   n
0       25        0         0            25          25          1            0.5   2   0
1       25        14        0.56         25          24          0.96         0.76  2   4
2       25        20        0.8          25          5           0.2          0.5   2   8
3       25        0         0            25          25          1            0.5   10  0
4       25        14        0.56         25          24          0.96         0.76  10  4
5       25        21        0.84         25          5           0.2          0.52  10  8
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




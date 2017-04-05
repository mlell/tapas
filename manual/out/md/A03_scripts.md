---
title:
  - Appendix A3 -- Overview of the scripts by category
---

Below you find a list of the scripts in this package, grouped by rough
application situations. 

More specific help for each command can be obtained by invoking the respective
command with the `--help` or `-h` command line argument.

General file and table manipulation
-----------------------------------

Name                 Purpose
----                 -------
add_const_column     Add a column with a column name and fixed value.
cat_tables           Concatenate tables with the same headers.
cross_tab            Print all combinations of input table rows.
fill_template        Output copies of a file, where placeholders are replaced by values read from a table.
index_column         Add a column with a name and a counting number to the table.
merge                Based on values of table 1, look up corresponding rows of table 2 (table join).
pocketR              Change text tables by R commands.
write_later          Cache the input and write it only after input completion, to enable file modification without (explicit) temporary files.

Read sampling and fitering
--------------------------

Name          Purpose
----          -------
filter_fastq  Apply a program to ID, nucleotide or quality string of each read.
uniform       Sample reads from a reference genome.
synth_fastq   Create a FASTQ file from input IDs, nucleotide strings and quality strings.

Introducing mutations into reads
--------------------------------

Name                 Purpose
----                 -------
geom_induce          Change bases of input nucleotide strings with a probability dependent of proximity to the string beginning or end.
mapdamage2geomparam  Parse output of mapDamage an output a table of base mutation probabilities.
multiple_mutate      Based on a table of base mutation probabilities, apply multiple mutation rounds to nucleotide strings.
plot_mutation_probabilities  Plot mutation probability versus base position.

Parallel program calls (e.g. mappers)
--------------------------------------

Name             Purpose
----             -------
mcall            Read a list of program calls and invoke several of them in parallel.
table2calls      Based on a table of parameters, generate calls to a script with changing parameters.


SAM parsing and result data handling
------------------------------------

Name                     Purpose
----                     -------
add_mapped_organisms     Add organisms relating to FASTA record names in the input tables to the output.
plot_read_fate           Plot how many reads from which origin were mapped to which target organism correctly or incorrectly.
plot_parameter_effects   Plot how much mapping parameters influence sensitivity or specificity
sam_extract              Extract information from a SAM file into a text table.
sensspec                 Calculate sensitivity and specificity of a mapping run.




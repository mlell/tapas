# This is a Snakefile. Run it by calling "snakemake -s FILE"

from pipeline_helpers import cross_product, read_tab, \
                             write_tab
import itertools
import re

#    Constants
# ============================================================================

pr                  = os.environ["pr"]
# Script directory
d_sps               = pr+"/mapper-compare"

# Worker Scripts
s_md2geomparam      = d_sps+"/distribution-parametrization/"+ \
                                     "mapdamage2geomparam.py"
s_filter_fastq      = pr+"/scripts/filter-fastq.py"
s_multiple_mutate   = d_sps+"/induce-errors/multiple_mutate.py"
s_map_bwa           = d_sps+"/bwa/map-reads-bwa.sh"
s_eval_mapping      = d_sps+"/eval/eval-mapping.sh"
s_tab2line          = pr+"/scripts/tab2line.py"

# Output directory
d_out               = pr+"/data/gen/150620-ruffus-test"

#    Input data
# ============================================================================

#  *  MapDamage
d_in_md=pr+"/data/in/150325_mapdamage_johanna_alex"
#  *  Unmutated Reads
in_reads=pr+"/data/gen/150602-reads/unmut/reads.fastq"

#  *  Mapping: BWA
bwa_ref=pr+"/mapper-compare/bwa/Usp_mito/Usp_mito"

#    Output parameters
# ============================================================================

# Levels of artificial additional sequence divergence introduced.
mut_levels        = [ 0, 0.01, 0.02, 0.05, 0.1 ]

# Mapper parameters. Each combination of these is tried.

bwa_parameters = { "-n" : [0.04, 0.08, 0.15],
                   "-l" : [ 999, 4 ],
                   "-k" : [ 2, 10 ],
                   "-M" : [ 3, 1, 10 ]}

bwa_par_combinations = cross_product(bwa_parameters)
bwa_run_index_range  = range(0, len(bwa_par_combinations))
 

workdir: pr+"/data/gen/snakemake-test/"

#    Targets aka Pseudo-Rules
# ============================================================================

# These rules can be called as an argument to 'snakemake'. They produce no
# output, only trigger the execution of other rules by requiring certain
# files.

rule all:
    """ First rule, executed by default. Starting from this rule, all 
    rules this rule depends on are executed.  """
    input: "bwa.eval"


#     Rules
# ============================================================================


rule fit_distribution: 
    """ Fit a geometric distribution to a mapDamage dataset """
    input:  expand( "{dir}/GS136_{d}_freq.txt" \
                  , d=["3pGtoA","5pCtoT"]      \
                  , dir=d_in_md )
    output: "fit/GS136.tab"
    shell:
        "{s_md2geomparam} --fit-plots fit/GS136_fit_plots/ {input} > {output}" 


rule add_mutation_line:
    " Add a line causing a constant mutation probability "
    input: "fit/GS136.tab"
    output: "par/c_{level}.tab"
    shell: """
        cp {input} {output}
        #     strand from to  factor  geom_prob intercept
        echo "3      *    *   0       0.1       {wildcards.level}"   >> {output}
        """


rule mutate_reads:
    """ Mutate the bases of a FASTQ file following a table containing
    probabilities """
    input: "par/c_{level}.tab"
    output: "fastq/c_{level}.fastq"
    shell:"""
        python2 {s_filter_fastq}  \
            --nucleotide @ {s_multiple_mutate} {input} @ \
            < {in_reads}  \
            > {output}
        """

rule bwa_parameter_table:
    "Provide BWA parameters for a given run index."
    output: "bwa/mut_{mut_level}/run_{run_index}.tab"
    run:
        run_index = int(wildcards.run_index)
        print( bwa_par_combinations[run_index])
        write_tab( [bwa_par_combinations[run_index]] , output[0] )


rule map_bwa:
    "Map a FASTQ set using a file with BWA parameters"
    input: partab = "bwa/mut_{mut_level}/run_{run_index}.tab" \
         , fastq  = "fastq/c_{mut_level}.fastq"
    params: out_dir = "bwa/mut_{mut_level}/run_{run_index}"
    output: "bwa/mut_{mut_level}/run_{run_index}/aln.sam"
    log:    "bwa/mut_{mut_level}/run_{run_index}.log"
    run:
        bwa_par = read_tab(input.partab,header=True)[0] # only 1 row in table
        # Merge dictionary to flat list
        # { "-a":3, "-b":4 } >> [ "-a", "3", "-b", "4" ]
        mut_level = wildcards.mut_level
        out_dir = str(output)[:-8]
        print(out_dir)
        par_list = [ [k,v] for (k,v) in bwa_par.items() ]
        par_list = list(itertools.chain(*par_list))
        shell("""
        echo {s_map_bwa} {input.fastq} {bwa_ref} {out_dir} {par_list} > {log}
        {s_map_bwa} {input.fastq} {bwa_ref} {out_dir} {par_list}
        """)


rule eval_bwa:
    "Count false and true read alignments and misalignments"
    input: rules.map_bwa.output
    output: eval="bwa/mut_{mut_level}/run_{run_index}.eval", \
             pdf="bwa/pdf_eval/mut_{mut_level}_run_{run_index}.pdf"
    shell: " {s_eval_mapping} -s {output.eval} {input} 25 {output.pdf}"


rule linerarize_table:
    "Convert a 2D table into only one line plus header"
    input: "{name}.eval"
    output: "{name}.eval1"
    shell: """
       {s_tab2line} {input} > {output} 
        """

# In Input: Braces referring to wildcards, and not to variables to be consumed
# by expand, must be escaped by doubling the braces. These Wildcards are 
# replaced after the call of expand. expand removes one pair of braces.
# Wildcards are determined by the output files that are required, whereas
# the variables in expand are specified in the expand call.
rule summary_mutation_level:
    """Collect output of all BWA runs (with different parameters) of one
    FASTQ set and output a table with one line per run"""
    input:
        eval = expand("{{folder}}/mut_{{mut_level}}/run_{run_index}.eval1",
                run_index = bwa_run_index_range),
        par  = expand("{{folder}}/mut_{{mut_level}}/run_{run_index}.tab",
                run_index = bwa_run_index_range)
    output: t1 = temp("{folder}/mut_{mut_level}.mleval.1"),
            t2 = temp("{folder}/mut_{mut_level}.mleval.2"), 
            o  = "{folder}/mut_{mut_level}.mleval"
    shell: """
        # Print first line of first file and second line of every file
        awk '(NR == 1); (FNR == 2)' {input.par} > {output.t1}
        awk '(NR == 1); (FNR == 2)' {input.eval} > {output.t2}
        
        paste -d "\t" {output.t1} {output.t2} > {output.o}
        
        # Add column named "divergence" containing the mutation level
        # Note that awk commands need to be escaped in order to
        # not be mistaken for file wildcards!
        awk '(NR == 1) {{print $0 "\t" "divergence"}} 
             (NR != 1) {{print $0 "\t" {wildcards.mut_level} }}' \
             {output.o} > {output.t1}

        cp {output.t1} {output.o}
        """


rule summary_bwa:
    """Collect summaries of BWA runs against different mutation levels"""
    input: expand("bwa/mut_{mut_level}.mleval",mut_level=mut_levels)
    output: "bwa.eval"
    shell: """
        awk '(NR == 1); (FNR != 1)' {input} > {output}
        """






# vim: ft=python : tw=80

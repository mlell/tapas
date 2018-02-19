#!/bin/bash
# This bash script summarises the pipeline which is outlined in the 
# manual

# Stop if an error occurs or a variable is unknown
set -ue

# Variables
# =========================================================================
# 
# Folders
# -------
# 
# The paths here currently assume that this script lies in the manual/
# folder of TAPAS and is executed there. You need to adapt the paths
# if you execute this script from another location. 
#
# The manual/ folder of TAPAS.
tapasmanual="."
# The scripts/ folder of TAPAS.
tapas="scripts"
# Where the results of this script are saved
outputdir="tapas-example.out"
# Where the input data comes from
inputdir="${tapasmanual}/input"
# Where the TAPAS scripts are saved

# Input files
# ------------
#
# Names of the used genomes
g_names=("volpertinger" "retli")
# Paths to the used example genomes, without file extensions.
# The .fasta and .fai-file (samtools index) files for the genome
# must be present.
declare -A g_paths
# A heavily truncated cat genome.
g_paths[volpertinger]="${inputdir}/genome/volpertinger"
# A heavily truncated R. etli genome. 
g_paths[retli]="${inputdir}/retli/retli_tr"


# Preparations
# =========================================================================
#
# Create the output folder
mkdir "$outputdir"

# Check if the paths are correct
if [ ! -f "${tapasmanual}/gen-html.sh" ]; then
    cat >&2 <<EOF 
Error: Your working directory is outside the TAPAS manual folder.  Either
move into the TAPAS manual/ folder by using the cd command or adapt the
paths "tapas" and "tapasmanual" at the beginning of this file to point to
the TAPAS scripts folder and the TAPAS manual/ folder, respectively.
EOF
fi

# Generate artificial reads
# =========================================================================

# Generate 25 reads, with a minimum length of 20bp and length 
# decay parameter of 5 (higher values lead to longer output reads).
# If you want reproducible results, you can use the --seed parameter.
for g in ${g_names[@]}; do
    echo $g
    "$tapas"/uniform "${g_paths[$g]}.fasta" \
        --name "${g}_" \
        --output "${outputdir}/${g}.coord" \
                 "${outputdir}/${g}.nucl" \
        25 20 5
done

# Introduce mutations into the reads
# ========================================================================
# 
# Write a file which contains the parameters for point mutations.
cat >"${outputdir}/mut.tab" <<EOF
strand   from   to   factor  geom_prob  intercept
3p       C      T    0.3     0.4        0.1
5p       C      T    0.1     0.2        0.0
3p       *      *    0.0     0.1        0.12
EOF

# Subject the endogenous reads to mutations
# If you want reproducability, you can use the --seed parameter.
"${tapas}"/multiple_mutate  \
    "${outputdir}/mut.tab" \
  < "${outputdir}/volpertinger.nucl" \
  > "${outputdir}/volpertinger.mut.nucl"

# Merge the reads from the different genomes
# ========================================================================

# bash expands dir/{file1,file2} to dir/file1 dir/file2.
# {...} must be outside of "..." like below, else it will be taken as-is.
cat "${outputdir}"/{volpertinger.mut,retli}.nucl > "${outputdir}/all.nucl"
cat "${outputdir}"/{volpertinger,retli}.coord > "${outputdir}/all.coord"

# Create the FASTQ file of the synthetic reads
# ========================================================================
# The three arguments are the sources for (i) nucleotides (ii) quality
# strings, (iii) read names. Google "bash process substitution if you're
# not familiar with what "<(...)" means.
"${tapas}"/synth_fastq \
    "${outputdir}/all.nucl" \
    <(sed 's/./F/g' "${outputdir}/all.nucl") \
    <(awk '(NR>1){print $1}' "${outputdir}/all.coord") \
    > "${outputdir}/all.fastq"


# Set the parameters to test
# ========================================================================
#
# This code generates a table which contains the parameters for each
# mapping run to be performed. Later, the suitability of the chosen
# parameter values is judged based on the outcomes of these mapping runs. 
# The <(...) parts generate the *.par files mentioned in the manual and 
# input them into the cross_tab tool in one step. Exectute one of
# the contents of `printf ...`  by itself to see that it generates a file
# like shown in the manual (*.par). Finally, an index column called 
# `runidx` is prepended to the result. This column is used for output file
# naming. 

"${tapas}"/cross_tab --head 1 \
    <(printf "%s\n" k 2 10) \
    <(printf "%s\n" n 0 4 8) \
  | "${tapas}"/index_column --colname runidx \
    > "${outputdir}/partab"

# Set the needed steps perform a mapping
# ========================================================================
#
# Write a file which will be executed later for each parameter combination.
# It contains the mapper name and how to call it to perform the mapping. 
# This design ensures TAPAS can be used with every mapper. 
# 
# The ${...} strings will be replaced by arguments to the short read mapper.
# Some are variable, in this case ${n} and ${k}. They are determined by the
# file `partab` from the previous step. Some are constant, like
# ${reference}, the path to the reference genome, or ${reads}, the path to
# the read FASTQ file. The values of these variables will be determined in 
# the step following this step.
# 
# Technical node: Here <<'EOF' must be used instead of <<EOF to ensure the
# ${...} strings are written into the map.sh output file unchanged. 
# Alternatively, the contents below (between cat... and EOF, excluding)
# can also be saved manually into a file using a text editor.
cat > "${outputdir}/map.sh" << 'EOF' 
#!/bin/bash

# Security measure: Stop if one of the needed parameter
# values is not present (wrong commands used by the user)
set -ue

# All error messages will be written here
exec 2> "${outputdir}/map-${runidx}.log"

bwa aln -n "${n}" -k "${k}" \
    "${reference}" \
    "${reads}" \
    > "${outputdir}/${runidx}.sai"

bwa samse \
      "${reference}" \
      "${outputdir}/${runidx}.sai" \
      "${reads}" \
      > "${outputdir}/${runidx}.sam"
EOF
chmod u+x "${outputdir}/map.sh" # make the script executable

# Perform the mapping runs
# ========================================================================
# 
# table2calls uses the table of parameter combinations to generate 
# programm calls to start the mapping via the script shown in the previous
# section. mcall then executes several of the calls in parallel, starting
# several mapping processes in parallel.
# All of the variables ${...} used in the script in the previous section 
# must either be present in the file partab (generated in the section before
# the previous section) or be set to a constant value using the --const 
# option.
"${tapas}"/table2calls  \
    --const reference "${g_paths[volpertinger]}" \
    --const reads "${outputdir}/all.fastq" \
    --const outputdir "${outputdir}" \
    "${outputdir}/partab" \
    "${outputdir}/map.sh" \
  | "${tapas}"/mcall -t 4 --status


# Define the analysis steps for a SAM file
# =========================================================================
# The following analysis steps need to be performed for each resulting
# SAM file. Therefore they are first defined in a function, and later
# called for every sam file
function analyseSAM(){
    sam="$1"
    # Get the SAM file name without the extension .sam: "4.sam" -> "4"
    p=${sam%.sam}

    # Convert SAM to text table
    "${tapas}"/sam2table "${sam}" > "${p}.tab"

    # Look up the true origin genomes and locations of the reads
    "${tapas}"/add_mapped_organisms \
        --endogenous volpertinger \
                     "${g_paths[volpertinger]}.fasta.fai" \
                     "${outputdir}/volpertinger.coord" \
        --exogenous  retli \
                     "${g_paths[retli]}/.fasta.fai" \
                     "${outputdir}/retli.coord" \
        "${p}.tab" \
        | "${tapas}"/write_later "${p}.tab"


    # Determine whether each read was correctly mapped
    "${tapas}"/pocketR '
        within(input, {
            correct =
                mapped_pos == true_start  &
                mapped_rname == true_record &
                mapped_organism == true_organism })
    '  "${p}.tab" \
    | "${tapas}"/write_later "${p}.tab"

    # Count reads per origin/target organism and mapping status
    "${tapas}"/pocketR '
        aggregate( cbind(count=qname) ~ true_organism + mapped_organism + correct,
            FUN=length, data=input) ' \
    "${p}.tab" \
    > "${p}.agg"

    # Plot mapping targets per origin organism
    "${tapas}"/plot_read_fate --exogenous retli \
                              --format png \
                              true_organism    mapped_organism \
                              correct          count \
                              "${p}-fate.png"  "${p}.agg"

    # Calculate sensitivity, specificity and balanced accuracy
    "${tapas}"/sensspec --c-morg mapped_organism \
                        --c-torg true_organism \
                        "${p}.agg" volpertinger \
        > "${p}.performance"

    echo "$sam done. -> Generated ${p}.{tab,agg,png,performance}"
}

# Execute the above steps for each generated sam file
for s in "${outputdir}"/*.sam; do
    analyseSAM "${s}"
done

echo "Done. The output files can be found in $(readlink -f "${outputdir}")."


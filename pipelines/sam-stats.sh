#' Don't delete anything if executed non-interactively
set -ueC

if [[ $# -ne 2 || ${1-"x"} == "-h" ]]; then
    echo "Usage: calc-mapper-stats.sh SAM_DIR QTHRES" >&2
    exit 1
fi
#' Input arguments
#' Directory containing SAM files, with numerical file name
samdir="$1"
qthres="$2"

# Constants
NTHREADS=$(cat $pr/NTHREADS)

#' Used scripts
#' ============

s_mcall="$pr/scripts/mcall.py"
s_sam_extract="$pr/mapper-compare/eval/sam-extract.R"
s_pocketr="$pr/scripts/pocketR.R"
#' Folders containing alignments
d_gen="$pr/data/gen"

cd $samdir

# Check if there are any SAM files here
samgzfiles=(*.sam.gz)
if [ ! -f ${samgzfiles[0]} ]; then
    echo "There are no .sam.gz files in this directory!"
    exit 1
fi


#' Extract relevant information from the SAM files:
#' * read name, map target name, map position, mapping quality
#' * true (t) origin organism and chromosome, obtained from read name
#' * true origin, obtained by concatenating true organism and true 
#'   chromosome
for samgz in *.sam.gz; do
    # Remove .sam.gz extension
    fn=${samgz%.sam.gz} 
    echo "$s_sam_extract --gz \
                         --sam-fields qname,rname,pos,mapq \
                         --pattern {torg}_{tchr}_{tpos}_.* \
                         --collate trname={torg}_{tchr} \
                         $samgz > ${fn}.tab "
done | $s_mcall -t $NTHREADS --status > /dev/null


#' * Add run number to the statistic tables
#' * Add column for organism the read has been mapped to
#'   (remove _0 from SAM rname field)
for f in *.tab; do
    runnr=${f%.tab}
    #echo $samdir/$f
    awk -v runnr=$runnr -v OFS=$"\t" \
         '(NR==1){print $0,"run";next};
                {print $0,runnr}' \
        $f > ${f}.tmp && \
        mv ${f}.tmp $f
    printf "$f done\r"
done 

#' Replace origin to match
echo "Replace name of target genome..."
old_ref_name="gi|195661114|ref|NC_011112\.1|"
new_ref_name="uspemito_0"
for f in *.tab; do
    echo "sed -i 's/$old_ref_name/$new_ref_name/g' '$f' " 
done | $s_mcall -t $NTHREADS --status > /dev/null

#' Aggregate: Count reads of different groups

echo "Save if correct map..."
for f in *.tab; do
    n=${f%.tab}
    cat << EOF
    $s_pocketr ' 
    within(input,{ 
        org <- sub("_.*$","",rname)
        correct.mapping <- (rname == trname) & (pos == tpos)
        high.quality    <- mapq  >  '$qthres'
    })' \
        < $f > ${f}.tmp &&
    mv ${f}.tmp $f

    $s_pocketr '
    o <- aggregate(qname ~ torg + org + correct.mapping + high.quality, 
                   data = input, FUN = length)
    o\$run <- '$n'
    names(o)[names(o)=="qname"] <- "count"
    return(o)' \
        < $f > ${n}.agg

    EOR
EOF
done | $s_mcall --sep "EOR" -t $NTHREADS --status > /dev/null




# vim: tw=80:ft=sh


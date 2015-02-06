#!/usr/bin/bash
set -ue

#' Download the pig genome
#' =======================

url="ftp://ftp.ncbi.nlm.nih.gov/genomes/Sus_scrofa/Assembled_chromosomes/seq/"

d="$pr/data/in/ref/tmp/sscrofa_genome"
mkdir $d
cd $d

for i in $(echo {1..18} X Y MT); do
    wget "${url}/ssc_ref_Sscrofa10.2_chr${i}.fa.gz"
done

cat ssc_ref_*.fa.gz > ../SusScrofa.fasta.gz
rm ssc_ref_*.fa.gz

cd --



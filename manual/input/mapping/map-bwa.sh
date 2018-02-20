#!/bin/bash

## This script performs a mapping using BWA.
## It requires the variables k, n, runidx and fastq be set 
## prior to its execution. That step can be performed by 
## the tool table2calls.

# Fail if any needed variable is not set
set -ueC
# Redirect all output to a log file
exec 2>"${outdir}/${runidx}.log" >&2

bwa aln -n ${n} -k ${k} \
    "${genome}" \
    "${reads}" \
    > "${outdir}/${runidx}.sai"

bwa samse \
      "${genome}" \
      "${outdir}/${runidx}.sai" \
      "${reads}" \
      > "${outdir}/${runidx}.sam"


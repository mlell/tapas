#!/bin/bash
# Prepare the current directory for the output of mapping runs
# and set needed variables

export d_reads="$pr/data/gen/multi-origin_reads";
export bowtie_index="$pr/mapper-compare/bowtie/Usp/Usp";

mkdir log
mkdir run


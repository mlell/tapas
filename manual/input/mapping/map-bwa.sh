#!/bin/bash

## This script performs a mapping using BWA.
## It requires the variables k, n, runidx and fastq be set 
## prior to its execution. That step can be performed by 
## the tool table2calls.

# Fail if any needed variable is not set
set -ue

bwa aln -n ${n} -k ${k}      \
    input/genome/volpertinger \
    data/3/all.fastq         \
    > data/4/${runidx}.sai   \
    2> data/4/${runidx}.log   &&

bwa samse                      \
      input/genome/volpertinger \
      data/4/${runidx}.sai     \
      data/3/all.fastq         \
      > data/4/${runidx}.sam   \
      2>> data/4/${runidx}.log


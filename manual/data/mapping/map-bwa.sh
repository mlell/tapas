#!/bin/bash

## This script performs a mapping using BWA.
## It requires the variables k, n, runidx and fastq be set 
## prior to its execution.

# Fail if any needed variable is not set
set -ue

bwa aln -n ${n} -k ${k}      \
    data/genome/volpertinger \
    data/3/all.fastq         \
    > data/4/${runidx}.sai   \
    2> data/4/${runidx}.log   &&

bwa samse                      \
      data/genome/volpertinger \
      data/4/${runidx}.sai     \
      data/3/all.fastq         \
      > data/4/${runidx}.sam   \
      2>> data/4/${runidx}.log


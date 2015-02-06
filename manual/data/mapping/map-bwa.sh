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


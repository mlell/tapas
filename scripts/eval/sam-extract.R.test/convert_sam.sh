#!/bin/bash

set -ue

awk 'BEGIN{OFS="\t"} ($3=="gi|195661114|ref|NC_011112.1|"){$3 = "mito"; print;next} {print}' $1

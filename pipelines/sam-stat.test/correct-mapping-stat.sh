#!/usr/bin/bash

set -ue

# Scripts
s_mapping_stat="$pr/mapper-compare/eval/mapping-stat.R"
s_pocket_r="$pr/scripts/pocketR.R"

sam="$1"
stat_out="$2"

$s_mapping_stat --gz --sam-fields qname,rname,pos,mapq \
                --pattern "^{org}_{tpos}" "$sam" | \
$s_pocket_r \
'o <- within(input,{ 
    corr <- pos == tpos
    hq   <- mapq > 20
})
aggregate(qname ~ org + rname + corr + hq, o, length)' \
    > "$stat_out"

"$pr/mapper-compare/eval/plot-mapping-stat.R" org rname corr qname plot.pdf stat 


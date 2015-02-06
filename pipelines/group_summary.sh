#!/bin/bash

set -ueC

if [[ $# -ne 3 || $1 = "-h" ]]; then
    echo "Usage: group_summary.sh SAMDIR OUTFILE PAR_RUN_TAB" >&2
    exit 1
fi
samdir="$1"
output_file="$2"
par_run_tab="$3"

#' Scripts
#' =======

s_pocketr="$pr/scripts/pocketR.R"

awk '(FNR != 1||FNR==NR)' "$samdir"/*.agg > "${output_file}.agg"
awk '(FNR != 1||FNR==NR)' "$samdir"/*.tab > "${output_file}.tab"

cd "$(dirname $output_file)"

$s_pocketr '
merge(inputs[[1]], inputs[[2]], by.x="run", by.y="index")
' "${output_file}.agg" "$par_run_tab" > "${output_file}.agg.tmp" &&
mv "${output_file}.agg.tmp" "${output_file}.agg"







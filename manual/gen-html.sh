#!/bin/bash

set -ue

thisdir="$(dirname "$(readlink -f "$0")")"
cd "$thisdir"

# Empty data output directories
rm -rf   data/{1..6} data/2e
mkdir -p data/{1..6} data/2e

# Empty text output directories
rm -rf   out/html out/md
mkdir -p out/html out/md

mkdir tmp
trap "rm -r tmp" EXIT

# Remove vim modelines
for f in src/*.txt; do
    head -n-1 "$f"
done > manual.merged

gen-tools/pipeweave.py "bash --norc" < manual.merged >manual.md

sed 's/^```{.sh}/```{.bash}/' manual.md > manual.tmp && 
mv manual{.tmp,.md}

echo Pandoc...

pandoc --toc --mathml -s \
       -V toctitle:"Table of contents" \
       --template="pandoc.html.template" \
       --highlight-style=pygments \
       -f markdown+simple_tables \
       --css manual.css -i manual.md -o manual.html

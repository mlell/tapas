#!/bin/bash

set -ue

mkdir data/{1..6} || 
(cat >&2 <<EOF 

*** Folder creation failed. Remove folders named data/1 to data/6. ***
EOF
false
)

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

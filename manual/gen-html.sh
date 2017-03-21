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
    head -n-1 "$f" > "tmp/$(basename "$f")"
done

for f in tmp/*.txt; do
    echo "--- Chapter $f ---"
    md="${f%.txt}.md"
    html="${f%.txt}.html"
    gen-tools/pipeweave.py "bash --norc" <"$f" >"$md"

    # This enables bash syntax highlighting by pandoc
    sed 's/^```{.sh}/```{.bash}/' "$md" > "${md}.tmp" && 
    mv "${md}.tmp" "$md"

    echo Pandoc...

    pandoc --mathjax -s \
           --template="pandoc.html.template" \
           --highlight-style=pygments \
           -f markdown+simple_tables \
           --css ../../manual.css -i "$md" -o "$html"
           #-V toctitle:"Table of contents" \
done

mv tmp/*.html out/html
mv tmp/*.md   out/md

cat >toc.html <<EOF
<html>
<head> <title> Table of contents </title> 
<link rel="stylesheet" href="manual.css" type="text/css" />
<body>
<div class="title"> The TAPAS Manual</div>
<div class="content">
<ul>
EOF
grep --color=none -r '<title>' out/html |sort |\
    sed -E 's|^(.*):.*<title>(.*)</title>|<li><a href="\1">\2</a>|' \
    >> toc.html
   
cat >>toc.html <<EOF
</ul>
</div>
</body>
</html>
EOF


        


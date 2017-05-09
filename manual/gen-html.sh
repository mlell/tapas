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

rm -rf fig
mkdir  fig

mkdir tmp
trap "rm -r tmp" EXIT

# Remove vim modelines
for f in src/*.txt; do
    head -n-1 "$f" > "tmp/$(basename "$f")"
done

for f in tmp/*.txt; do
    echo "--- Chapter $f ---"
    bn="$(basename "$f")"
    md="out/md/${bn%.txt}.md"

    gen-tools/pipeweave.py "bash --norc" <"$f" >"$md"

    # This enables bash syntax highlighting by pandoc of {.sh} sections
    # only {.bash} is syntax highlighted, but {.sh} is executed and weaved
    # by pipeweave
    sed 's/^```{.sh}/```{.bash}/' "$md" > "${md}.tmp" && 
    mv "${md}.tmp" "$md"
done


for md in out/md/*.md; do
    fn="$(basename "$md")"
    html="out/html/${fn%.md}.html"
    echo "Pandoc $md -> $html ..."
    pandoc -s \
           --template="pandoc.html.template" \
           --mathjax \
           --highlight-style=pygments \
           -f markdown+simple_tables \
           --css manual.css -i "$md" -o "$html"
           #-V toctitle:"Table of contents" \
done

cat >toc.html <<EOF
<ul>
<li><a href="index.html">Package overview</a></li>
EOF
grep -I -r '<title>' out/html |sort |\
    sed -E 's|^out/html/(.*):.*<title>(.*)</title>|<li><a href="\1">\2</a>|' |\
    grep -v "index.html" \
    >> toc.html
   
cat >>toc.html <<EOF
</ul>
EOF

function printTOC(){
    # fn: if this string is found in a TOC line, the respective <a> element
    #     is assigned the "tochere" CSS class
    fn="${1?}"
    while IFS= read -r line; do
        if grep -I -F -q "$fn" <<< "$line"; then
            sed 's/<li>/<li class="tocthis">/' <<< "$line"
        else
            printf "%s\n" "$line"
        fi
    done < toc.html
}


# Insert the TOC into every file
for f in out/html/*.html; do
    echo "Add TOC: $f"
    # read removes all characters in $IFS by default
    while IFS= read -r line; do
        if [ "$line" = '<!-- ## TOC HERE ## -->' ]; then
            printTOC "$(basename "$f")"
        else
            printf "%s\n" "$line"
        fi
    done <"$f" >"$f.tmp" &&
    mv "$f.tmp" "$f"

done

rm -rf   ../docs
mkdir -p ../docs
mv out/html/* ../docs
cp fig-static/* fig
mv fig    ../docs
cp manual.css ../docs

        


#!/bin/bash
set -ueC

help(){
cat <<EOF
Usage: mapdamage2probabilities.sh < mapdamage-output

Extracts base exchange probabilities from mapDamage textual output.

The output is expected in the following form:

1lineoftext...
1  0.1234
2  0.1234
...

The first line is ignored, of the following lines the second column
is extracted and printed.
EOF
}

if [ $# -ne 0 ];then
    if [ $1 = "-h" ]; then
        usage
        exit 0
    else 
        help >&2
        exit 1
    fi
fi


awk '{ if (NR!=1) {print $2}}'


# vim: tw=70

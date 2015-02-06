#!/bin/bash

set -ue

# Don't overwrite any files by using output redirection (cmd > file)
set -o noclobber

if [[ ${1-} == '-i' ]];then
    inplace='true'
    shift
fi

if [[ ${1-} == "-h" || $# != 3 ]];then
    cat <<EOF

Usage: add_const_column.sh [-i] FILE NAME VALUE

Adds a column with the specified NAME and the VALUE to the FILE.

The column separator is a tabstop character.


Options
=======

 -i   Modify FILE in-place instead of printing the modified file to
      standard output


Example: add a column in-place
==============================

testfile before:

a   b   c
1   1   2
3   3   2
8   1   2

call: add_constant_column -i testfile d A

testfile after:

a   b   c   d
1   1   2   A
3   3   2   A
8   1   2   A
EOF
exit 1
fi

function add_col(){
    awk -vOFS=$'\t' \
        -vcolname="$2" -vcolval="$3" \
        '(NR==1){
             # Check if column of this name exists already
             split($0, hfields); 
             for(i in hfields){
                 if(hfields[i] == colname){
                     print "Column name "colname" exists already!"|"cat >&2"
                     exit 1
                 }
             }
         }
         # Append new column
         (NR==1){print $0,colname; next}; 
                {print $0,colval}' \
        "$1"
}

if [[ ! -z ${inplace-} ]]; then
    # Modify file $1 in-place:

    # Generate random string for temporary file naming
    rnd=$(cat /dev/urandom | tr -dc "a-zA-Z0-9" |head -c 16)

    # prepend tmp_ to filename
    input_dirname="$(dirname "$1")"
    tmpfile="$input_dirname/tmp_$rnd"

    # write result to temp file
    add_col "$1" "$2" "$3" > "$tmpfile"

    # Overwrite original file by file with added column
    mv "$tmpfile" "$1"

else 
    # Print result to standard output
    add_col "$1" "$2" "$3" 
fi




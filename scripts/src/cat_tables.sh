#!/bin/bash
set -ue 

function help(){
cat <<EOF >&2

Usage: cat_tables [-h | --help] [var=value]... [FILE]...

A simple wrapper around \`awk\` to concatenate tables without repeating
their headers. 

Only tables whose headers are the same can be concatenated, otherwise an error
is issued.

Output columns are separated by a tab character by default, change the 
OFS variable to another character to change this behaviour. See the parameter
section for information how this is done.

Parameters: 

    var=value
            Assign a variable in awk. Use the manual of awk (type "man awk"),
            section "Variables and Special Variables" to see a list of 
            variables which can be set. Take care not to include spaces
            around the "=" sign. Examples are FS (input column separator)
            and OFS (output column separator)

    FILE    File names of tables to be concatenated. Find an example input
            file below. An arbitrary number of file names can be specified
            (limited only by the maxmimum number of arguments of your shell)
            
            If no FILE argument is given or if it is "-", the input is read
            from standard input.

    -h, --help
            Display this help text and exit.

Example:

    ── FILE 1 ────
    a   b   c   d
    1   2   X   Y
    2   2   Y   Y
    2   3   X   Z
    ──────────────
    
    ── FILE 2 ────
    a   b   c   d
    6   8   A   C
    7   2   A   A
    9   9   B   C
    ──────────────

    Call: cat_tables FILE1 FILE2

    yields:

    ──────────────
    a   b   c   d
    1   2   X   Y
    2   2   Y   Y
    2   3   X   Z
    6   8   A   C
    7   2   A   A
    9   9   B   C
    ──────────────
EOF


}

if [[ ${1-x} = "--help" || ${1-x} = "-h" ]]; then
    help
    exit 0
fi

# Invoke awk and forward all arguments
awk '
# Save the first header
(NR == 1){
    split($0, header, FS);
}

# Compare each header to the first header and throw an error if it
# doesnt match 
(NR !=1 && FNR == 1){
    split($0, cheader, FS);
    for(i in cheader){
        if(cheader[i] != header[i]){
            print "Error: Input table headers do not match" | "cat>&2";
            exit 1;
        }
    }
}

# Output each input, but only the first input with included first line.
(NR == 1 || FNR != 1){
    # Assign a field to itself to recompute $0.
    # This is to make a change of OFS by the user take effect.
    $1=$1;
    print $0;
}
' OFS=$'\t' "$@"
    

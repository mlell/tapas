#!/usr/bin/bash
set -ueC

function usage(){
    cat >&2 <<EOF
    Usage: eval colnames.sh TABLE VARIABLE

    Saves the column names of TABLE to an associative array called VARIABLE
    
    The output of this script must be executed in the calling script using
    eval
EOF
}

# Parse optional arguments
start=0
while [ $# -gt 2 ]; do
    case $1 in
    -s)
        start=$2
        shift 2
        ;;
    -h)
        usage
        exit 0
        ;;
    *) 
        usage
        exit 1
        ;;
    esac
done

# Parse mandatory arguments
if [[ $# -ne 2 ]]; then
    usage
    exit 1
fi

table="$1"
variable="$2"

# Get input header line
hline=$(head -n1 "$table")

if [[ "$hline" =~ [^[:alnum:]\._\t ] ]]; then
    echo "Invalid character in column of TABLE! Allowed: "\
         "alphanumeric, . and _" >&2
    exit 1
fi

echo "declare -A ${variable};"
echo "${variable}=("

i=$start
IFS=$'\t '
for field in $hline;do
    echo "[$field]=$i"
    i=(( i+1 ))
done
echo ")"







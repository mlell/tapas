#!/bin/bash
set -ue

function usage(){
    echo "Usage: some_program < myfile | write_later myfile"
    echo ""
    echo "Read from standard input and write it into a temporary file."
    echo "If all input is read, write the file to its permanent destination."
    echo "This is to enable programs to write into their own input file "
    echo ""
    echo "This program is meant to be used as the final section of a pipe, "
    echo "as shown above. 'myfile' is used as input file by some program"
    echo "upstream of the pipe (not nessecarily by using the '<' operator"
    echo "like in the usage example above). The data this program receives"
    echo "from the pipe will be written into the specified file, which can"
    echo "be the same as used somewhere upstream the pipe (that's the whole"
    echo "purpose)."
    echo ""
}

# Show help message, if needed
if [ -z "${1-}"  -o "${1-x}" = "-h" -o "${1-x}" = "--help" ]; then
    usage
    exit 1
fi

outputfile="${1:?}"

tempfile="$(mktemp)"
trap "rm ${tempfile:?}" EXIT

# Forward all data from standard input to the temporary file
cat > "${tempfile}"

# After all input is read, move the temporary file to a permanent location
cp "${tempfile}" "${outputfile}"




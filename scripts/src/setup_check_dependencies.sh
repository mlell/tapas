#!/bin/bash
set -ue -o pipefail

# This script checks if each dependency is met and outputs the result.
# Call without further arguments.


thisFolder="$(dirname "$(readlink -f "$0")")"

libFolder="$(readlink -f "$thisFolder/../lib")"

python_deps=(pandas docopt numpy scipy)
r_deps=(stringr magrittr ggplot2 docopt dplyr gridExtra)

# Generate a temporary output file to filter for installation instructions
tmpf=$(mktemp)
trap "rm $tmpf" EXIT

msgprefix="#>"

rfail=0
echo "R dependencies:"
$thisFolder/../setup_r_check_dependencies ${r_deps[@]} |\
    tee "$tmpf" |grep -v "$msgprefix" || rfail=1

echo "--------------------------------------------------------------------"
echo ""

pyfail=0
echo "Python dependencies:"
$thisFolder/../setup_py_check_dependencies ${python_deps[@]} |\
    tee -a "$tmpf" | grep -v "$msgprefix" || pyfail=1

echo "--------------------------------------------------------------------"
echo ""

if [[ $rfail != 0 ]]; then
    echo "## Not all R dependencies are satisfied!"
else
    echo "All R dependencies are satisfied."
fi

if [[ $pyfail != 0 ]]; then
    echo "## Not all Python dependencies are satisfied!"
else
    echo "All Python dependencies are satisfied."
fi

grep "^#>" "$tmpf" | cut -c3-

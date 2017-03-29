#!/bin/bash
set -ue -o pipefail

# This script checks if each dependency is met and outputs the result.
# Call without further arguments.


thisFolder="$(dirname "$(readlink -f "$0")")"

libFolder="$(readlink -f "$thisFolder/../lib")"

python_deps=(pandas docopt numpy scipy)
r_deps=(stringr magrittr ggplot2 docopt dplyr gridExtra)


rfail=0
echo "R dependencies:"
$thisFolder/../setup_r_check_dependencies ${r_deps[@]}  || rfail=1

echo "--------------------------------------------------------------------"
echo ""

pyfail=0
echo "Python dependencies:"
$thisFolder/../setup_py_check_dependencies ${python_deps[@]} || pyfail=1

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

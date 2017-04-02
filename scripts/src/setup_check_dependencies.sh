#!/bin/bash
set -ue -o pipefail

# This script checks if each dependency is met and outputs the result.
# Call without further arguments.


thisFolder="$(dirname "$(readlink -f "$0")")"

libFolder="$(readlink -f "$thisFolder/../lib")"

echo "$thisFolder/../lib"
echo "$libFolder"


$thisFolder/../setup_r_check_dependencies stringr magrittr dplyr ggplot2


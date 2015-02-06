#/bin/bash

export pr="$(pwd)"

export PYTHONPATH="$pr/lib/python/site-packages"
export R_LIBS="$pr/lib/R:$R_LIBS"

echo "Shell set up for mapper evaluation."
echo "R version: $(R --version | head -n1)"
pyVer=$(python -c '
import sys
print(sys.version_info[0])')
echo "Python version: $pyVer"
echo

if [ "$pyVer" != "3" ]; then
    cat >&2 <<EOF
Python 3 is required but not accessible! Install Python 3 or if it is
already installed, make sure that the \`python\` executable is linked
to a python3 installation!
EOF
fi




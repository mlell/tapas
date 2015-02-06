#!/bin/bash
set -ue

if [ -z ${pr-} ]; then
    echo "\$pr not set!"
    exit 1
fi
if [[  ${1-} == "-h"  ||  -z ${1-}  ]];then
    echo 'Usage: py-switch.sh {2 | 3}'
    exit 0
fi
version=$1

symlink_or_fail(){
    r=0
    test -h $1 || r=1
    if [ $r -ne 0 ];then
        echo "$1 is no symlink!"
        exit 1
    fi
}

symlink_or_fail $pr/bin/python
symlink_or_fail $pr/lib/python

case $version in
2)
    ln -svf ~/.bin/python2     $pr/bin/python
    ln -svfT python2.7 $pr/lib/python
    ;;
3)  ln -svf ~/.bin/python3     $pr/bin/python
    ln -svfT python3.4 $pr/lib/python
    ;;
*)  echo "Invalid version: $version!"
    ;;
esac

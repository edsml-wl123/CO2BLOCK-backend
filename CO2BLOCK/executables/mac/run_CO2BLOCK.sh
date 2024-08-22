#!/bin/sh
# script for execution of deployed applications
#
# Simplified script to run MATLAB compiled application
#

exe_name=$0
exe_dir=`dirname "$0"`
echo "------------------------------------------"

args=""
while [ $# -gt 0 ]; do
    token=$1
    args="${args} \"${token}\""
    shift
done

eval "\"${exe_dir}/CO2BLOCK.app/Contents/MacOS/CO2BLOCK\"" $args
exit

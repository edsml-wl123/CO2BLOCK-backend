#!/bin/sh
# script for execution of deployed applications
#
# Sets up the MATLAB Runtime environment for the current $ARCH and executes 
# the specified command.
#
exe_name=$0
exe_dir=`dirname "$0"`
echo "------------------------------------------"
if [ "x$1" = "x" ]; then
  echo Usage:
  echo    $0 \<deployedMCRroot\> args
else
  echo Setting up environment variables
  MCRROOT="/home/ec2-user/R2024a"
  echo ---
  LD_LIBRARY_PATH=.:$MCRROOT/runtime/glnxa64;
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$MCRROOT/bin/glnxa64;
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$MCRROOT/sys/os/glnxa64;
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$MCRROOT/sys/opengl/lib/glnxa64;
  export LD_LIBRARY_PATH;
  echo LD_LIBRARY_PATH is ${LD_LIBRARY_PATH};
  
  # Preload glibc_shim in case of RHEL7 variants
  test -e /usr/bin/ldd &&  ldd --version |  grep -q "(GNU libc) 2\.17"  \
            && export LD_PRELOAD="$MCRROOT/bin/glnxa64/glibc-2.17_shim.so"
  
  

  echo "Arguments: $@"

  # Directly pass all arguments to the executable
  exec "$exe_dir/CO2BLOCK_linux" "$@"
fi
exit

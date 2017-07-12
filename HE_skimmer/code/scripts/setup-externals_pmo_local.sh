#!/bin/bash
#@
#@ This script sets the software packages required for the offline dampe software
#@

printf "\n>>>> Execute setup-externals_pmo_local.bash \n\n"

DAMPE_EXT=${HOME}/Soft/DAMPE_externals
wd=$(pwd)

#@@@@@@@@@@@@@@@@@@@@
echo "Setting GCC.."
GCC_PATH=${DAMPE_EXT}/gcc/4.9.3/
LIBDIR=${GCC_PATH}/lib64
#export COMPILER_PATH=${GCC_PATH}/lib64
export PATH=${GCC_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LIBDIR}:${LD_LIBRARY_PATH}
export LD_RUN_PATH=${LIBDIR}:${LD_RUN_PATH}
export CC=${GCC_PATH}/bin/gcc
export CXX=${GCC_PATH}/bin/g++

#@@@@@@@@@@@@@@@@@@@@
echo "Setting CMAKE.."
export PATH=${DAMPE_EXT}/cmake/cmake-3.4.3/bin:${PATH}

#@@@@@@@@@@@@@@@@@@@@
echo "Setting xerces"
export LD_LIBRARY_PATH=${DAMPE_EXT}/xerces-c/xerces-c-3.1.2/lib:$LD_LIBRARY_PATH

#@@@@@@@@@@@@@@@@@@@@
echo "Setting python2.7.."
pypath=${DAMPE_EXT}/Python-2.7.12/build
export LD_LIBRARY_PATH=${pypath}/lib:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${pypath}/lib:${LIBRARY_PATH}
export PYTHONPATH=${pypath}/lib:${PYTHONPATH}
export PATH=${pypath}/bin:${PATH}

#@@@@@@@@@@@@@@@@@@@@
echo "Setting boost.."
cd ${DAMPE_EXT}/boost/1.55.0/include/
export CPATH=`pwd`:$CPATH
cd ${DAMPE_EXT}/boost/1.55.0/lib/
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
export LIBRARY_PATH=`pwd`:$LIBRARY_PATH

#@@@@@@@@@@@@@@@@@@@@
echo "Setting scons.."
export PATH=${DAMPE_EXT}/scons/scons-2.4.1/bin:${PATH}
export LD_LIBRARY_PATH=${DAMPE_EXT}/scons/scons-2.4.1/lib:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${DAMPE_EXT}/scons/scons-2.4.1/lib:${LIBRARY_PATH}
export PYTHONPATH=${DAMPE_EXT}/scons/scons-2.4.1/lib:${PYTHONPATH}

#@@@@@@@@@@@@@@@@@@@@
echo "Setting ROOT.."
cd ${DAMPE_EXT}/root_v5.34.34.build
source bin/thisroot.sh

#@@@@@@@@@@@@@@@@@@@@
echo "Setting Geant4.."
cd ${DAMPE_EXT}/geant4.10.02_build/share/Geant4-10.2.0/geant4make
source geant4make.sh

cd ${wd}


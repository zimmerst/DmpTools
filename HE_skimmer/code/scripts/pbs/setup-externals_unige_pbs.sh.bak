#!/bin/bash
#@
#@  This script sets the software packages required for the offline dampe software
#@

printf "\n>>>> Execute setup-externals_unige_pbs.bash \n\n"

DAMPE_EXT=/atlas/software/dampe/externals
wd=$(pwd)

#@@@@@@@@@@@@@@@@@@@@
echo "Setting GCC.."
GCC_PATH=${DAMPE_EXT}/gcc/latest
LIBDIR=${GCC_PATH}/lib64
export PATH=${GCC_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LIBDIR}:${LD_LIBRARY_PATH}
export LD_RUN_PATH=${LIBDIR}:${LD_RUN_PATH}
export CC=${GCC_PATH}/bin/gcc
export CXX=${GCC_PATH}/bin/g++
export LC_ALL=C

#@@@ adding cmake
export PATH=${DAMPE_EXT}/cmake/latest/bin:${PATH} 

#@@@@@@@@@@@@@@@@@@@@
echo "Setting python2.7.."
pypath=${DAMPE_EXT}/python2.7/latest/build
export LD_LIBRARY_PATH=${pypath}/lib:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${pypath}/lib:${LIBRARY_PATH}
export PYTHONPATH=${pypath}/lib:${PYTHONPATH}
export PATH=${pypath}/bin:${PATH}

#@@@@@@@@@@@@@@@@@@@
echo "Setting xerces"
export LD_LIBRARY_PATH=${DAMPE_EXT}/xerces-c/latest/lib:$LD_LIBRARY_PATH

#@@@@@@@@@@@@@@@@@@@@
echo "Setting boost.."
cd ${DAMPE_EXT}/boost/latest/include/
export CPATH=`pwd`:$CPATH
cd ${DAMPE_EXT}/boost/latest/lib/
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
export LIBRARY_PATH=`pwd`:$LIBRARY_PATH

#@@@@@@@@@@@@@@@@@@@@
echo "Setting scons.."
export PATH=${DAMPE_EXT}/scons/latest/bin:${PATH}
export LD_LIBRARY_PATH=${DAMPE_EXT}/scons/latest/lib:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${DAMPE_EXT}/scons/latest/lib:${LIBRARY_PATH}
export PYTHONPATH=${DAMPE_EXT}/scons/latest/lib:${PYTHONPATH}

#@@@@@@@@@@@@@@@@@@@@
echo "Setting geant4.."
cd ${DAMPE_EXT}/geant4/latest/share/Geant4-*/geant4make
source ./geant4make.sh

echo "Setting root..."
cd ${DAMPE_EXT}/root/latest
source bin/thisroot.sh

cd $wd

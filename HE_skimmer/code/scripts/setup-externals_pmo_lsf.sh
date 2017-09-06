#!/bin/bash
#@
#@ This script sets the software packages required for the offline dampe software
#@

printf "\n>>>> Execute setup-externals_pmo_lsf.bash \n\n"

wd=$(pwd)

export LD_RUN_PATH=/usr/lib64:${LD_RUN_PATH}
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH=/usr/lib64:${LD_LIBRARY_PATH}

export LIBRARY_PATH=/usr/lib:${LIBRARY_PATH}

export PYTHONPATH=/usr/lib:${PYTHONPATH}

export PATH=/usr/local/bin:${PATH}
export PATH=/usr/bin:${PATH}


#@@@@@@@@@@@@@@@@@@@@
echo "Setting ROOT.."
cd /data/software/root
source bin/thisroot.sh

#@@@@@@@@@@@@@@@@@@@@
echo "Setting Geant4.."
cd /data/software/GEANT4/geant4.10.01.p02-install/share/Geant4-10.1.2/geant4make
source geant4make.sh

cd ${wd}


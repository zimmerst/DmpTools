#!/bin/bash
#@
#@  This script sets the software packages required for the offline dampe software
#@
# adding the standard paths.
# first add EMI x509 certificate
setProxy(){
    #source /cvmfs/grid.cern.ch/etc/profile.d/setup-cvmfs-ui.sh
    # load older version
    #source /atlas/software/dampe/setup/setup-cvmfs-ui.sh
    source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup-cvmfs-ui.sh
    export HOME=/atlas/users/${USER}
    export X509_USER_CERT=${HOME}/.globus/usercert.pem
    export X509_USER_KEY=${HOME}/.globus/userkey.pem
    grid-proxy-info -e
    RC=$?
    if [[ $RC != 0 ]]; then
        echo "can't find valid proxy, renewing for 24 hrs"
        cat ${HOME}/.globus/.password | grid-proxy-init -valid 24:00 -pwstdin
    else
        echo "proxy OK"
    fi
}

#setProxy
source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup-cvmfs-ui.sh

export PATH=/cvmfs/dampe.cern.ch/bin:${PATH}
export LD_LIBRARY_PATH=/cvmfs/dampe.cern.ch/lib:${LD_LIBRARY_PATH}

DAMPE_EXT=/cvmfs/dampe.cern.ch/rhel6-64/opt/externals
export RELEASE_DIR=/cvmfs/dampe.cern.ch/rhel6-64/opt/releases
wd=$(pwd)

#@@@@@@@@@@@@@@@@@@@@
#echo "Setting GCC.."
GCC_PATH=${DAMPE_EXT}/gcc/4.9.3/
LIBDIR=${GCC_PATH}/lib64
export PATH=${GCC_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LIBDIR}:${LD_LIBRARY_PATH}
export LD_RUN_PATH=${LIBDIR}:${LD_RUN_PATH}
export CC=${GCC_PATH}/bin/gcc
export CXX=${GCC_PATH}/bin/g++
export LC_ALL=C

#echo "adding xrootd"
xrp=${DAMPE_EXT}/xrootd/latest/
export PATH=${xrp}/bin:${PATH}
export LD_LIBRARY_PATH=${xrp}/lib:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH=${xrp}/lib64:${LD_LIBRARY_PATH}
export XRD_LIBDIR=${xrp}/lib64
export XRD_INCDIR=${xrp}/include/xrootd

#@@@ adding cmake
export PATH=${DAMPE_EXT}/cmake/latest/bin:${PATH} 

#@@@@@@@@@@@@@@@@@@@@
#echo "Setting python2.7.."
pypath=${DAMPE_EXT}/python2.7/latest/build
export LD_LIBRARY_PATH=${pypath}/lib:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${pypath}/lib:${LIBRARY_PATH}
export PYTHONPATH=${pypath}/lib:${PYTHONPATH}
export PATH=${pypath}/bin:${PATH}

#@@@@@@@@@@@@@@@@@@@
#echo "Setting xerces"
export LD_LIBRARY_PATH=${DAMPE_EXT}/xerces-c/latest/lib:$LD_LIBRARY_PATH

#@@@@@@@@@@@@@@@@@@@@
#echo "Setting boost.."
cd ${DAMPE_EXT}/boost/latest/include/
export CPATH=`pwd`:$CPATH
cd ${DAMPE_EXT}/boost/latest/lib/
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
export LIBRARY_PATH=`pwd`:$LIBRARY_PATH
#export LD_LIBRARY_PATH=${DAMPE_EXT}/boost/lib:$LD_LIBRARY_PATH # old from Andrii!

#@@@@@@@@@@@@@@@@@@@@
#echo "Setting scons.."
export PATH=${DAMPE_EXT}/scons/latest/bin:${PATH}
export LD_LIBRARY_PATH=${DAMPE_EXT}/scons/latest/lib:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${DAMPE_EXT}/scons/latest/lib:${LIBRARY_PATH}
export PYTHONPATH=${DAMPE_EXT}/scons/latest/lib:${PYTHONPATH}

#@@@@@@@@@@@@@@@@@@@@
#echo "Setting geant4.."
cd ${DAMPE_EXT}/geant4/latest/share/Geant4-*/geant4make
source geant4make.sh

#echo "Setting root..."
source ${DAMPE_EXT}/root/latest/bin/thisroot.sh

cd $wd

dampe_init(){
    if (( $# == 0 )); then release="latest";
    else release=$1; fi
    workdir=$(pwd)
    echo "DAMPE software setup - core"
    cd ${RELEASE_DIR}/${release}
    echo "DmpBuild: $(readlink -f .)"
    source bin/thisdmpsw.sh
    cd ${workdir}
}

root6(){
    wd=$(pwd)
    unset ROOTSYS
    source ${DAMPE_EXT}/root/root6/latest/bin/thisroot.sh
    cd ${wd}
}

set_virtualenv(){
    if (( $# == 0 )); then MY_PATH=${HOME};
    else MY_PATH=$1; fi
    export WORKON_HOME=${MY_PATH}/virtualEnvs/
    mkdir -p $WORKON_HOME
    source $(which virtualenvwrapper.sh)
}

#!/bin/bash
wd=$(pwd)
cv=/cvmfs/dampe.cern.ch/rhel6-64
DAMPE_EXT=${cv}/opt/externals
#echo "Setting GCC.."
GCC_PATH=${DAMPE_EXT}/gcc/4.9.3/
LIBDIR=${GCC_PATH}/lib64
export PATH=${GCC_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LIBDIR}:${LD_LIBRARY_PATH}
export LD_RUN_PATH=${LIBDIR}:${LD_RUN_PATH}
export CC=${GCC_PATH}/bin/gcc
export CXX=${GCC_PATH}/bin/g++
export LC_ALL=C

# xrootd
#echo "adding xrootd"
xrp=${DAMPE_EXT}/xrootd/latest/
export PATH=${xrp}/bin:${PATH}
export LD_LIBRARY_PATH=${xrp}/lib:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH=${xrp}/lib64:${LD_LIBRARY_PATH}
export XRD_LIBDIR=${xrp}/lib64
export XRD_INCDIR=${xrp}/include/xrootd

export LD_LIBRARY_PATH=${cv}/lib64:${LD_LIBRARY_PATH}
# PYTHON
export PATH=/atlas/software/dampe/centos7/conda/bin:${PATH}
#echo "Setting root..."
cd /atlas/software/dampe/centos7/root-5-34-36/
source bin/thisroot.sh

# setting keras environment (David)
export KERAS_BACKEND=theano

# Method to extract site
host=$(hostname)
site="UNDEF"
case $host in
     "ui03.recas.ba.infn.it") site=BARI;;
     "gridvm7.unige.ch") site=UNIGE;;
     "ui-dampe.cr.cnaf.infn.it") site=CNAF;;
    esac
export DAMPE_SITE=${site}

cd $wd
dmpevt_init(){
     wd=$(pwd)
     cd /atlas/software/dampe/centos7/DmpSoftware/Event/
     source thisdmpeventclass.sh
     cd ${wd}
}
dampe_init(){
     workdir=$(pwd)
     cd /atlas/software/dampe/centos7/Event/
     source thisdmpeventclass.sh
     cd ${workdir}
#    if (( $# == 0 )); then release="latest";
#    else release=$1; fi
#    workdir=$(pwd)
#    echo "DAMPE software setup - core"
#    cd ${RELEASE_DIR}/${release}
#    echo "DmpBuild: $(readlink -f .)"
#    source bin/thisdmpsw.sh
#    cd ${workdir}
}

#set_virtualenv(){
#    if (( $# == 0 )); then MY_PATH=${HOME};
#    else MY_PATH=$1; fi
#    export WORKON_HOME=${MY_PATH}/virtualEnvs/
#    mkdir -p $WORKON_HOME
#    source $(which virtualenvwrapper.sh)
#}

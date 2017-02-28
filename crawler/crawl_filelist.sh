#!/usr/bin/env bash
# RELIES ON $CRAWLER variable
release="latest"
infile=$1
badfiles=$2
ofile=${infile/".txt"/".json"}

source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
dampe_init ${release}

touch ${ofile}

for f in $(cat ${infile});
do
    python ${CRAWLER} ${f} -y ${ofile} 2> ${ofile/".json"/".err"}
done

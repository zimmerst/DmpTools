#!/bin/bash
wd=$(pwd)
echo "SLURM ARRAY JOB ID : ${SLURM_ARRAY_JOB_ID}"
echo "SLURM ARRAY TASK ID: ${SLURM_ARRAY_TASK_ID}"
source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
cd ${SWPATH}/bin
source thisdmpsw.sh
cd ${wd}
## EXECUTABLE BELOW ##

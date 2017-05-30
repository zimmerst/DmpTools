#!/bin/bash
wd=$(pwd)
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "HOSTNAME: $(hostname -f)"
echo "SLURM ARRAY JOB ID : ${SLURM_ARRAY_JOB_ID}"
echo "SLURM ARRAY TASK ID: ${SLURM_ARRAY_TASK_ID}"
echo "SWPATH: ${SWPATH}"
echo "SCRATCH: ${SCRATCH}"
echo "WORKDIR: ${WORKDIR}"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
cd ${SWPATH}/bin
source thisdmpsw.sh
cd ${SCRATCH}
## EXECUTABLE BELOW ##
exe="python ${DMPSWSYS}/share/TestRelease/JobOption_MC_DigiReco_Prod.py -y ${WORKDIR}/cycle_${SLURM_ARRAY_TASK_ID}.yaml"

echo ${exe}

#!/usr/bin/env bash
exec_dir=$(pwd)
source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
dampe_init DmpSoftware-5-4-0
export DAMPE_LOGLEVEL="ERROR"
cycles=0

input_folder=/home/DAMPE/zimmer/dampe_prod/output/simu
mask="v5r4p0"

while true;
do
    echo "$(date): started cycle ${cycles}"
    tmpDir=`mktemp -d`
    mkdir -p ${tmpDir}
    cd ${tmpDir}
    find ${input_folder} -type f | grep ${mask} >> input_files.txt
    for f in $(cat input_files.txt);
    do
        inf=${f}
        outf=${f/"simu"/"reco"}
        outf=${outf/"mc.root"/"reco.root"}
        if [ ! -f "${outf}" ]; then
            echo "${inf} ${outf}" >> files_to_process.txt
        fi
    done
    if [ -f files_to_process.txt ]; then
        nf=$(wc -l files_to_process.txt | awk '{print $2}')
        echo "$(date): found ${nf} files to process this cycle"
        exe="python ${DMPSWSYS}/share/TestRelease/JobOption_MC_DigiReco_Prod.py -t $(readlink -f files_to_process.txt)"
        echo ${exe}
        time ${exe}
    fi
    let cycles++
    echo "$(date): cycle complete, sleeping 60s"
    sleep 60
    cd ${exec_dir}
    rm -rf ${tmpDir}
done
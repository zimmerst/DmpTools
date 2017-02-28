#!/usr/bin/env bash
source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
dampe_init DmpSoftware-5-4-0
export DAMPE_LOGLEVEL="ERROR"
cycles=0

while true;
do
    echo "$(date): started cycle ${cycles}"
    rm -f input_files.txt files_to_process.txt
    find /home/DAMPE/zimmer/dampe_prod/output/simu -type f | grep v5r4p0 >> input_files.txt
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
        exe="python ${DMPSWSYS}/share/TestRelease/JobOption_MC_DigiReco_Prod.py -t $(readlink -f files_to_process.txt)"
        echo ${exe}
        time ${exe}
    fi
    let cycles++
    echo "$(date): cycle complete, sleeping 60s"
    sleep 60
done
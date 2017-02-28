#!/usr/bin/env bash
####N INPUT SECTION ####
nstreams=4             # number of simultaneous streams of copy operations
mask="v5r3p1"          # this will be used to grep
ncycles=10             # number of cycles to run agent

xrdprefix="grid05.unige.ch:1094"
input_dir="/dpm/unige.ch/home/mc/reco"
output_root="/DATA"
home="/atlas/users/${USER}"

#### DO NOT CHANGE LINES BELOW ####
exec_dir=$(pwd)
source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
setProxy(){
    source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup-cvmfs-ui.sh
    export HOME=${home}
    export X509_USER_CERT=${HOME}/.globus/usercert.pem
    export X509_USER_KEY=${HOME}/.globus/userkey.pem
    grid-proxy-info -e
    RC=$?
    if [[ $RC != 0 ]]; then
	echo "can't find valid proxy, renewing for 24 hrs"
	cat ${HOME}/.globus/.password | grid-proxy-init -valid 96:00 -pwstdin
    else
	echo "proxy OK"
    fi
}
# this exports my function to subprocesses.
export -f setProxy
cycle=1

while [ "$cycle" -lt "$ncycles" ];
do
    echo "$(date): starting cycle ${cycle}/${ncycles}"
    # assemble task list
    echo "$(date): getting proxy"
    setProxy

    echo "$(date): creating list of files to copy"
    tmpDir=`mktemp -d`
    mkdir -p ${tmpDir}
    cd ${tmpDir}
    touch allFiles.in allCommands.shell
    for task in $(xrdfs ${xrdprefix} ls ${input_dir} | grep ${mask});
    do
        echo "${task}..."
        xrdfs ${xrdprefix} ls ${task} >> allFiles.in
    done

    echo "$(date): assemble command streams"

    for ifile in $(cat allFiles.in);
    do
        fdir=dirname ${ifile}
        fname=basename ${ifile}
        dname=basename $(fdir) # the directory
        ofile=${output_root}/${dname}/${fname}
        if [ ! -f ${ofile} ];
        then
            echo "xrdcp root://${xrdprefix}/${ifile} ${ofile}" >> allCommands.shell
        fi
    done
    nf=$(wc -l allCommands.shell | awk '{print $1}')
    echo "$(date): splitting ${nf} files to copy in ${nstreams} parallel copy streams"
    ((lines_per_file = (nf + nstreams - 1) / nstreams))
    split --lines=${lines_per_file} allCommands.shell input_

    pids=""
    for f in $(find -name "input_*");
    do
        tmpFile=`mktemp -p ${tmpDir}`
        touch ${tmpFile}
        echo "#!/bin/bash" >> ${tmpFile}
        echo "setProxy " >> ${tmpFile}
        cat ${f} >> ${tmpFile}
        chmod u+x ${tmpFile}

        ./${tmpFile} 1>${tmpFile}.out 2>${tmpFile}.err &
        pids+="$! "
    done
    for pid in $pids; do
        wait ${pid}
        if [ $? -eq 0 ]; then
            echo "SUCCESS - chunk $pid exited with a status of $?"
        else
            echo "FAILED - chunk $pid exited with a status of $?"
        fi
    done
    echo "$(date): done with cycle, sleeping 60s"
    sleep 60
    cd ${exec_dir}
    rm -rf ${tmpDir}
done

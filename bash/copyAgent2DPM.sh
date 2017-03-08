#!/usr/bin/env bash
####N INPUT SECTION ####
nstreams=30             # number of simultaneous streams of copy operations
mask="all.*-v5r4p0_1GeV_100GeV" # this will be used for grep
ncycles=10             # number of cycles to run agent

xrdprefix="grid05.unige.ch:1094"
input_dir="/lustre/dampe/XROOTD/MC/reco/"
output_root="/dpm/unige.ch/home/dampe/mc/reco"
home="/lustrehome/dampeuser"


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
    echo "tmpDir: ${tmpDir}"
    mkdir -p ${tmpDir}
    cd ${tmpDir}
    mkdir -p ${tmpDir}/error
    mkdir -p ${tmpDir}/output
    touch allFiles.in allCommands.shell
    for task in $(ls ${input_dir} | grep ${mask});
    do
        echo "${task}..."
        find ${input_dir}/${task} -type f >> allFiles.in
	echo "try to create folder on xrootd:"
	xrdfs ${xrdprefix} mkdir -p -mrwxr-xr-x ${output_root}/${task}

    done

    echo "$(date): assemble command streams"

    for ifile in $(cat allFiles.in);
    do
        fdir=$(dirname ${ifile})
        fname=$(basename ${ifile/".mc"/".reco"})
        dname=$(basename ${fdir}) # the directory
        ofile=${output_root}/${dname}/${fname}
        #mkdir -p $(dirname ${ofile})
        if [ ! -f ${ofile} ];
        then
            echo "xrdcp ${ifile} root://${xrdprefix}/${ofile}" >> allCommands.shell
        fi
    done
    nf=$(wc -l allCommands.shell | awk '{print $1}')
    echo "$(date): splitting ${nf} files to copy in ${nstreams} parallel copy streams"
    #exit 1
    if [ "$nf" -gt 0 ];
    then
        ((lines_per_file = (nf + nstreams - 1) / nstreams))
        split --lines=${lines_per_file} allCommands.shell input_

        pids=""
        for f in $(find -name "input_*");
        do
            tmpFile=`mktemp -p ${tmpDir}`
            tmpFile=$(basename ${tmpFile})
            touch ${tmpFile}
            echo "#!/bin/bash" >> ${tmpFile}
            echo "setProxy " >> ${tmpFile}
            cat ${f} >> ${tmpFile}
            chmod u+x ${tmpFile}
            bash ${tmpFile} 1> ${tmpDir}/output/${tmpFile} 2> ${tmpDir}/error/${tmpFile} &
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
    fi
    echo "$(date): done with cycle, sleeping 60s"
    sleep 60
    cd ${exec_dir}
    rm -rf ${tmpDir}
done
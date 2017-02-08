#!/bin/bash
# this is for the Portable Batch System (PBS)
# note that shorter intervals than 2s may be detrimental and cause premature termination of the code
export PLUGIN_NAME='hpc'
export PLUGIN_TYPE='counter'

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-15}"
USERNAME="${USER:-zimmer}"

start_run=$(date +\%s)
next_run=$((start_run+INTERVAL))
time_left=$((INTERVAL))
i=0
while [ $((time_left)) -gt 0 ];
do
        tmpfile=/tmp/${EXPERIMENT}.qstat
        start_run=$(date +\%s)
        #echo ${start_run}
        next_run=$((start_run + INTERVAL))
        /bin/env qstat -u ${USERNAME} >> ${tmpfile}
        njobs=$(grep -c ${USERNAME} ${tmpfile})
        running=$(cat ${tmpfile} | awk '{print $10}' | grep -c "R")
        pending=$(cat ${tmpfile} | awk '{print $10}' | grep -c "Q")
        suspend=$(cat ${tmpfile} | awk '{print $10}' | grep -c "S")

        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_pending ${start_run}:${pending:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_running ${start_run}:${running:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_suspend ${start_run}:${suspend:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_njobs ${start_run}:${njobs:-0}"
        rm -f ${tmpfile}
        let i++
        now=$(date +\%s)
        time_left=$((next_run - now))
        #echo "${i}: ${time_left}"
        #echo "sleep for ${time_left}"
        sleep ${time_left}

done
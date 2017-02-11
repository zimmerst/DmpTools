#!/bin/bash
# this is for IBM's LSF
# note that shorter intervals than 2s may be detrimental and cause premature termination of the code
export PLUGIN_NAME='hpc'
export PLUGIN_TYPE='counter'

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-15}"
EXPERIMENT='dampe'
interval=${INTERVAL%.*}

start_run=$(date +\%s)
next_run=$((start_run+interval))
time_left=$((interval))
i=0
while [ $((time_left)) -gt 0 ];
do
        tmpfile=/tmp/${EXPERIMENT}.bqueues
        start_run=$(date +\%s)
        #echo ${start_run}
        next_run=$((start_run + interval))

        /bin/env bqueues ${EXPERIMENT} > ${tmpfile}
        njobs=$(tail -n 1 ${tmpfile} | awk '{print $8}')
        pending=$(tail -n 1 ${tmpfile} | awk '{print $9}')
        running=$(tail -n 1 ${tmpfile} | awk '{print $10}')
        suspend=$(tail -n 1 ${tmpfile} | awk '{print $11}')

        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-lsf_pending ${start_run}:${pending:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-lsf_running ${start_run}:${running:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-lsf_suspend ${start_run}:${suspend:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-lsf_njobs ${start_run}:${njobs:-0}"
        rm -f ${tmpfile}
        let i++
        now=$(date +\%s)
        time_left=$((next_run - now))
        #echo "${i}: ${time_left}"
        #echo "sleep for ${time_left}"
        sleep ${time_left}

done